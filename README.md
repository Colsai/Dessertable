# Dessertable

A Python web application that helps you find dessert restaurants near your location (by zip code) with links to their websites, popular menu items, and detailed filtering options.

## Features

- **Search by Zip Code**: Find restaurants near any US zip code
- **Filter by Cuisine**: Choose from 15+ cuisine types (Italian, Chinese, Mexican, etc.)
- **Filter by Price Range**: Select restaurants by price level ($, $$, $$$, $$$$)
- **Sort Results**: Sort by highest rating, closest distance, or newest restaurants
- **Restaurant Details**: View ratings, addresses, phone numbers, and links to websites
- **Popular Menu Items**: Discover popular dishes mentioned in customer reviews
- **Search History**: All searches automatically saved to SQLite database
- **GUI Launcher**: Easy-to-use desktop launcher for non-technical users
- **Clean Web Interface**: Responsive Bootstrap 5 design that works on all devices

## Quick Start (Easy Method for Non-Programmers)

**This is the easiest way to use the app - no coding knowledge required!**

### Windows Users:
1. Make sure Python is installed (download from https://www.python.org/)
2. Get your Google Places API Key (see "Get API Key" section below)
3. Double-click `START_APP.bat`
4. Enter your API key in the launcher window and click "Save API Key"
5. Click "Start Server"
6. The app will automatically open in your browser!

### Mac/Linux Users:
1. Make sure Python 3 is installed
2. Get your Google Places API Key (see "Get API Key" section below)
3. Open Terminal and navigate to the project folder
4. Run: `./START_APP.sh`
5. Enter your API key in the launcher window and click "Save API Key"
6. Click "Start Server"
7. The app will automatically open in your browser!

### Using the GUI Launcher

The launcher provides:
- **Easy API Key Setup**: Enter and save your API key visually
- **One-Click Start/Stop**: Start and stop the server with buttons
- **Automatic Browser Launch**: Opens your browser automatically
- **Server Status**: See if the server is running
- **Server Logs**: View real-time logs in the window

## Technology Stack

- **Backend**: Python 3.8+, Flask
- **API**: Google Places API (Geocoding, Nearby Search, Place Details)
- **Frontend**: Bootstrap 5, Jinja2 templates
- **Libraries**: googlemaps, python-dotenv, requests

## Prerequisites

- Python 3.8 or higher
- Google Cloud account with Places API enabled
- Google Places API key

## Setup Instructions

### 1. Clone or Download the Repository

```bash
cd pick_it_whatever
```

### 2. Create a Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Get Google Places API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - Geocoding API
   - Places API
4. Go to "Credentials" and create an API key
5. (Recommended) Restrict your API key:
   - Set application restrictions (HTTP referrers for web)
   - Set API restrictions to only allow Geocoding and Places APIs

**Note**: Google offers $200 in free credit per month. Typical costs:
- Geocoding: $5 per 1,000 requests
- Places Nearby Search: $32 per 1,000 requests
- Place Details: $17 per 1,000 requests

### 5. Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and add your API key:

```
GOOGLE_PLACES_API_KEY=your_actual_api_key_here
FLASK_ENV=development
SECRET_KEY=your_secret_key_here
```

To generate a secure secret key in Python:
```python
import secrets
print(secrets.token_hex(16))
```

### 6. Run the Application

```bash
python run.py
```

The application will start at: http://localhost:5000

## Usage

### Searching for Restaurants

1. **Enter Zip Code**: Type a 5-digit US zip code (e.g., 10001, 90210, 60601)
2. **Select Filters** (Optional):
   - Choose a cuisine type from the dropdown
   - Select one or more price ranges
   - Choose how to sort results
3. **Click "Search Restaurants"**: View results with restaurant details
4. **Explore Results**: Click on restaurant names or "View on Maps" to learn more

### Viewing Search History

All your searches are automatically saved to a local SQLite database!

1. **Access History**: Click "History" in the navigation bar
2. **View Statistics**: See your total searches, restaurants found, and top cuisines
3. **Browse Past Searches**: View all your previous searches in a table
4. **Re-view Results**: Click "View Results" to see the restaurants from any past search
5. **No Internet Required**: Past searches are loaded from the local database

**Database Location**: `data/restaurants.db`

The database stores:
- All search parameters (zip code, cuisine, price range, sort method)
- Complete restaurant details from each search
- Search timestamps for tracking
- Statistics about your search patterns

## Project Structure

```
pick_it_whatever/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── routes.py                # Route handlers (with history routes)
│   ├── models/
│   │   ├── restaurant.py        # Restaurant data model
│   │   └── database.py          # SQLite database manager
│   ├── services/
│   │   ├── places_api.py        # Google Places API wrapper
│   │   └── restaurant_service.py # Business logic
│   ├── utils/
│   │   └── filters.py           # Template filters
│   ├── static/
│   │   ├── css/style.css        # Custom styles
│   │   └── js/main.js           # Client-side JavaScript
│   └── templates/
│       ├── base.html            # Base template
│       ├── index.html           # Search form
│       ├── results.html         # Results display
│       └── history.html         # Search history page
├── data/
│   └── restaurants.db           # SQLite database (auto-created)
├── tests/                       # Test files
├── launcher.py                  # GUI launcher for easy startup
├── START_APP.bat                # Windows startup script
├── START_APP.sh                 # Mac/Linux startup script
├── .env.example                 # Environment variables template
├── .gitignore                   # Git ignore rules
├── config.py                    # Configuration management
├── requirements.txt             # Python dependencies
├── run.py                       # Application entry point
└── README.md                    # This file
```

## Configuration

Edit `config.py` to customize:
- `DEFAULT_SEARCH_RADIUS`: Search radius in meters (default: 5000m / ~3 miles)
- `MAX_RESULTS`: Maximum number of results to return (default: 20)
- `CACHE_TIMEOUT`: Cache timeout in seconds (default: 60)

## Development

### Running in Development Mode

The app runs in development mode by default with debug enabled and auto-reload.

### Running Tests

```bash
pytest
```

### Code Structure

- **Models** (`app/models/`): Data structures for restaurants
- **Services** (`app/services/`): Business logic and API integration
- **Routes** (`app/routes.py`): HTTP request handlers
- **Templates** (`app/templates/`): HTML templates with Jinja2
- **Static** (`app/static/`): CSS, JavaScript, and images

## Production Deployment

### Using Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

### Environment Variables for Production

```
FLASK_ENV=production
GOOGLE_PLACES_API_KEY=your_production_api_key
SECRET_KEY=your_strong_secret_key
```

### Deployment Platforms

- **Heroku**: Add `Procfile` with `web: gunicorn run:app`
- **Google Cloud Run**: Deploy as a containerized application
- **AWS Elastic Beanstalk**: Deploy Python application directly

## Troubleshooting

### "API key is not configured" Error
- Make sure `.env` file exists with `GOOGLE_PLACES_API_KEY`
- Verify the API key is correct and has no extra spaces
- Ensure Geocoding and Places APIs are enabled in Google Cloud Console

### "Could not find location for zip code" Error
- Verify you entered a valid US zip code
- Check that Geocoding API is enabled
- Ensure you have API quota remaining

### No Menu Items Displayed
- Menu items are extracted from reviews, which may not always be available
- Some restaurants may have limited review data
- This is normal and not an error

### Slow Search Results
- First search after app start may be slower (no cache)
- Complex searches fetch details for up to 20 restaurants
- Enable caching to speed up repeated searches

## API Rate Limiting and Costs

The app implements caching to minimize API calls:
- Geocoding results cached for 60 seconds
- Restaurant search results cached for 60 seconds
- Place details cached for 60 seconds

**Estimated costs per search**:
- With cache: ~$0.054 (1 geocode + 1 nearby search + up to 20 details)
- Without cache: Same as above
- 1,000 searches ≈ $54

## Future Enhancements

- User authentication and saved favorites
- Map view of results
- More advanced menu item extraction (NLP)
- Restaurant comparison feature
- Email notifications for new restaurants
- Support for non-US locations
- Mobile app version

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

## License

This project is open source and available under the MIT License.

## Acknowledgments

- Powered by Google Places API
- Built with Flask and Bootstrap
- Icons and UI components from Bootstrap 5

## Support

For issues or questions:
1. Check the Troubleshooting section above
2. Review Google Places API documentation
3. Open an issue in the repository
