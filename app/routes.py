from flask import Blueprint, render_template, request, flash, current_app
import re
from datetime import datetime

from app.services.places_api import PlacesAPI, PlacesAPIError
from app.services.restaurant_service import RestaurantService
from app.models.database import Database

main_bp = Blueprint('main', __name__)

# Initialize database
db = Database()


@main_bp.route('/')
def index():
    """Render the search form"""
    return render_template('index.html')


@main_bp.route('/search', methods=['POST'])
def search():
    """Process restaurant search request"""
    # Get form data
    address = request.form.get('address', '').strip()

    # Validate address
    if not address or len(address) < 5:
        flash('Please enter a valid address', 'error')
        return render_template('index.html')

    # Use defaults for simplified search - limited to desserts only
    cuisine = 'dessert ice cream bakery cake pie'
    price_range = None
    sort_by = 'rating'

    try:
        # Initialize API and service
        api_key = current_app.config.get('GOOGLE_PLACES_API_KEY')
        if not api_key:
            flash('Google Places API key is not configured. Please set GOOGLE_PLACES_API_KEY in .env file', 'error')
            return render_template('index.html')

        places_api = PlacesAPI(api_key)
        restaurant_service = RestaurantService(places_api)

        # Search for restaurants
        radius = current_app.config.get('DEFAULT_SEARCH_RADIUS', 5000)
        restaurants = restaurant_service.find_restaurants(
            location=address,
            cuisine=cuisine,
            price_range=price_range,
            sort_by=sort_by,
            radius=radius
        )

        # Save search to database
        try:
            db.save_search(
                location=address,
                cuisine=cuisine,
                price_range=price_range,
                sort_by=sort_by,
                restaurants=restaurants
            )
        except Exception as e:
            print(f"Warning: Failed to save search to database: {e}")

        # Limit to top 3 results for display
        total_found = len(restaurants)
        top_restaurants = restaurants[:3]

        # Prepare search parameters for display (minimal for zen design)
        search_params = {
            'address': address
        }

        return render_template(
            'results.html',
            restaurants=top_restaurants,
            search_params=search_params,
            count=len(top_restaurants),
            total_found=total_found,
            now=datetime.now()
        )

    except PlacesAPIError as e:
        flash(f'Search error: {str(e)}', 'error')
        return render_template('index.html')
    except Exception as e:
        flash(f'An unexpected error occurred: {str(e)}', 'error')
        return render_template('index.html')


@main_bp.route('/history')
def history():
    """Display search history"""
    try:
        searches = db.get_search_history(limit=50)
        stats = db.get_stats()

        return render_template(
            'history.html',
            searches=searches,
            stats=stats
        )
    except Exception as e:
        flash(f'Error loading history: {str(e)}', 'error')
        return render_template('index.html')


@main_bp.route('/history/<int:search_id>')
def view_search(search_id):
    """View results from a previous search"""
    try:
        searches = db.get_search_history(limit=1000)
        search_info = None
        for s in searches:
            if s['id'] == search_id:
                search_info = s
                break

        if not search_info:
            flash('Search not found', 'error')
            return render_template('index.html')

        restaurants_data = db.get_search_results(search_id)

        # Convert dict to Restaurant-like objects for template compatibility
        from app.models.restaurant import Restaurant

        restaurants = []
        for r in restaurants_data:
            restaurant = Restaurant(
                place_id=r['place_id'],
                name=r['name'],
                address=r['address'],
                rating=r['rating'],
                price_level=r['price_level'],
                cuisine_type=r['cuisine_type'],
                distance=r['distance'],
                url=r['url'],
                phone=r['phone'],
                menu_items=r['menu_items'],
                lat=r['lat'],
                lng=r['lng']
            )
            restaurants.append(restaurant)

        # Limit to top 3 results for display
        total_found = len(restaurants)
        top_restaurants = restaurants[:3]

        # Prepare search parameters for display
        search_params = {
            'location': search_info.get('location', 'Unknown'),
            'cuisine': search_info['cuisine'] if search_info['cuisine'] else 'Any',
            'price_range': search_info['price_range'] if search_info['price_range'] else 'Any',
            'sort_by': search_info['sort_by'].title() if search_info['sort_by'] else 'Rating',
            'search_date': search_info['search_date']
        }

        return render_template(
            'results.html',
            restaurants=top_restaurants,
            search_params=search_params,
            count=len(top_restaurants),
            total_found=total_found,
            from_history=True,
            now=datetime.now()
        )

    except Exception as e:
        flash(f'Error loading search: {str(e)}', 'error')
        return render_template('index.html')
