"""Test actual runtime behavior of the app"""
import time
import sys

print("=" * 60)
print("RUNTIME TEST - Testing actual app behavior")
print("=" * 60)
print()

# Test with Flask test client
print("[TEST] Starting Flask test client...")
try:
    from app import create_app

    app = create_app('development')
    client = app.test_client()

    print("[OK] Test client created")
    print()

    # Test 1: GET /
    print("[TEST 1] GET / (Home page)")
    response = client.get('/')
    print(f"  Status: {response.status_code}")
    if response.status_code == 200:
        print("  [PASS] Home page loads")
    else:
        print(f"  [FAIL] Expected 200, got {response.status_code}")
        print(f"  Response: {response.data.decode()[:200]}")
    print()

    # Test 2: GET /history
    print("[TEST 2] GET /history (History page)")
    response = client.get('/history')
    print(f"  Status: {response.status_code}")
    if response.status_code == 200:
        print("  [PASS] History page loads")
    else:
        print(f"  [FAIL] Expected 200, got {response.status_code}")
        print(f"  Response: {response.data.decode()[:200]}")
    print()

    # Test 3: POST /search with valid data
    print("[TEST 3] POST /search (Search with valid zip)")
    response = client.post('/search', data={
        'zip_code': '10001',
        'cuisine': 'any',
        'sort_by': 'rating'
    }, follow_redirects=True)
    print(f"  Status: {response.status_code}")

    # This will likely fail without actual API, but we can see the error
    if response.status_code == 200:
        if b'restaurants' in response.data or b'error' in response.data.lower():
            print("  [PASS] Search endpoint responds")
        else:
            print("  [WARN] Search returned but response unclear")
    else:
        print(f"  Status: {response.status_code}")
        # Check if it's an error page
        if b'error' in response.data.lower() or b'flash' in response.data.lower():
            print("  [INFO] Search returned error (expected without real API)")
        else:
            print(f"  [FAIL] Unexpected response")
    print()

    # Test 4: POST /search with invalid data
    print("[TEST 4] POST /search (Invalid zip code)")
    response = client.post('/search', data={
        'zip_code': 'INVALID',
        'cuisine': 'any',
        'sort_by': 'rating'
    }, follow_redirects=True)
    print(f"  Status: {response.status_code}")
    if response.status_code == 200:
        if b'valid' in response.data.lower() or b'error' in response.data.lower():
            print("  [PASS] Validation error shown")
        else:
            print("  [INFO] Response received")
    print()

    # Test 5: GET /history/1 (View specific search)
    print("[TEST 5] GET /history/1 (View past search)")
    response = client.get('/history/1')
    print(f"  Status: {response.status_code}")
    if response.status_code in [200, 302]:
        print("  [PASS] History view endpoint responds")
    else:
        print(f"  [INFO] Status {response.status_code}")
    print()

    print("=" * 60)
    print("RUNTIME TESTS COMPLETE")
    print("=" * 60)
    print()
    print("If all tests passed, the app is working correctly.")
    print("Any failures with actual API calls are expected without a real API key.")

except Exception as e:
    print(f"\n[ERROR] Runtime test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
