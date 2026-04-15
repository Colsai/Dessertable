import googlemaps
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import time


class PlacesAPIError(Exception):
    """Custom exception for Places API errors"""
    pass


class PlacesAPI:
    """Google Places API wrapper"""

    def __init__(self, api_key: str, cache_timeout: int = 60):
        if not api_key:
            raise PlacesAPIError("Google Places API key is required")

        try:
            self.client = googlemaps.Client(key=api_key)
        except Exception as e:
            raise PlacesAPIError(f"Failed to initialize Google Maps client: {str(e)}")

        # Simple cache: {cache_key: (data, timestamp)}
        self._cache = {}
        self._cache_timeout = cache_timeout

    def _get_from_cache(self, cache_key: str) -> Optional[any]:
        """Get data from cache if not expired"""
        if cache_key in self._cache:
            data, timestamp = self._cache[cache_key]
            if datetime.now() - timestamp < timedelta(seconds=self._cache_timeout):
                return data
            else:
                del self._cache[cache_key]
        return None

    def _add_to_cache(self, cache_key: str, data: any):
        """Add data to cache with current timestamp"""
        self._cache[cache_key] = (data, datetime.now())

    def geocode_address(self, address: str) -> Tuple[float, float]:
        """
        Convert street address to latitude/longitude coordinates

        Args:
            address: Full street address (e.g., "123 Main St, New York, NY")

        Returns:
            Tuple of (latitude, longitude)

        Raises:
            PlacesAPIError: If geocoding fails
        """
        cache_key = f"geocode_{address}"
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached

        try:
            results = self.client.geocode(address)
            if not results:
                raise PlacesAPIError(f"Could not find location for address: {address}")

            location = results[0]['geometry']['location']
            coords = (location['lat'], location['lng'])

            self._add_to_cache(cache_key, coords)
            return coords

        except googlemaps.exceptions.ApiError as e:
            raise PlacesAPIError(f"Geocoding API error: {str(e)}")
        except Exception as e:
            raise PlacesAPIError(f"Geocoding failed: {str(e)}")

    def search_restaurants(
        self,
        lat: float,
        lng: float,
        radius: int = 5000,
        cuisine: Optional[str] = None
    ) -> List[Dict]:
        """
        Search for restaurants near a location

        Args:
            lat: Latitude
            lng: Longitude
            radius: Search radius in meters (default 5000)
            cuisine: Optional cuisine type keyword

        Returns:
            List of restaurant dictionaries from Places API

        Raises:
            PlacesAPIError: If search fails
        """
        cache_key = f"search_{lat}_{lng}_{radius}_{cuisine}"
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached

        try:
            # Build search parameters
            location = (lat, lng)
            keyword = cuisine if cuisine else None

            # Nearby search for restaurants
            results = self.client.places_nearby(
                location=location,
                radius=radius,
                type='restaurant',
                keyword=keyword
            )

            restaurants = results.get('results', [])

            # Handle pagination if there are more results
            # Note: Google limits to 60 results total (3 pages of 20)
            while 'next_page_token' in results and len(restaurants) < 60:
                # Need to wait a bit before requesting next page
                time.sleep(2)
                try:
                    results = self.client.places_nearby(
                        page_token=results['next_page_token']
                    )
                    restaurants.extend(results.get('results', []))
                except Exception:
                    # If pagination fails, just return what we have
                    break

            self._add_to_cache(cache_key, restaurants)
            return restaurants

        except googlemaps.exceptions.ApiError as e:
            raise PlacesAPIError(f"Places search API error: {str(e)}")
        except Exception as e:
            raise PlacesAPIError(f"Restaurant search failed: {str(e)}")

    def get_place_details(self, place_id: str) -> Dict:
        """
        Get detailed information about a place

        Args:
            place_id: Google Places ID

        Returns:
            Dictionary with place details

        Raises:
            PlacesAPIError: If request fails
        """
        cache_key = f"details_{place_id}"
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached

        try:
            # Request specific fields to minimize API costs
            fields = [
                'place_id',
                'name',
                'formatted_address',
                'geometry',
                'rating',
                'user_ratings_total',
                'price_level',
                'website',
                'formatted_phone_number',
                'reviews',
                'type',
                'opening_hours'
            ]

            result = self.client.place(
                place_id=place_id,
                fields=fields
            )

            details = result.get('result', {})
            self._add_to_cache(cache_key, details)
            return details

        except googlemaps.exceptions.ApiError as e:
            raise PlacesAPIError(f"Place details API error: {str(e)}")
        except Exception as e:
            raise PlacesAPIError(f"Failed to get place details: {str(e)}")

    def calculate_distance(
        self,
        origin_lat: float,
        origin_lng: float,
        dest_lat: float,
        dest_lng: float
    ) -> float:
        """
        Calculate distance between two points using Haversine formula

        Args:
            origin_lat: Origin latitude
            origin_lng: Origin longitude
            dest_lat: Destination latitude
            dest_lng: Destination longitude

        Returns:
            Distance in meters
        """
        from math import radians, sin, cos, sqrt, atan2

        R = 6371000  # Earth's radius in meters

        lat1, lon1 = radians(origin_lat), radians(origin_lng)
        lat2, lon2 = radians(dest_lat), radians(dest_lng)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        distance = R * c
        return distance
