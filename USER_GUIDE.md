# Restaurant Finder - User Guide

## Table of Contents
1. [Getting Started](#getting-started)
2. [Using the Application](#using-the-application)
3. [Features Explained](#features-explained)
4. [Search History](#search-history)
5. [Tips & Best Practices](#tips--best-practices)
6. [Troubleshooting](#troubleshooting)

---

## Getting Started

### First Time Setup

1. **Install Python**
   - Download Python 3.8 or higher from https://python.org
   - During installation, check "Add Python to PATH"

2. **Get Your Google Places API Key**
   - Go to https://console.cloud.google.com/
   - Create a new project or select an existing one
   - Enable these APIs:
     - Geocoding API
     - Places API
   - Go to "Credentials" and create an API key
   - Copy your API key

3. **Configure the API Key**
   - Open the project folder
   - Copy `.env.example` to `.env`
   - Open `.env` in a text editor
   - Replace `your_api_key_here` with your actual API key
   - Save the file

4. **Launch the Application**
   - **Windows**: Double-click `START_APP.bat`
   - **Mac/Linux**: Run `./START_APP.sh` in Terminal

---

## Using the Application

### Launching the App

**Method 1: GUI Launcher (Recommended)**
1. Double-click `START_APP.bat` (Windows) or run `./START_APP.sh` (Mac/Linux)
2. The launcher window will open
3. Click "Start Server"
4. Your browser will automatically open to http://localhost:5000

**Method 2: Command Line**
```bash
# Activate virtual environment
venv\Scripts\activate    # Windows
source venv/bin/activate # Mac/Linux

# Run the app
python run.py
```

### Searching for Restaurants

1. **Enter Your Zip Code**
   - Type a valid 5-digit US zip code
   - Example: 10001 (Manhattan), 90210 (Beverly Hills), 60601 (Chicago)

2. **Select Filters** (Optional)
   - **Cuisine Type**: Choose from 15+ options (Italian, Chinese, Mexican, etc.)
   - **Price Range**: Check one or more price levels:
     - $ - Budget
     - $$ - Moderate
     - $$$ - Expensive
     - $$$$ - Very Expensive
   - **Sort By**: Choose how to rank results:
     - Highest Rating (default)
     - Closest Distance
     - Newest Restaurants

3. **Click "Search Restaurants"**
   - The app will search for restaurants
   - Results appear in seconds

4. **View Your Top 3 Results**
   - Ranked #1, #2, #3
   - Trophy icon on #1 result

---

## Features Explained

### 1. Top 3 Results Display

**What It Does:**
- Shows only the **best 3 restaurants** based on your sort preference
- Displays total number found (e.g., "Showing Top 3 of 25 restaurants found")

**Why Top 3?**
- Reduces decision fatigue
- Focuses on the best options
- Faster browsing experience

**Ranking:**
- Each result shows a rank number (#1, #2, #3)
- #1 result has a trophy icon
- Ranking based on your selected sort method

### 2. Cuisine Filtering

**How It Works:**
- Select a cuisine from the dropdown
- App searches only for that type of restaurant
- Uses Google's restaurant categorization

**Available Cuisines:**
- American
- Italian
- Chinese
- Mexican
- Japanese
- Thai
- Indian
- French
- Greek
- Korean
- Vietnamese
- Mediterranean
- Pizza
- Seafood
- Steakhouse
- Sushi
- BBQ
- Burgers
- And more!

### 3. Price Range Filtering

**Price Levels:**
- **$** (Budget): Inexpensive, casual dining
- **$$** (Moderate): Mid-range prices
- **$$$** (Expensive): Upscale dining
- **$$$$** (Very Expensive): Fine dining, luxury

**Multi-Select:**
- Check multiple boxes to include multiple price ranges
- Example: Check both $ and $$ for budget-friendly options

**Note:** If no price range is selected, all price levels are included.

### 4. Sort Methods

**Highest Rating (Default):**
- Shows restaurants with best customer ratings first
- Perfect for finding quality restaurants
- Ratings from Google Reviews

**Closest Distance:**
- Shows nearest restaurants first
- Great when you want to minimize travel
- Distance calculated from zip code center

**Newest Restaurants:**
- Prioritizes recently opened establishments
- Discover new spots in your area
- Based on opening date data when available

### 5. Restaurant Details

Each result shows:
- **Name**: Click to view on Google Maps or visit website
- **Rating**: Star display with numeric rating
- **Price Level**: Dollar signs ($, $$, $$$, $$$$)
- **Cuisine Type**: Category (Italian, Mexican, etc.)
- **Address**: Full street address
- **Distance**: How far from searched zip code (in miles)
- **Phone**: Contact number (when available)
- **Popular Menu Items**: Top dishes mentioned in reviews

### 6. Popular Menu Items

**What It Is:**
- Automatically extracted from customer reviews
- Shows most-mentioned food items
- Displayed as colorful badges

**How It Works:**
- App analyzes Google Reviews
- Identifies frequently mentioned dishes
- Uses keyword matching and frequency analysis
- Shows top 5-10 items per restaurant

**Example:**
- "pizza", "margherita", "tiramisu", "pasta", "gelato"

**Note:** Not all restaurants will have menu items (depends on review availability)

### 7. Restaurant Links

**View on Maps:**
- Opens restaurant location in Google Maps
- Shows directions, hours, photos
- Read more reviews

**Website Button:**
- Links directly to restaurant's website
- Make reservations
- View full menu
- Check hours and contact info

**Note:** Not all restaurants have websites. If unavailable, use Google Maps link.

---

## Search History

### Accessing History

1. Click "History" in the navigation bar
2. View all your past searches

### What's Saved

**Every search automatically saves:**
- Zip code searched
- Cuisine filter used
- Price range selected
- Sort method
- Date and time of search
- All restaurant results

### History Features

**Statistics Dashboard:**
- Total searches performed
- Total restaurants found
- Top 5 cuisines searched
- Top 5 zip codes

**Search History Table:**
- Chronological list of all searches
- See search parameters at a glance
- Results count for each search

**Re-View Results:**
- Click "View Results" on any past search
- See the exact results from that search
- No internet required (loads from database)
- No API call needed (saves money!)

### Benefits of History

1. **Quick Access**: Find that great restaurant you searched for last week
2. **No Repeat API Calls**: View past results instantly
3. **Track Patterns**: See what you search for most
4. **Offline Access**: View saved searches without internet
5. **Cost Savings**: Reduces Google API usage

---

## Tips & Best Practices

### Finding Great Restaurants

1. **Start Broad**
   - First search: No filters, sort by "Highest Rating"
   - See the top-rated options overall

2. **Then Narrow Down**
   - Add cuisine filter for specific cravings
   - Add price filter to match your budget
   - Try "Newest" to discover new places

3. **Check Multiple Zip Codes**
   - Try nearby zip codes for more options
   - Example: Search both downtown and suburb zip codes

### Using Filters Effectively

**For Best Results:**
- **Cuisine + Rating**: Find best restaurants of a specific type
- **Price + Distance**: Find affordable nearby options
- **Newest + Rating**: Discover highly-rated new restaurants

**For Exploration:**
- **No filters + Newest**: See what's new in the area
- **Different cuisines**: Try a cuisine you've never had

### Interpreting Results

**High Rating (4.5+):**
- Generally excellent choice
- Consistently good reviews
- Reliable quality

**Popular Menu Items:**
- Try these first
- Most recommended by customers
- Restaurant's signature dishes

**Distance:**
- Under 1 mile: Very close, walkable
- 1-3 miles: Short drive
- 3-5 miles: Moderate drive

### Saving Money on API Calls

**Google Places API Costs:**
- Each NEW search costs ~$0.05-0.10
- History views are FREE (no API call)

**Best Practices:**
1. Use Search History to re-view past results
2. Be specific with filters to get relevant results
3. Download/screenshot results you like
4. Check history before searching again

---

## Troubleshooting

### Common Issues

**Problem: "API Key not configured"**

Solution:
1. Make sure `.env` file exists
2. Open `.env` and check API key is present
3. Restart the launcher
4. Verify API key is correct (copy-paste from Google Cloud Console)

**Problem: "No restaurants found"**

Solutions:
- Try a different zip code
- Remove some filters (especially price range)
- Check zip code is valid 5-digit US code
- Try "Any Cuisine" instead of specific type

**Problem: "Search error"**

Solutions:
- Check internet connection
- Verify API key in Google Cloud Console
- Make sure Geocoding API and Places API are enabled
- Check if you've exceeded API quota

**Problem: App won't start**

Solutions:
1. Make sure Python is installed
2. Run `venv\Scripts\activate` then `pip install -r requirements.txt`
3. Check for error messages in launcher
4. Try running `python run.py` directly

**Problem: No menu items showing**

This is normal:
- Menu items come from reviews
- Some restaurants don't have enough reviews
- Newer restaurants may not have review data yet
- Not a bug - just limited data availability

**Problem: Slow searches**

Normal behavior:
- First search is slower (no cache)
- Complex searches take 3-5 seconds
- API calls take time
- Distance calculation for many results

**Problem: Browser doesn't open**

Solution:
- Manually open browser
- Go to http://localhost:5000
- Check if server is running (green status in launcher)

### Getting Help

**Check These First:**
1. README.md - Setup instructions
2. This USER_GUIDE.md - How to use features
3. .env.example - Environment variable reference

**Still Need Help?**
- Check if your API key is valid
- Verify billing is enabled in Google Cloud
- Check API quotas haven't been exceeded
- Try with a simple search (no filters)

---

## Keyboard Shortcuts

- **Ctrl/Cmd + Click** on restaurant link: Open in new tab
- **Browser Back Button**: Return to search form
- **F5 / Ctrl+R**: Refresh page

---

## Data & Privacy

### What's Stored Locally

**In Database (data/restaurants.db):**
- Your search queries
- Restaurant results
- Search timestamps
- No personal information

**Not Stored:**
- Your location
- Personal details
- Payment information
- Google account data

### API Key Security

- Stored only in `.env` file
- Never displayed in app
- Not sent anywhere except Google APIs
- Keep your `.env` file private
- Never share your API key

### Google Places Data

- Restaurant data provided by Google
- Reviews are from Google users
- Ratings updated regularly
- Data subject to Google's privacy policy

---

## Advanced Usage

### Customizing Search Radius

Edit `config.py`:
```python
DEFAULT_SEARCH_RADIUS = 5000  # meters (about 3 miles)
```

Change to:
- 3000 for ~2 miles
- 8000 for ~5 miles
- 16000 for ~10 miles

### Viewing More Results

The app shows Top 3 by default. All results are saved to the database.

To change the display limit:
1. Edit `app/routes.py`
2. Find: `top_restaurants = restaurants[:3]`
3. Change 3 to desired number
4. Restart app

### API Cost Tracking

Monitor your usage:
1. Go to Google Cloud Console
2. Click "Billing"
3. View "Reports"
4. Filter by service (Geocoding API, Places API)

---

## Glossary

**Zip Code**: 5-digit US postal code identifying an area

**Cuisine Type**: Category of food (Italian, Chinese, etc.)

**Price Level**: Restaurant cost category ($ to $$$$)

**Rating**: Average customer rating from Google Reviews (0-5 stars)

**API**: Application Programming Interface - how the app gets data from Google

**Search History**: Database of past searches saved locally

**Menu Items**: Popular dishes extracted from customer reviews

**Distance**: Straight-line distance from zip code center to restaurant

---

## Enjoy Finding Great Restaurants!

The app is designed to make restaurant discovery fun and easy. With the retro 8-bit theme, top 3 results format, and automatic history saving, you'll spend less time searching and more time eating!

Happy dining! 🍕🍜🍔
