# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**DessertAble** is a Flask web application that finds and recommends dessert spots using Google Places API and DeepSeek AI. It features user authentication, favorites management, and an AI-powered ranking system that balances rating quality, distance, and newness.

## Core Commands

### Development
```bash
# Run the application locally
python run.py

# Or use the platform-specific scripts
# Windows: START_APP.bat
# Mac/Linux: ./START_APP.sh

# Run tests
pytest tests/

# Run specific test file
pytest tests/test_scoring_algorithm.py

# Run with verbose output
pytest -v
```

### Environment Setup
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Production Deployment
```bash
# Run with Gunicorn (production)
gunicorn --workers 4 run:app

# Generate production SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"
```

## Architecture Overview

### Application Factory Pattern
- `app/__init__.py` - Flask application factory using `create_app()`
- Configuration loaded from `config.py` based on `FLASK_ENV` environment variable
- Blueprint-based routing with single main blueprint (`main_bp`)

### Service Layer Architecture
The application uses a **service-oriented architecture** separating concerns:

1. **PlacesAPI** (`app/services/places_api.py`)
   - Wrapper around Google Maps Python client
   - Handles geocoding, nearby search, and place details
   - Built-in caching system (60-second TTL)
   - Uses Haversine formula for distance calculations

2. **DeepSeekService** (`app/services/deepseek_service.py`)
   - Generates 10-15 word AI descriptions from reviews
   - OpenAI-compatible API client pointing to DeepSeek
   - Gracefully degrades if API key not available

3. **RestaurantService** (`app/services/restaurant_service.py`)
   - Core business logic for restaurant search and ranking
   - **Progressive filter relaxation**: automatically widens search criteria if insufficient results
   - Composite scoring algorithm (see below)

### Database Layer
- SQLite database managed by `Database` class (`app/models/database.py`)
- Database location: `data/restaurants.db` (created automatically)
- Four main tables:
  - `searches` - Search history with parameters
  - `restaurants` - Cached restaurant data linked to searches
  - `users` - User accounts with password hashing
  - `favorites` - User-restaurant many-to-many with notes

### Authentication
- Flask-Login integration in `app/__init__.py`
- User model implements `UserMixin` interface
- Password hashing with werkzeug security utilities
- Session-based authentication with 7-day persistence

## Critical Algorithm: Composite Scoring

The **composite scoring algorithm** in `RestaurantService.calculate_composite_score()` is the heart of the ranking system:

**Weight Distribution:**
- **60%** - User's sort preference (rating OR distance)
- **15%** - Cuisine match bonus
- **20%** - Newness score (logarithmic decay based on review count)
- **5%** - Proximity bonus (always applied regardless of sort preference)

**Score Calculation:**
```
Total Score = Base Score (60) + Cuisine Bonus (0-15) + Newness (0-20) + Proximity (0-5)
Maximum Possible: 100 points
```

**Newness Formula:**
```
newness = max(0, 20 - (log10(review_count) * 8))
```
This creates logarithmic decay:
- 25 reviews ≈ 9 pts (newer establishments)
- 100 reviews ≈ 4 pts
- 500+ reviews ≈ 0 pts (established venues)

**Progressive Filter Relaxation:**
The search applies filters in multiple passes to guarantee at least 5 results:
1. Try: 25+ reviews, 5-mile radius
2. Try: 15+ reviews, 7-mile radius
3. Try: 10+ reviews, 10-mile radius
4. Try: 5+ reviews, 15-mile radius
5. Final: 0+ reviews, 20-mile radius

This ensures users always get results while preferring well-reviewed nearby options.

## Data Flow: Search Request

1. User submits address via `/search` POST route
2. `PlacesAPI.geocode_address()` converts address → (lat, lng)
3. `PlacesAPI.search_restaurants()` fetches nearby dessert places with pagination
4. `RestaurantService.apply_filters()` applies progressive filtering
5. `PlacesAPI.get_place_details()` enriches top 20 results with reviews, hours, etc.
6. `DeepSeekService.generate_dessert_description()` creates AI summaries from reviews
7. `RestaurantService.calculate_composite_score()` scores each restaurant
8. Results sorted by composite score descending
9. Database saves search + top 3 results
10. Template renders top 3 to user

## Key Design Decisions

### Why SQLite?
- Zero configuration for local development
- Persistent search history without external dependencies
- User data and favorites stored reliably
- **Production Note**: Consider PostgreSQL for high-concurrency deployments (see DEPLOYMENT.md)

### Why Progressive Filtering?
- Guarantees non-empty results (critical UX requirement)
- Prefers quality (high reviews, close distance) but adapts to reality
- Avoids the "no results found" problem in sparse areas

### Why Composite Scoring Instead of Simple Rating Sort?
- Pure rating sort favors established restaurants with hundreds of reviews
- Pure distance sort ignores quality entirely
- Composite approach surfaces hidden gems (new places with high ratings)
- Newness component gives newer businesses a chance to compete

### API Cost Optimization
- Caching layer in PlacesAPI (60s TTL)
- Limits detailed fetches to top 20 candidates only
- DeepSeek gracefully degrades without breaking functionality

## Environment Variables

Required in `.env` file:

```bash
# Required for core functionality
GOOGLE_PLACES_API_KEY=your_google_api_key

# Required for production
SECRET_KEY=generate_with_secrets_token_hex_32
FLASK_ENV=production

# Optional - AI descriptions
DEEPSEEK_API_KEY=your_deepseek_api_key
```

**Getting API Keys:**
- Google Places: https://console.cloud.google.com/ (enable Places API, create credentials)
- DeepSeek: https://platform.deepseek.com/

## Testing Philosophy

- **33 unit tests** for composite scoring algorithm (`tests/test_scoring_algorithm.py`)
- Tests use MockPlacesAPI to avoid real API calls
- Fixtures provide reusable restaurant objects
- `pytest.approx()` for floating-point comparisons (±10% tolerance)
- **Known quirk**: `distance=0` evaluated as falsy in Python; documented in tests

## Common Modifications

### Adding a New Filter
1. Add parameter to `RestaurantService.find_restaurants()`
2. Update `apply_filters()` method with new filter logic
3. Update route parameter extraction in `routes.py`
4. Update HTML form in templates

### Changing Scoring Weights
Modify constants in `RestaurantService.calculate_composite_score()`:
```python
# Current: 60% base, 15% cuisine, 20% newness, 5% proximity
score += (restaurant.rating / 5.0) * 60  # Adjust 60
# ... etc
```
**Important**: Update tests in `test_scoring_algorithm.py` to match new weights.

### Adding New Database Fields
1. Add column in `Database._init_database()` CREATE TABLE statements
2. Update corresponding model class (`User`, `Restaurant`)
3. Handle migration (SQLite doesn't support ALTER TABLE well; recommend recreating DB in dev)
4. Update insert/select queries in database methods

## File Structure

```
app/
  __init__.py           # Application factory, Flask-Login setup
  routes.py             # All routes (main blueprint)
  models/
    database.py         # SQLite database manager
    restaurant.py       # Restaurant data model
    user.py             # User model with authentication
  services/
    places_api.py       # Google Places API wrapper
    deepseek_service.py # DeepSeek AI integration
    restaurant_service.py # Core business logic & scoring
  utils/
    filters.py          # Jinja2 template filters
  static/               # CSS, JS, images
  templates/            # Jinja2 HTML templates

config.py              # Config classes (Dev, Prod, Test)
run.py                 # Application entry point
requirements.txt       # Python dependencies
tests/                 # Pytest test suite
data/                  # SQLite database location (auto-created)
```

## Security Considerations

- Passwords hashed with werkzeug security (PBKDF2)
- Session cookies: HttpOnly + SameSite=Lax
- SECRET_KEY required for session security (change from default in production)
- API keys loaded from environment variables (never committed)
- SQL injection prevented via parameterized queries

## Deployment

See `DEPLOYMENT.md` for comprehensive deployment guides covering:
- Render (recommended for beginners)
- Railway, Fly.io, PythonAnywhere
- AWS Elastic Beanstalk, AWS Lightsail

**Key production changes:**
- Set `FLASK_ENV=production`
- Generate secure `SECRET_KEY`
- Use Gunicorn with multiple workers
- Consider PostgreSQL for database
- Enable HTTPS (automatic on most platforms)
