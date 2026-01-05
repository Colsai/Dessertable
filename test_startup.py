"""Quick startup test to verify the app works"""
import sys

print("Testing Dessertable startup...")
print("-" * 50)

# Test 1: Import Flask
try:
    import flask
    print("[OK] Flask imported successfully")
    print(f"     Flask version: {flask.__version__}")
except ImportError as e:
    print(f"[ERROR] Flask import failed: {e}")
    sys.exit(1)

# Test 2: Import app modules
try:
    from app import create_app
    print("[OK] App modules imported successfully")
except ImportError as e:
    print(f"[ERROR] App import failed: {e}")
    sys.exit(1)

# Test 3: Create app instance
try:
    app = create_app('development')
    print("[OK] App created successfully")
except Exception as e:
    print(f"[ERROR] App creation failed: {e}")
    sys.exit(1)

# Test 4: Check routes
try:
    with app.app_context():
        from app.routes import main_bp
        rules = [rule.rule for rule in app.url_map.iter_rules() if not rule.rule.startswith('/static')]
        print("[OK] Routes registered successfully:")
        for rule in sorted(rules):
            print(f"     - {rule}")
except Exception as e:
    print(f"[ERROR] Route check failed: {e}")
    sys.exit(1)

# Test 5: Check database
try:
    from app.models.database import Database
    db = Database()
    stats = db.get_stats()
    print("[OK] Database initialized successfully")
    print(f"     Total searches: {stats['total_searches']}")
except Exception as e:
    print(f"[ERROR] Database check failed: {e}")
    sys.exit(1)

# Test 6: Check config
try:
    api_key = app.config.get('GOOGLE_PLACES_API_KEY')
    if api_key and api_key != 'your_api_key_here':
        print("[OK] API key configured")
    else:
        print("[WARNING] API key not set (app will still run but searches won't work)")
except Exception as e:
    print(f"[ERROR] Config check failed: {e}")
    sys.exit(1)

print("-" * 50)
print("[SUCCESS] All startup tests passed!")
print("\nTo start the app:")
print("  - Double-click START_APP.bat (Windows)")
print("  - Or run: python run.py")
print("  - Then visit: http://localhost:5000")
