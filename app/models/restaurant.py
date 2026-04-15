from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from datetime import datetime
import re

METERS_TO_MILES = 0.000621371


@dataclass
class Restaurant:
    """Restaurant data model"""
    place_id: str
    name: str
    address: str
    rating: Optional[float] = None
    price_level: Optional[int] = None  # 0-4 scale (0=free, 1=$, 2=$$, 3=$$$, 4=$$$$)
    cuisine_type: Optional[str] = None
    distance: Optional[float] = None  # meters from search location
    opening_date: Optional[datetime] = None
    url: Optional[str] = None
    phone: Optional[str] = None
    menu_items: List[str] = field(default_factory=list)
    lat: Optional[float] = None
    lng: Optional[float] = None
    user_review_count: Optional[int] = None  # Total number of Google reviews
    opening_hours: Optional[List[str]] = None  # Weekday text like ["Monday: 9:00 AM – 5:00 PM", ...]
    ai_description: Optional[str] = None  # AI-generated short description from DeepSeek
    long_description: Optional[str] = None  # AI-generated 2-3 sentence hover description

    @classmethod
    def from_dict(cls, d: dict) -> 'Restaurant':
        """Construct a Restaurant from a dict (e.g. database row or JSON payload)"""
        return cls(
            place_id=d['place_id'],
            name=d['name'],
            address=d.get('address'),
            rating=d.get('rating'),
            price_level=d.get('price_level'),
            cuisine_type=d.get('cuisine_type'),
            distance=d.get('distance'),
            url=d.get('url'),
            phone=d.get('phone'),
            menu_items=d.get('menu_items') or [],
            lat=d.get('lat'),
            lng=d.get('lng'),
            opening_hours=d.get('opening_hours'),
            ai_description=d.get('ai_description'),
        )

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'place_id': self.place_id,
            'name': self.name,
            'address': self.address,
            'rating': self.rating,
            'price_level': self.price_level,
            'cuisine_type': self.cuisine_type,
            'distance': self.distance,
            'opening_date': self.opening_date.isoformat() if self.opening_date else None,
            'url': self.url,
            'phone': self.phone,
            'menu_items': self.menu_items,
            'lat': self.lat,
            'lng': self.lng,
            'user_review_count': self.user_review_count,
            'opening_hours': self.opening_hours,
            'ai_description': self.ai_description,
            'long_description': self.long_description
        }

    def get_google_maps_url(self):
        """Get Google Maps URL for this restaurant"""
        if self.url:
            return self.url
        return f"https://www.google.com/maps/search/?api=1&query={self.name.replace(' ', '+')}&query_place_id={self.place_id}"

    def get_price_display(self):
        """Get price level as dollar signs"""
        if self.price_level is None:
            return "N/A"
        return "$" * self.price_level if self.price_level > 0 else "Free"

    def get_distance_display(self):
        """Get distance in readable format (miles)"""
        if self.distance is None:
            return "N/A"
        miles = self.distance * METERS_TO_MILES
        return f"{miles:.1f} mi"

    def get_distance_miles(self):
        """Get distance in miles as a float"""
        if self.distance is None:
            return None
        return self.distance * METERS_TO_MILES

    def get_driving_time_estimate(self):
        """Estimate driving time based on distance (assumes 25 mph average city speed)"""
        if self.distance is None:
            return "N/A"

        miles = self.distance * METERS_TO_MILES
        avg_speed_mph = 25  # Average city driving speed

        time_hours = miles / avg_speed_mph
        time_minutes = int(time_hours * 60)

        if time_minutes < 1:
            return "< 1 min"
        elif time_minutes == 1:
            return "1 min"
        else:
            return f"{time_minutes} min"

    def is_open_now(self) -> Optional[bool]:
        """Check if restaurant is currently open based on opening_hours"""
        try:
            if not self.opening_hours:
                return None

            from datetime import time as time_class

            now = datetime.now()
            current_day = now.strftime('%A')  # e.g., "Monday"
            current_time = now.time()

            # Find today's hours
            for hours_text in self.opening_hours:
                if not hours_text.startswith(current_day):
                    continue

                # Check if closed
                if 'Closed' in hours_text or 'closed' in hours_text:
                    return False

                # Try multiple regex patterns for different time formats
                patterns = [
                    # "9:00 AM – 5:00 PM" (en dash)
                    r'(\d{1,2}):(\d{2})\s*(AM|PM)\s*–\s*(\d{1,2}):(\d{2})\s*(AM|PM)',
                    # "9:00 AM - 5:00 PM" (hyphen)
                    r'(\d{1,2}):(\d{2})\s*(AM|PM)\s*-\s*(\d{1,2}):(\d{2})\s*(AM|PM)',
                    # "9:00AM–5:00PM" (no spaces)
                    r'(\d{1,2}):(\d{2})(AM|PM)\s*[–-]\s*(\d{1,2}):(\d{2})(AM|PM)',
                ]

                match = None
                for pattern in patterns:
                    match = re.search(pattern, hours_text)
                    if match:
                        break

                if not match:
                    return None

                # Parse opening time
                open_hour = int(match.group(1))
                open_min = int(match.group(2))
                open_period = match.group(3).upper()

                # Parse closing time
                close_hour = int(match.group(4))
                close_min = int(match.group(5))
                close_period = match.group(6).upper()

                # Convert to 24-hour format
                if open_period == 'PM' and open_hour != 12:
                    open_hour += 12
                elif open_period == 'AM' and open_hour == 12:
                    open_hour = 0

                if close_period == 'PM' and close_hour != 12:
                    close_hour += 12
                elif close_period == 'AM' and close_hour == 12:
                    close_hour = 0

                # Create time objects for comparison
                opening_time = time_class(open_hour, open_min)
                closing_time = time_class(close_hour, close_min)

                # Check if current time is within operating hours
                if closing_time < opening_time:
                    # Handles places open past midnight
                    return current_time >= opening_time or current_time <= closing_time
                else:
                    return opening_time <= current_time <= closing_time

            return None

        except Exception as e:
            # Log error but don't break the app
            print(f"Error checking if open: {e}")
            return None

    def get_current_day_index(self) -> int:
        """Get index of current day (0-6 for Mon-Sun)"""
        return datetime.now().weekday()

    def get_dessert_description(self) -> str:
        """Generate a short description of desserts available"""
        # Sentence-style descriptions by cuisine type
        cuisine_descriptions = {
            'Ice Cream': 'Creamy scoops that make every visit worthwhile.',
            'Bakery': 'Fresh pastries baked to golden perfection daily.',
            'Desserts': 'Sweet treats that leave you wanting more.',
            'Cafe': 'Cozy spot with coffee and delightful sweets.',
            'Coffee & Desserts': 'Perfect pastries paired with a great cup.',
            'Donuts': 'Fluffy donuts that are hard to resist.',
            'Cupcakes': 'Beautiful cupcakes packed with incredible flavor.',
        }

        if self.cuisine_type and self.cuisine_type in cuisine_descriptions:
            return cuisine_descriptions[self.cuisine_type]

        # Default fallback
        return 'Delicious desserts worth every single bite.'
