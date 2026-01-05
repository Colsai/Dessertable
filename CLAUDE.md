# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Flask web application that helps users find dessert restaurants near their location using the Google Places API. The app searches for dessert-focused establishments, displays top 3 results with detailed information, and maintains a SQLite database of search history.

## Development Commands

### Environment Setup
```bash
# Create and activate virtual environment (Windows)
python -m venv venv
venv\Scripts\activate

# Create and activate virtual environment (Mac/Linux)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Application
```bash
# Start development server
python run.py

# Start with GUI launcher (easier for non-technical users)
START_APP.bat        # Windows
./START_APP.sh       # Mac/Linux

# Production server (Gunicorn)
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

### Testing
```bash
# Run all tests
pytest

# Run startup verification test
python test_startup.py

# Run runtime tests
python test_runtime.py

# Run complete test suite
python test_complete.py
```

### Database Management
```bash
# Database file location: data/restaurants.db
# To reset database, delete the file and it will be recreated on next app start
```

## Architecture Overview

### Application Factory Pattern
The app uses Flask's application factory pattern (`app/__init__.py:create_app()`). Configuration is managed through environment-specific config classes in `config.py` (Development, Production, Testing).

### Three-Layer Architecture

1. **Routes Layer** (`app/routes.py`)
   - Blueprint-based routing (`main_bp`)
   - Three main routes: `/` (search form), `/search` (POST handler), `/history` (view past searches)
   - Handles request validation and response rendering

2. **Service Layer** (`app/services/`)
   - `PlacesAPI`: Google Places API wrapper with built-in caching (60s timeout)
   - `RestaurantService`: Business logic for finding, filtering, and sorting restaurants
   - Implements composite scoring algorithm for ranking (60% sort preference + 15% cuisine match + 20% newness + 5% proximity)

3. **Data Layer** (`app/models/`)
   - `Restaurant`: Dataclass model with helper methods for display formatting
   - `Database`: SQLite operations for saving/retrieving search history

### Key Design Patterns

**Caching Strategy**: `PlacesAPI` implements in-memory caching with 60-second TTL to minimize API costs. Cache keys use format: `{operation}_{params}` (e.g., `geocode_10001`, `search_{lat}_{lng}_{radius}_{cuisine}`).

**Composite Scoring Algorithm** (`app/services/restaurant_service.py:106-169`): Ranks restaurants using weighted scoring:
- 60%: User's sort preference (rating or distance)
- 15%: Cuisine type match bonus
- 20%: Newness score (logarithmic decay based on review count)
- 5%: Proximity bonus

**Database Schema**: Two tables with foreign key relationship:
- `searches`: Stores search parameters and metadata
- `restaurants`: Stores restaurant details linked to searches
- Indexes on `search_date` and `place_id` for performance

### Data Flow for Search Operation

1. User submits address via POST to `/search`
2. `PlacesAPI.geocode_address()` converts address to coordinates (cached)
3. `PlacesAPI.search_restaurants()` performs nearby search (pagination supported, max 60 results)
4. Results converted to `Restaurant` objects with distance calculation
5. `RestaurantService.apply_filters()` enforces:
   - Minimum 25 reviews
   - Maximum 5 mile radius
   - Optional price range filter
6. `PlacesAPI.get_place_details()` enriches top 20 results with:
   - Website URL and phone number
   - Menu items extracted from reviews using regex patterns
   - Opening hours
7. `RestaurantService.sort_restaurants()` applies composite scoring
8. Top 3 results displayed to user
9. All results saved to SQLite database via `Database.save_search()`

## Important Configuration

### Environment Variables (`.env` file required)
```
GOOGLE_PLACES_API_KEY=your_api_key_here
FLASK_ENV=development
SECRET_KEY=your_secret_key_here
```

### Configurable Parameters (`config.py`)
- `DEFAULT_SEARCH_RADIUS`: 5000 meters (approximately 3 miles)
- `MAX_RESULTS`: 20 restaurants (for detail fetching)
- `CACHE_TIMEOUT`: 60 seconds

### Hardcoded Filters in Routes
The `/search` route in `app/routes.py:33-35` hardcodes cuisine to dessert-only:
```python
cuisine = 'dessert ice cream bakery cake pie'
price_range = None
sort_by = 'rating'
```

## Google Places API Integration

### API Operations and Costs
- Geocoding: $5 per 1,000 requests
- Places Nearby Search: $32 per 1,000 requests
- Place Details: $17 per 1,000 requests

Per search cost: ~$0.054 (1 geocode + 1 nearby + up to 20 details)

### Required APIs to Enable
1. Geocoding API (for address-to-coordinates conversion)
2. Places API (for restaurant search and details)

### Fields Requested in Details Call
The app requests these fields in `app/services/places_api.py:160-173` to minimize costs:
- Basic: `place_id`, `name`, `formatted_address`, `geometry`
- Ratings: `rating`, `user_ratings_total`
- Contact: `website`, `formatted_phone_number`
- Extra: `reviews`, `type`, `opening_hours`, `price_level`

## Menu Item Extraction

Located in `app/services/restaurant_service.py:246-315`, this feature uses regex patterns to extract food mentions from reviews:
- Looks for quoted items: `"chocolate cake"`
- Patterns after keywords: "try the...", "order the...", "had the..."
- Filters out stop words (service, great, good, etc.)
- Returns top 10 most frequently mentioned items

## Database Operations

### Schema
```sql
searches (id, location, cuisine, price_range, sort_by, search_date, results_count)
restaurants (id, search_id, place_id, name, address, rating, price_level,
             cuisine_type, distance, url, phone, menu_items, lat, lng)
```

### Key Methods
- `Database.save_search()`: Saves search and all restaurant results in transaction
- `Database.get_search_history()`: Returns most recent searches
- `Database.get_search_results()`: Retrieves restaurants for specific search
- `Database.clear_old_data(days)`: Cleanup utility for old searches

## Template System

Uses Jinja2 templates with Bootstrap 5 for styling:
- `base.html`: Base template with navigation and flash messages
- `index.html`: Search form (single address input for zen design)
- `results.html`: Displays top 3 restaurants with detailed cards
- `history.html`: Shows search history and statistics

Custom template filters registered in `app/utils/filters.py`.

## Common Development Tasks

### Adding New Cuisine Types
Update the `cuisine_map` dictionary in `app/services/restaurant_service.py:327-357` to map Google Place types to display names.

### Modifying Search Filters
The hardcoded filters are in `app/routes.py:33-35`. To make them user-configurable, extract from `request.form` and update the search form in `app/templates/index.html`.

### Adjusting Composite Scoring Weights
Modify the percentage calculations in `RestaurantService.calculate_composite_score()` at lines 106-169 in `app/services/restaurant_service.py`.

### Changing Result Limit Display
The top 3 limit is set in `app/routes.py:71` (`top_restaurants = restaurants[:3]`). Adjust this value and corresponding display logic in templates.

## Testing Strategy

Three test files provide different verification levels:
- `test_startup.py`: Quick verification that imports work and database initializes
- `test_runtime.py`: Requires API key, tests actual Google Places API integration
- `test_complete.py`: Comprehensive test suite

When making changes to API integration or business logic, run the runtime tests to ensure functionality with real API calls.
