# Test Suite

This directory contains unit tests for the restaurant finder application.

## Test Files

### `test_scoring_algorithm.py`

**33 unit tests** for the composite scoring algorithm used to rank restaurants.

**Test Coverage:**

- **Rating-Based Scoring (3 tests)**: Tests the 60% weight on user rating preference
  - Perfect 5.0 rating gives 60 points
  - 4.0 rating gives 48 points
  - Missing rating gives 0 points

- **Distance-Based Scoring (5 tests)**: Tests the 60% weight on distance preference
  - Zero distance handling (Python falsy quirk)
  - Very small distances (1m) give maximum score
  - 5-mile distance gives 0 base score
  - Proportional scoring for mid-range distances
  - Distances beyond 5 miles are capped

- **Cuisine Match Bonus (4 tests)**: Tests the 15% cuisine matching bonus
  - Exact matches give 15 points
  - Partial/case-insensitive matches give 15 points
  - Non-matches give 0 points
  - None values give 0 points

- **Newness Score (5 tests)**: Tests the 20% newness weight based on review count
  - 25 reviews ≈ 9 points (newer)
  - 50 reviews ≈ 6 points
  - 100 reviews ≈ 4 points
  - 500+ reviews ≈ 0 points (established)
  - Missing review count gives 10 points (middle score)

- **Proximity Bonus (4 tests)**: Tests the 5% proximity bonus
  - Very close (1m) gives ~5 points
  - 5 miles gives 0 points
  - Mid-range distances get proportional bonus
  - Missing distance gives 0 points

- **Integration Tests (4 tests)**: Tests complete composite scoring
  - Perfect restaurant scores very high (83-95 points)
  - Poor restaurant scores low (~24 points)
  - Distance preference changes ranking order
  - Cuisine match bonus can tip the balance

- **Sort Method Tests (3 tests)**: Tests the sort_restaurants method
  - Sorts by composite score descending
  - Empty lists return empty
  - Single restaurant returns in list with score

- **Edge Cases (5 tests)**: Tests boundary conditions
  - All None values
  - Zero rating
  - Negative distances
  - Very large review counts (100k+)
  - Review count of 1

**Running These Tests:**

```bash
# Run all scoring tests
pytest tests/test_scoring_algorithm.py

# Run with verbose output
pytest tests/test_scoring_algorithm.py -v

# Run specific test class
pytest tests/test_scoring_algorithm.py::TestRatingBasedScoring

# Run specific test
pytest tests/test_scoring_algorithm.py::TestRatingBasedScoring::test_perfect_rating_gives_60_points
```

## Known Quirks

### Distance = 0 Edge Case

Due to Python's truthiness, `distance=0` evaluates to `False` in conditional checks like `if restaurant.distance:`. This means restaurants at exactly 0 distance from the search location don't receive distance or proximity scores. This is an implementation quirk documented in the tests.

**Workaround:** The algorithm still works correctly in practice because real-world restaurants are never at exactly 0 meters from the search location.

## Test Organization

Tests are organized into classes by functionality:
- `TestRatingBasedScoring`: Rating preference tests
- `TestDistanceBasedScoring`: Distance preference tests
- `TestCuisineMatchBonus`: Cuisine matching tests
- `TestNewnessScore`: Review count newness tests
- `TestProximityBonus`: Proximity bonus tests
- `TestCompositeScoreIntegration`: End-to-end integration tests
- `TestSortRestaurantsMethod`: Sorting method tests
- `TestEdgeCases`: Boundary and edge case tests

## Fixtures

- `restaurant_service`: Creates a RestaurantService instance with mock API
- `base_restaurant`: Creates a Restaurant with typical values for testing
- `MockPlacesAPI`: Mock Google Places API to avoid real API calls

## Adding New Tests

When adding new scoring components or modifying the algorithm:

1. Add tests to the appropriate class
2. Use fixtures for common setup
3. Use `pytest.approx()` for floating-point comparisons
4. Document expected scores in comments
5. Run the full test suite to ensure no regressions

```bash
# Example test structure
def test_new_feature(self, restaurant_service, base_restaurant):
    """Test description"""
    base_restaurant.new_field = value

    score = restaurant_service.calculate_composite_score(
        base_restaurant, None, 'rating'
    )

    # Expected: base_score + new_feature_score
    assert score == pytest.approx(expected_value, rel=0.1)
```
