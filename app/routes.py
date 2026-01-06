from flask import Blueprint, render_template, request, flash, current_app, redirect, url_for, jsonify
import re
from datetime import datetime
from flask_login import login_user, logout_user, login_required, current_user

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


# ========== AUTHENTICATION ROUTES ==========

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    # Redirect if already logged in
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Validation
        if not username or len(username) < 3:
            flash('Username must be at least 3 characters', 'error')
            return render_template('register.html')

        if not password or len(password) < 6:
            flash('Password must be at least 6 characters', 'error')
            return render_template('register.html')

        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('register.html')

        # Create user
        user_id = db.create_user(username, password)

        if user_id is None:
            flash('Username already exists', 'error')
            return render_template('register.html')

        # Log in the new user
        user = db.get_user_by_id(user_id)
        login_user(user)

        flash('Account created successfully!', 'success')
        return redirect(url_for('main.index'))

    return render_template('register.html')


@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    # Redirect if already logged in
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)

        # Validate input
        if not username or not password:
            flash('Please enter username and password', 'error')
            return render_template('login.html')

        # Authenticate user
        user = db.get_user_by_username(username)

        if user is None or not user.check_password(password):
            flash('Invalid username or password', 'error')
            return render_template('login.html')

        # Log in user
        login_user(user, remember=remember)

        # Redirect to next page or index
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        return redirect(url_for('main.index'))

    return render_template('login.html')


@main_bp.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('main.index'))


# ========== FAVORITES ROUTES ==========

@main_bp.route('/favorites')
@login_required
def favorites():
    """Display user's favorite restaurants"""
    try:
        favorites = db.get_user_favorites(current_user.id)

        # Convert to Restaurant objects for template compatibility
        from app.models.restaurant import Restaurant

        restaurants = []
        for fav in favorites:
            restaurant = Restaurant(
                place_id=fav['place_id'],
                name=fav['name'],
                address=fav['address'],
                rating=fav['rating'],
                price_level=fav['price_level'],
                cuisine_type=fav['cuisine_type'],
                distance=fav['distance'],
                url=fav['url'],
                phone=fav['phone'],
                menu_items=fav['menu_items'],
                lat=fav['lat'],
                lng=fav['lng'],
                opening_hours=fav['opening_hours'],
                ai_description=fav['ai_description']
            )
            # Attach favorite metadata
            restaurant._favorite_id = fav['id']
            restaurant._note = fav['note']
            restaurant._favorited_at = fav['favorited_at']

            restaurants.append(restaurant)

        return render_template(
            'favorites.html',
            restaurants=restaurants,
            count=len(restaurants),
            now=datetime.now()
        )

    except Exception as e:
        flash(f'Error loading favorites: {str(e)}', 'error')
        return redirect(url_for('main.index'))


@main_bp.route('/api/favorites/add', methods=['POST'])
@login_required
def add_favorite_api():
    """Add restaurant to favorites (AJAX endpoint)"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['place_id', 'name']
        if not all(field in data for field in required_fields):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400

        # Create Restaurant object from data
        from app.models.restaurant import Restaurant

        restaurant = Restaurant(
            place_id=data['place_id'],
            name=data['name'],
            address=data.get('address'),
            rating=data.get('rating'),
            price_level=data.get('price_level'),
            cuisine_type=data.get('cuisine_type'),
            distance=data.get('distance'),
            url=data.get('url'),
            phone=data.get('phone'),
            menu_items=data.get('menu_items', []),
            lat=data.get('lat'),
            lng=data.get('lng'),
            opening_hours=data.get('opening_hours'),
            ai_description=data.get('ai_description')
        )

        note = data.get('note')

        # Add to favorites
        success = db.add_favorite(current_user.id, restaurant, note)

        if success:
            return jsonify({'success': True, 'message': 'Added to favorites'})
        else:
            return jsonify({'success': False, 'error': 'Already in favorites'}), 409

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@main_bp.route('/api/favorites/remove', methods=['POST'])
@login_required
def remove_favorite_api():
    """Remove restaurant from favorites (AJAX endpoint)"""
    try:
        data = request.get_json()
        place_id = data.get('place_id')

        if not place_id:
            return jsonify({'success': False, 'error': 'Missing place_id'}), 400

        success = db.remove_favorite(current_user.id, place_id)

        if success:
            return jsonify({'success': True, 'message': 'Removed from favorites'})
        else:
            return jsonify({'success': False, 'error': 'Not found in favorites'}), 404

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@main_bp.route('/api/favorites/note', methods=['POST'])
@login_required
def update_favorite_note_api():
    """Update note for a favorite (AJAX endpoint)"""
    try:
        data = request.get_json()
        place_id = data.get('place_id')
        note = data.get('note', '')

        if not place_id:
            return jsonify({'success': False, 'error': 'Missing place_id'}), 400

        success = db.update_favorite_note(current_user.id, place_id, note)

        if success:
            return jsonify({'success': True, 'message': 'Note updated'})
        else:
            return jsonify({'success': False, 'error': 'Favorite not found'}), 404

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
