from typing import List, Optional, Dict
from datetime import datetime
import re
from collections import Counter

from app.models.restaurant import Restaurant
from app.services.places_api import PlacesAPI, PlacesAPIError
from app.services.deepseek_service import DeepSeekService


class RestaurantService:
    """Business logic for restaurant operations"""

    def __init__(self, places_api: PlacesAPI):
        self.places_api = places_api

        # Initialize DeepSeek service (optional - requires API key)
        try:
            self.deepseek_service = DeepSeekService()
        except (ValueError, Exception) as e:
            print(f"Warning: DeepSeek service not available: {e}")
            self.deepseek_service = None

    def find_restaurants(
        self,
        location: str,
        cuisine: Optional[str] = None,
        price_range: Optional[List[int]] = None,
        sort_by: str = 'rating',
        radius: int = 5000
    ) -> List[Restaurant]:
        """
        Find restaurants near a location with filtering and sorting

        Args:
            location: Full street address (e.g., "123 Main St, New York, NY")
            cuisine: Optional cuisine type filter
            price_range: Optional list of price levels to include (1-4)
            sort_by: Sort method ('rating', 'distance', 'newest')
            radius: Search radius in meters

        Returns:
            List of Restaurant objects

        Raises:
            PlacesAPIError: If API calls fail
        """
        # Geocode address to coordinates
        lat, lng = self.places_api.geocode_address(location)

        # Search for restaurants
        raw_results = self.places_api.search_restaurants(
            lat=lat,
            lng=lng,
            radius=radius,
            cuisine=cuisine
        )

        # Convert to Restaurant objects
        restaurants = []
        for place in raw_results:
            try:
                # Calculate distance
                place_lat = place['geometry']['location']['lat']
                place_lng = place['geometry']['location']['lng']
                distance = self.places_api.calculate_distance(
                    lat, lng, place_lat, place_lng
                )

                # Get basic info from search results
                restaurant = Restaurant(
                    place_id=place.get('place_id'),
                    name=place.get('name', 'Unknown'),
                    address=place.get('vicinity', 'N/A'),
                    rating=place.get('rating'),
                    price_level=place.get('price_level'),
                    distance=distance,
                    lat=place_lat,
                    lng=place_lng,
                    user_review_count=place.get('user_ratings_total')
                )

                # Try to determine cuisine type from types
                restaurant.cuisine_type = self._extract_cuisine_type(
                    place.get('types', [])
                )

                restaurants.append(restaurant)

            except Exception as e:
                # Skip restaurants that fail to parse
                print(f"Warning: Failed to parse restaurant: {e}")
                continue

        # Apply filters with progressive relaxation to ensure at least 5 results
        min_results = 5
        filter_attempts = [
            {'min_reviews': 25, 'max_distance_miles': 5.0},
            {'min_reviews': 15, 'max_distance_miles': 7.0},
            {'min_reviews': 10, 'max_distance_miles': 10.0},
            {'min_reviews': 5, 'max_distance_miles': 15.0},
            {'min_reviews': 0, 'max_distance_miles': 20.0},
        ]

        restaurants_filtered = []
        for attempt in filter_attempts:
            restaurants_filtered = self.apply_filters(
                restaurants,
                cuisine,
                price_range,
                min_reviews=attempt['min_reviews'],
                max_distance_miles=attempt['max_distance_miles']
            )
            if len(restaurants_filtered) >= min_results:
                break

        restaurants = restaurants_filtered

        # Fetch detailed info for remaining restaurants (limited to prevent excessive API calls)
        max_details = 20  # Limit detailed fetches
        for restaurant in restaurants[:max_details]:
            try:
                details = self.places_api.get_place_details(restaurant.place_id)
                self._enrich_restaurant(restaurant, details)
            except Exception as e:
                # If details fetch fails, continue with basic info
                print(f"Warning: Failed to fetch details for {restaurant.name}: {e}")
                continue

        # Sort restaurants
        restaurants = self.sort_restaurants(restaurants, sort_by, cuisine)

        return restaurants

    def calculate_composite_score(
        self,
        restaurant: Restaurant,
        selected_cuisine: Optional[str],
        sort_preference: str
    ) -> float:
        """
        Calculate composite score for restaurant ranking

        Scoring algorithm:
        - 60% weight on user's sort preference (rating or distance)
        - 15% bonus for cuisine match
        - 20% newness score (fewer reviews = newer)
        - 5% proximity bonus (closer = better)

        Args:
            restaurant: Restaurant object to score
            selected_cuisine: User's selected cuisine filter
            sort_preference: User's sort preference ('rating' or 'distance')

        Returns:
            Composite score (higher is better)
        """
        import math
        score = 0.0

        # Base score (60%) - user's sort preference
        if sort_preference == 'rating':
            # Normalize rating to 0-1 scale, then scale to 0-60
            score += (restaurant.rating / 5.0) * 60 if restaurant.rating else 0
        elif sort_preference == 'distance':
            # Convert distance to score (closer = higher score)
            # Cap at 5 miles (8046.72 meters), scale to 0-60
            if restaurant.distance:
                max_distance = 8046.72  # 5 miles in meters
                normalized = 1 - min(restaurant.distance / max_distance, 1.0)
                score += normalized * 60

        # Cuisine match bonus (15%)
        if selected_cuisine and restaurant.cuisine_type:
            # Check if cuisines match (case-insensitive)
            if selected_cuisine.lower() in restaurant.cuisine_type.lower():
                score += 15

        # Newness score (20%) - fewer reviews = newer
        if restaurant.user_review_count:
            # Logarithmic decay: fewer reviews = higher score
            # Formula: max(0, 20 - (log10(reviews) * 8))
            # 25 reviews ≈ 9 pts, 50 ≈ 6 pts, 100 ≈ 4 pts, 250 ≈ 1 pt, 500+ ≈ 0 pts
            newness_score = max(0, 20 - (math.log10(restaurant.user_review_count) * 8))
            score += newness_score
        else:
            # No review data available, give middle score
            score += 10.0

        # Proximity bonus (5%) - closer is better
        if restaurant.distance:
            # Cap at 5 miles (8046.72 meters), scale to 0-5
            max_distance = 8046.72  # 5 miles in meters
            normalized = 1 - min(restaurant.distance / max_distance, 1.0)
            proximity_score = normalized * 5
            score += proximity_score

        return score

    def apply_filters(
        self,
        restaurants: List[Restaurant],
        cuisine: Optional[str] = None,
        price_range: Optional[List[int]] = None,
        min_reviews: int = 25,
        max_distance_miles: float = 5.0
    ) -> List[Restaurant]:
        """
        Apply filters to restaurant list

        Args:
            restaurants: List of Restaurant objects
            cuisine: Cuisine type filter (already applied in search, this is secondary)
            price_range: List of acceptable price levels
            min_reviews: Minimum number of reviews required (default 25)
            max_distance_miles: Maximum distance in miles (default 5.0)

        Returns:
            Filtered list of restaurants
        """
        # Filter by minimum review count
        filtered = [
            r for r in restaurants
            if r.user_review_count is not None and r.user_review_count >= min_reviews
        ]

        # Filter by maximum distance (5 miles = 8046.72 meters)
        max_distance_meters = max_distance_miles * 1609.34
        filtered = [
            r for r in filtered
            if r.distance is not None and r.distance <= max_distance_meters
        ]

        # Filter by price range
        if price_range:
            filtered = [
                r for r in filtered
                if r.price_level is not None and r.price_level in price_range
            ]

        return filtered

    def sort_restaurants(
        self,
        restaurants: List[Restaurant],
        sort_by: str = 'rating',
        selected_cuisine: Optional[str] = None
    ) -> List[Restaurant]:
        """
        Sort restaurants using composite scoring algorithm

        Args:
            restaurants: List of Restaurant objects
            sort_by: Sort method ('rating', 'distance', 'newest')
            selected_cuisine: User's selected cuisine for score bonus

        Returns:
            Sorted list of restaurants (highest score first)
        """
        # Calculate composite score for each restaurant
        for restaurant in restaurants:
            restaurant._composite_score = self.calculate_composite_score(
                restaurant=restaurant,
                selected_cuisine=selected_cuisine,
                sort_preference=sort_by
            )

        # Sort by composite score descending (highest first)
        return sorted(
            restaurants,
            key=lambda r: getattr(r, '_composite_score', 0),
            reverse=True
        )

    def extract_menu_items(self, reviews: List[Dict]) -> List[str]:
        """
        Extract popular menu items from reviews

        Args:
            reviews: List of review dictionaries from Places API

        Returns:
            List of popular menu items (top 5-10)
        """
        if not reviews:
            return []

        # Common food-related keywords to look for
        food_keywords = []

        # Combine all review texts
        all_text = ' '.join([
            review.get('text', '') for review in reviews
        ])

        # Extract food-related phrases (simple approach)
        # Look for capitalized words that might be menu items
        words = all_text.split()

        # Find quoted items and capitalized items that might be menu items
        potential_items = []

        # Look for quoted phrases
        quoted = re.findall(r'"([^"]+)"', all_text)
        potential_items.extend(quoted)

        # Look for phrases after "the" or "try" or "order" (common in food mentions)
        food_patterns = [
            r'the ([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
            r'try (?:the )?([a-z][a-z]+(?:\s+[a-z]+)?)',
            r'order (?:the )?([a-z][a-z]+(?:\s+[a-z]+)?)',
            r'had (?:the )?([a-z][a-z]+(?:\s+[a-z]+)?)',
            r'delicious ([a-z][a-z]+(?:\s+[a-z]+)?)',
        ]

        for pattern in food_patterns:
            matches = re.findall(pattern, all_text, re.IGNORECASE)
            potential_items.extend(matches)

        # Filter out common non-food words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
            'this', 'that', 'these', 'those', 'was', 'were', 'been', 'be', 'have',
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
            'may', 'might', 'must', 'can', 'service', 'place', 'restaurant', 'food',
            'great', 'good', 'excellent', 'amazing', 'perfect', 'best', 'nice'
        }

        cleaned_items = []
        for item in potential_items:
            item = item.strip().lower()
            if item and item not in stop_words and len(item) > 2:
                cleaned_items.append(item.title())

        # Count frequency
        if not cleaned_items:
            return []

        counter = Counter(cleaned_items)
        # Return top 10 most common items
        top_items = [item for item, count in counter.most_common(10)]

        return top_items

    def _extract_cuisine_type(self, types: List[str]) -> Optional[str]:
        """
        Extract cuisine type from Google Places types

        Args:
            types: List of place types from Google

        Returns:
            Cuisine type string or None
        """
        cuisine_map = {
            'american_restaurant': 'American',
            'chinese_restaurant': 'Chinese',
            'italian_restaurant': 'Italian',
            'japanese_restaurant': 'Japanese',
            'mexican_restaurant': 'Mexican',
            'indian_restaurant': 'Indian',
            'thai_restaurant': 'Thai',
            'french_restaurant': 'French',
            'greek_restaurant': 'Greek',
            'spanish_restaurant': 'Spanish',
            'korean_restaurant': 'Korean',
            'vietnamese_restaurant': 'Vietnamese',
            'mediterranean_restaurant': 'Mediterranean',
            'middle_eastern_restaurant': 'Middle Eastern',
            'pizza_restaurant': 'Pizza',
            'seafood_restaurant': 'Seafood',
            'steak_house': 'Steakhouse',
            'sushi_restaurant': 'Sushi',
            'barbecue_restaurant': 'BBQ',
            'hamburger_restaurant': 'Burgers',
            'sandwich_shop': 'Sandwiches',
            'fast_food_restaurant': 'Fast Food',
            'bakery': 'Bakery',
            'ice_cream_shop': 'Ice Cream',
            'dessert_shop': 'Desserts',
            'cafe': 'Cafe',
            'coffee_shop': 'Coffee & Desserts',
            'donut_shop': 'Donuts',
            'cupcake_shop': 'Cupcakes',
        }

        for place_type in types:
            if place_type in cuisine_map:
                return cuisine_map[place_type]

        return 'Restaurant'

    def _enrich_restaurant(self, restaurant: Restaurant, details: Dict):
        """
        Enrich restaurant object with detailed information

        Args:
            restaurant: Restaurant object to enrich
            details: Details dictionary from Places API
        """
        # Update address if more detailed one available
        if 'formatted_address' in details:
            restaurant.address = details['formatted_address']

        # Update website
        if 'website' in details:
            restaurant.url = details['website']

        # Update phone
        if 'formatted_phone_number' in details:
            restaurant.phone = details['formatted_phone_number']

        # Update review count if not already set
        if 'user_ratings_total' in details:
            restaurant.user_review_count = details['user_ratings_total']

        # Extract menu items from reviews
        if 'reviews' in details:
            restaurant.menu_items = self.extract_menu_items(details['reviews'])

            # Generate AI description from reviews using DeepSeek
            if self.deepseek_service:
                restaurant.ai_description = self.deepseek_service.generate_dessert_description(
                    restaurant_name=restaurant.name,
                    reviews=details['reviews']
                )

        # Try to extract opening date
        # Note: Google doesn't directly provide opening date in standard API
        # We would need to use additional data sources or manual curation
        # For now, we'll leave this as None unless data is available

        # Update cuisine type if we have better info
        if 'type' in details:
            cuisine = self._extract_cuisine_type(details['type'])
            if cuisine and cuisine != 'Restaurant':
                restaurant.cuisine_type = cuisine

        # Extract opening hours
        if 'opening_hours' in details and 'weekday_text' in details['opening_hours']:
            restaurant.opening_hours = details['opening_hours']['weekday_text']
