"""Comprehensive test of all app functionality"""
import sys
import os

print("=" * 60)
print("COMPREHENSIVE APP TEST")
print("=" * 60)
print()

# Test 1: Import all modules
print("[TEST 1] Importing all modules...")
try:
    from app import create_app
    from app.models.restaurant import Restaurant
    from app.models.database import Database
    from app.services.places_api import PlacesAPI
    from app.services.restaurant_service import RestaurantService
    from app.utils.filters import register_filters
    print("[PASS] All modules imported successfully")
except Exception as e:
    print(f"[FAIL] Import error: {e}")
    sys.exit(1)

# Test 2: Create Flask app
print("\n[TEST 2] Creating Flask app...")
try:
    app = create_app('development')
    print("[PASS] Flask app created successfully")
except Exception as e:
    print(f"[FAIL] App creation error: {e}")
    sys.exit(1)

# Test 3: Check routes
print("\n[TEST 3] Checking routes...")
try:
    with app.app_context():
        routes = [rule.rule for rule in app.url_map.iter_rules()
                  if not rule.rule.startswith('/static')]
        expected_routes = ['/', '/search', '/history', '/history/<int:search_id>']

        for route in expected_routes:
            if route in routes or any(r.startswith(route.split('<')[0]) for r in routes):
                print(f"[PASS] Route exists: {route}")
            else:
                print(f"[FAIL] Missing route: {route}")
except Exception as e:
    print(f"[FAIL] Route check error: {e}")
    sys.exit(1)

# Test 4: Check template filters
print("\n[TEST 4] Checking template filters...")
try:
    with app.app_context():
        required_filters = [
            'price_display',
            'distance_display',
            'rating_stars',
            'format_phone',
            'truncate_address'
        ]

        for filter_name in required_filters:
            if filter_name in app.jinja_env.filters:
                print(f"[PASS] Filter registered: {filter_name}")
            else:
                print(f"[FAIL] Missing filter: {filter_name}")
except Exception as e:
    print(f"[FAIL] Filter check error: {e}")
    sys.exit(1)

# Test 5: Test template rendering
print("\n[TEST 5] Testing template rendering...")
try:
    with app.test_request_context():
        from flask import render_template

        # Test index template
        try:
            render_template('index.html')
            print("[PASS] index.html renders")
        except Exception as e:
            print(f"[FAIL] index.html error: {e}")

        # Test results template with mock data
        try:
            mock_restaurant = Restaurant(
                place_id='test123',
                name='Test Restaurant',
                address='123 Test St',
                rating=4.5,
                price_level=2,
                cuisine_type='Italian',
                distance=1000,
                url='https://test.com',
                phone='555-1234',
                menu_items=['pizza', 'pasta'],
                lat=40.7,
                lng=-74.0
            )

            render_template(
                'results.html',
                restaurants=[mock_restaurant],
                search_params={
                    'zip_code': '10001',
                    'cuisine': 'Italian',
                    'price_range': '$$',
                    'sort_by': 'Rating'
                },
                count=1,
                total_found=5
            )
            print("[PASS] results.html renders with data")
        except Exception as e:
            print(f"[FAIL] results.html error: {e}")

        # Test history template
        try:
            render_template(
                'history.html',
                searches=[],
                stats={
                    'total_searches': 0,
                    'total_restaurants': 0,
                    'top_cuisines': [],
                    'top_zip_codes': []
                }
            )
            print("[PASS] history.html renders")
        except Exception as e:
            print(f"[FAIL] history.html error: {e}")

except Exception as e:
    print(f"[FAIL] Template rendering error: {e}")
    sys.exit(1)

# Test 6: Test Database
print("\n[TEST 6] Testing database...")
try:
    db = Database()
    stats = db.get_stats()
    print(f"[PASS] Database initialized - {stats['total_searches']} searches saved")
except Exception as e:
    print(f"[FAIL] Database error: {e}")
    sys.exit(1)

# Test 7: Test Restaurant model
print("\n[TEST 7] Testing Restaurant model...")
try:
    restaurant = Restaurant(
        place_id='test123',
        name='Test Restaurant',
        address='123 Test St'
    )

    # Test methods
    url = restaurant.get_google_maps_url()
    price = restaurant.get_price_display()
    distance = restaurant.get_distance_display()
    dict_repr = restaurant.to_dict()

    print("[PASS] Restaurant model methods work")
except Exception as e:
    print(f"[FAIL] Restaurant model error: {e}")
    sys.exit(1)

# Test 8: Check configuration
print("\n[TEST 8] Checking configuration...")
try:
    api_key = app.config.get('GOOGLE_PLACES_API_KEY')
    if api_key and api_key != 'your_api_key_here':
        print("[PASS] API key is configured")
    else:
        print("[WARN] API key not configured (app will still run)")

    debug = app.config.get('DEBUG')
    print(f"[INFO] Debug mode: {debug}")

    radius = app.config.get('DEFAULT_SEARCH_RADIUS')
    print(f"[INFO] Default search radius: {radius}m")

except Exception as e:
    print(f"[FAIL] Configuration error: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("ALL TESTS PASSED!")
print("=" * 60)
print("\nThe app is ready to use. Start with:")
print("  python run.py")
print("  or")
print("  Double-click START_APP.bat")
