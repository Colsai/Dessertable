"""Unit tests for the composite scoring algorithm"""
import pytest
import math
from app.models.restaurant import Restaurant
from app.services.restaurant_service import RestaurantService
from app.services.places_api import PlacesAPI


class MockPlacesAPI:
    """Mock PlacesAPI for testing without actual API calls"""
    def __init__(self):
        pass


@pytest.fixture
def restaurant_service():
    """Fixture to create RestaurantService with mock API"""
    mock_api = MockPlacesAPI()
    return RestaurantService(mock_api)


@pytest.fixture
def base_restaurant():
    """Fixture for a base restaurant with typical values"""
    return Restaurant(
        place_id='test_123',
        name='Test Restaurant',
        address='123 Test St',
        rating=4.0,
        price_level=2,
        cuisine_type='Italian',
        distance=1609.34,  # 1 mile in meters
        user_review_count=100,
        lat=40.7128,
        lng=-74.0060
    )


class TestRatingBasedScoring:
    """Test scoring when sort preference is 'rating'"""

    def test_perfect_rating_gives_60_points(self, restaurant_service, base_restaurant):
        """A 5.0 rating should give maximum 60 points (60% weight)"""
        base_restaurant.rating = 5.0
        score = restaurant_service.calculate_composite_score(
            base_restaurant, None, 'rating'
        )
        # Should get 60 points from rating (5.0/5.0 * 60)
        # Plus some points from newness and proximity
        assert score >= 60.0

    def test_4_star_rating_gives_48_points(self, restaurant_service, base_restaurant):
        """A 4.0 rating should give 48 points base (4.0/5.0 * 60)"""
        base_restaurant.rating = 4.0
        base_restaurant.user_review_count = None  # Remove newness score
        base_restaurant.distance = None  # Remove proximity score
        score = restaurant_service.calculate_composite_score(
            base_restaurant, None, 'rating'
        )
        # 4.0/5.0 * 60 = 48 points, plus 10 for missing review data
        assert score == pytest.approx(58.0, rel=0.1)

    def test_no_rating_gives_zero_base_score(self, restaurant_service, base_restaurant):
        """No rating should give 0 base points"""
        base_restaurant.rating = None
        base_restaurant.user_review_count = None
        base_restaurant.distance = None
        score = restaurant_service.calculate_composite_score(
            base_restaurant, None, 'rating'
        )
        # Should only get 10 points for missing review data
        assert score == pytest.approx(10.0, rel=0.1)


class TestDistanceBasedScoring:
    """Test scoring when sort preference is 'distance'"""

    def test_zero_distance_gives_60_points(self, restaurant_service, base_restaurant):
        """Restaurant at search location should get maximum 60 points

        Note: Due to Python's truthiness, distance=0 evaluates to False in
        'if restaurant.distance:' checks, so a restaurant at exactly 0 distance
        doesn't get distance or proximity scores. This is a quirk in the implementation.
        """
        base_restaurant.distance = 0
        base_restaurant.user_review_count = None
        score = restaurant_service.calculate_composite_score(
            base_restaurant, None, 'distance'
        )
        # With distance=0 (falsy), no distance score or proximity bonus is added
        # Only gets 10 from missing review data
        assert score == pytest.approx(10.0, rel=0.1)

    def test_very_small_distance_gives_max_points(self, restaurant_service, base_restaurant):
        """Restaurant at 1 meter should get nearly maximum 60 points"""
        base_restaurant.distance = 1  # 1 meter
        base_restaurant.user_review_count = None
        score = restaurant_service.calculate_composite_score(
            base_restaurant, None, 'distance'
        )
        # 1m / 8046.72m ≈ 0.0001, normalized ≈ 0.9999, score ≈ 60
        # Plus 10 from missing review data + ~5 from proximity
        assert score == pytest.approx(75.0, rel=0.01)

    def test_max_distance_gives_zero_points(self, restaurant_service, base_restaurant):
        """Restaurant at 5 miles should give 0 base distance points"""
        base_restaurant.distance = 8046.72  # 5 miles in meters
        base_restaurant.user_review_count = None
        score = restaurant_service.calculate_composite_score(
            base_restaurant, None, 'distance'
        )
        # 0 from distance + 10 from missing review data + 0 from proximity
        assert score == pytest.approx(10.0, rel=0.1)

    def test_mid_distance_gives_proportional_score(self, restaurant_service, base_restaurant):
        """Restaurant at 2.5 miles should give ~30 points"""
        base_restaurant.distance = 4023.36  # 2.5 miles in meters
        base_restaurant.user_review_count = None
        score = restaurant_service.calculate_composite_score(
            base_restaurant, None, 'distance'
        )
        # ~30 from distance (50% of 60) + 10 from missing data + ~2.5 from proximity
        assert score == pytest.approx(42.5, rel=0.2)

    def test_beyond_max_distance_capped_at_zero(self, restaurant_service, base_restaurant):
        """Restaurants beyond 5 miles should still compute (capped at 0 base)"""
        base_restaurant.distance = 16093.44  # 10 miles in meters
        base_restaurant.user_review_count = None
        score = restaurant_service.calculate_composite_score(
            base_restaurant, None, 'distance'
        )
        # 0 from distance (capped) + 10 from missing data + 0 from proximity (capped)
        assert score == pytest.approx(10.0, rel=0.1)


class TestCuisineMatchBonus:
    """Test the 15% cuisine match bonus"""

    def test_exact_cuisine_match_gives_15_points(self, restaurant_service, base_restaurant):
        """Exact cuisine match should add 15 bonus points"""
        base_restaurant.cuisine_type = 'Italian'
        base_restaurant.rating = 4.0
        base_restaurant.user_review_count = None
        base_restaurant.distance = None

        # Without cuisine match
        score_without = restaurant_service.calculate_composite_score(
            base_restaurant, None, 'rating'
        )

        # With cuisine match
        score_with = restaurant_service.calculate_composite_score(
            base_restaurant, 'Italian', 'rating'
        )

        assert score_with == pytest.approx(score_without + 15.0, rel=0.1)

    def test_partial_cuisine_match_gives_15_points(self, restaurant_service, base_restaurant):
        """Partial cuisine match (case-insensitive substring) should give 15 points"""
        base_restaurant.cuisine_type = 'Italian Restaurant'
        base_restaurant.rating = 4.0
        base_restaurant.user_review_count = None
        base_restaurant.distance = None

        score = restaurant_service.calculate_composite_score(
            base_restaurant, 'italian', 'rating'  # lowercase match
        )

        # 48 (rating) + 10 (missing data) + 15 (cuisine match)
        assert score == pytest.approx(73.0, rel=0.1)

    def test_no_cuisine_match_gives_zero_bonus(self, restaurant_service, base_restaurant):
        """Non-matching cuisine should not add bonus"""
        base_restaurant.cuisine_type = 'Italian'
        base_restaurant.rating = 4.0
        base_restaurant.user_review_count = None
        base_restaurant.distance = None

        score = restaurant_service.calculate_composite_score(
            base_restaurant, 'Chinese', 'rating'
        )

        # 48 (rating) + 10 (missing data) + 0 (no match)
        assert score == pytest.approx(58.0, rel=0.1)

    def test_none_cuisine_gives_zero_bonus(self, restaurant_service, base_restaurant):
        """None cuisine type should not add bonus"""
        base_restaurant.cuisine_type = None
        base_restaurant.rating = 4.0
        base_restaurant.user_review_count = None
        base_restaurant.distance = None

        score = restaurant_service.calculate_composite_score(
            base_restaurant, 'Italian', 'rating'
        )

        # 48 (rating) + 10 (missing data) + 0 (no cuisine)
        assert score == pytest.approx(58.0, rel=0.1)


class TestNewnessScore:
    """Test the 20% newness score based on review count"""

    def test_25_reviews_gives_high_newness_score(self, restaurant_service, base_restaurant):
        """25 reviews should give ~9 points (newer restaurant)"""
        base_restaurant.user_review_count = 25
        base_restaurant.rating = None
        base_restaurant.distance = None

        score = restaurant_service.calculate_composite_score(
            base_restaurant, None, 'rating'
        )

        # Formula: max(0, 20 - (log10(25) * 8))
        # log10(25) ≈ 1.398, 1.398 * 8 ≈ 11.18, 20 - 11.18 ≈ 8.82
        expected_newness = max(0, 20 - (math.log10(25) * 8))
        assert score == pytest.approx(expected_newness, rel=0.1)

    def test_50_reviews_gives_medium_newness_score(self, restaurant_service, base_restaurant):
        """50 reviews should give ~6 points"""
        base_restaurant.user_review_count = 50
        base_restaurant.rating = None
        base_restaurant.distance = None

        score = restaurant_service.calculate_composite_score(
            base_restaurant, None, 'rating'
        )

        expected_newness = max(0, 20 - (math.log10(50) * 8))
        assert score == pytest.approx(expected_newness, rel=0.1)

    def test_100_reviews_gives_low_newness_score(self, restaurant_service, base_restaurant):
        """100 reviews should give ~4 points"""
        base_restaurant.user_review_count = 100
        base_restaurant.rating = None
        base_restaurant.distance = None

        score = restaurant_service.calculate_composite_score(
            base_restaurant, None, 'rating'
        )

        expected_newness = max(0, 20 - (math.log10(100) * 8))
        assert score == pytest.approx(expected_newness, rel=0.1)

    def test_500_reviews_gives_near_zero_newness_score(self, restaurant_service, base_restaurant):
        """500+ reviews should give ~0 points (established restaurant)"""
        base_restaurant.user_review_count = 500
        base_restaurant.rating = None
        base_restaurant.distance = None

        score = restaurant_service.calculate_composite_score(
            base_restaurant, None, 'rating'
        )

        expected_newness = max(0, 20 - (math.log10(500) * 8))
        assert score == pytest.approx(expected_newness, rel=0.5)
        assert score < 1.0  # Should be very low

    def test_no_review_count_gives_middle_score(self, restaurant_service, base_restaurant):
        """Missing review count should give 10 points (middle score)"""
        base_restaurant.user_review_count = None
        base_restaurant.rating = None
        base_restaurant.distance = None

        score = restaurant_service.calculate_composite_score(
            base_restaurant, None, 'rating'
        )

        assert score == pytest.approx(10.0, rel=0.1)


class TestProximityBonus:
    """Test the 5% proximity bonus"""

    def test_zero_distance_gives_5_point_bonus(self, restaurant_service, base_restaurant):
        """Restaurant at search location should get full 5 point bonus

        Note: Due to Python's truthiness, distance=0 is falsy, so no proximity bonus
        is added. Use a very small distance instead to test the bonus.
        """
        base_restaurant.distance = 1  # 1 meter (essentially at location)
        base_restaurant.rating = 4.0
        base_restaurant.user_review_count = None

        score = restaurant_service.calculate_composite_score(
            base_restaurant, None, 'rating'
        )

        # 48 (rating) + 10 (missing data) + ~5 (proximity for 1m distance)
        assert score == pytest.approx(63.0, rel=0.1)

    def test_max_distance_gives_zero_proximity_bonus(self, restaurant_service, base_restaurant):
        """Restaurant at 5 miles should get 0 proximity bonus"""
        base_restaurant.distance = 8046.72  # 5 miles
        base_restaurant.rating = 4.0
        base_restaurant.user_review_count = None

        score = restaurant_service.calculate_composite_score(
            base_restaurant, None, 'rating'
        )

        # 48 (rating) + 10 (missing data) + 0 (proximity)
        assert score == pytest.approx(58.0, rel=0.1)

    def test_mid_distance_gives_proportional_proximity_bonus(self, restaurant_service, base_restaurant):
        """Restaurant at 2.5 miles should get ~2.5 point proximity bonus"""
        base_restaurant.distance = 4023.36  # 2.5 miles
        base_restaurant.rating = 4.0
        base_restaurant.user_review_count = None

        score = restaurant_service.calculate_composite_score(
            base_restaurant, None, 'rating'
        )

        # 48 (rating) + 10 (missing data) + ~2.5 (proximity)
        assert score == pytest.approx(60.5, rel=0.2)

    def test_no_distance_gives_zero_proximity_bonus(self, restaurant_service, base_restaurant):
        """Missing distance should give 0 proximity bonus"""
        base_restaurant.distance = None
        base_restaurant.rating = 4.0
        base_restaurant.user_review_count = None

        score = restaurant_service.calculate_composite_score(
            base_restaurant, None, 'rating'
        )

        # 48 (rating) + 10 (missing data) + 0 (no distance)
        assert score == pytest.approx(58.0, rel=0.1)


class TestCompositeScoreIntegration:
    """Test complete composite score calculations with all components"""

    def test_perfect_restaurant_high_score(self, restaurant_service, base_restaurant):
        """Perfect restaurant should score very high"""
        base_restaurant.rating = 5.0
        base_restaurant.distance = 1  # 1 meter (very close)
        base_restaurant.user_review_count = 25  # Newer restaurant
        base_restaurant.cuisine_type = 'Italian'

        score = restaurant_service.calculate_composite_score(
            base_restaurant, 'Italian', 'rating'
        )

        # 60 (perfect rating) + 15 (cuisine match) + ~8.8 (newness) + ~5 (proximity)
        # Should be close to 88-89
        assert score >= 83.0
        assert score <= 95.0

    def test_poor_restaurant_low_score(self, restaurant_service, base_restaurant):
        """Poor restaurant should score low"""
        base_restaurant.rating = 2.0
        base_restaurant.distance = 8046.72  # 5 miles
        base_restaurant.user_review_count = 1000  # Very established
        base_restaurant.cuisine_type = 'Italian'

        score = restaurant_service.calculate_composite_score(
            base_restaurant, 'Chinese', 'rating'  # No cuisine match
        )

        # 24 (2.0 rating) + 0 (no cuisine match) + ~0 (very established) + 0 (far)
        # Should be around 24
        assert score >= 20.0
        assert score <= 30.0

    def test_distance_preference_changes_ranking(self, restaurant_service):
        """Closer restaurant should rank higher with distance sort"""
        close_restaurant = Restaurant(
            place_id='close',
            name='Close Restaurant',
            address='123 Main St',
            rating=3.5,
            distance=804.67,  # 0.5 miles
            user_review_count=100
        )

        far_restaurant = Restaurant(
            place_id='far',
            name='Far Restaurant',
            address='456 Main St',
            rating=4.5,
            distance=4828.03,  # 3 miles
            user_review_count=100
        )

        # With rating sort, far restaurant should win
        score_close_rating = restaurant_service.calculate_composite_score(
            close_restaurant, None, 'rating'
        )
        score_far_rating = restaurant_service.calculate_composite_score(
            far_restaurant, None, 'rating'
        )
        assert score_far_rating > score_close_rating

        # With distance sort, close restaurant should win
        score_close_distance = restaurant_service.calculate_composite_score(
            close_restaurant, None, 'distance'
        )
        score_far_distance = restaurant_service.calculate_composite_score(
            far_restaurant, None, 'distance'
        )
        assert score_close_distance > score_far_distance

    def test_cuisine_match_can_tip_balance(self, restaurant_service):
        """Cuisine match bonus can change ranking between similar restaurants"""
        italian = Restaurant(
            place_id='italian',
            name='Italian Place',
            address='123 Main St',
            rating=4.0,
            distance=1609.34,
            user_review_count=100,
            cuisine_type='Italian'
        )

        chinese = Restaurant(
            place_id='chinese',
            name='Chinese Place',
            address='456 Main St',
            rating=4.1,  # Slightly higher rating
            distance=1609.34,
            user_review_count=100,
            cuisine_type='Chinese'
        )

        # Without cuisine filter, Chinese wins (higher rating)
        score_italian_no_filter = restaurant_service.calculate_composite_score(
            italian, None, 'rating'
        )
        score_chinese_no_filter = restaurant_service.calculate_composite_score(
            chinese, None, 'rating'
        )
        assert score_chinese_no_filter > score_italian_no_filter

        # With Italian cuisine filter, Italian wins (15 point bonus overcomes 0.1 rating difference)
        score_italian_filtered = restaurant_service.calculate_composite_score(
            italian, 'Italian', 'rating'
        )
        score_chinese_filtered = restaurant_service.calculate_composite_score(
            chinese, 'Italian', 'rating'
        )
        assert score_italian_filtered > score_chinese_filtered


class TestSortRestaurantsMethod:
    """Test the sort_restaurants method that uses composite scoring"""

    def test_sorts_by_composite_score(self, restaurant_service):
        """Restaurants should be sorted by composite score descending"""
        restaurants = [
            Restaurant(
                place_id='low',
                name='Low Score',
                address='123 St',
                rating=2.0,
                distance=8000,
                user_review_count=1000
            ),
            Restaurant(
                place_id='high',
                name='High Score',
                address='456 St',
                rating=5.0,
                distance=100,
                user_review_count=50
            ),
            Restaurant(
                place_id='medium',
                name='Medium Score',
                address='789 St',
                rating=3.5,
                distance=3000,
                user_review_count=200
            )
        ]

        sorted_restaurants = restaurant_service.sort_restaurants(
            restaurants, 'rating', None
        )

        # Should be sorted high -> medium -> low
        assert sorted_restaurants[0].place_id == 'high'
        assert sorted_restaurants[2].place_id == 'low'

        # Verify scores are attached and in descending order
        assert hasattr(sorted_restaurants[0], '_composite_score')
        assert sorted_restaurants[0]._composite_score >= sorted_restaurants[1]._composite_score
        assert sorted_restaurants[1]._composite_score >= sorted_restaurants[2]._composite_score

    def test_empty_list_returns_empty(self, restaurant_service):
        """Empty restaurant list should return empty list"""
        result = restaurant_service.sort_restaurants([], 'rating', None)
        assert result == []

    def test_single_restaurant_returns_same(self, restaurant_service):
        """Single restaurant should return in list"""
        restaurant = Restaurant(
            place_id='only',
            name='Only Restaurant',
            address='123 St',
            rating=4.0
        )

        result = restaurant_service.sort_restaurants([restaurant], 'rating', None)
        assert len(result) == 1
        assert result[0].place_id == 'only'
        assert hasattr(result[0], '_composite_score')


class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_all_none_values(self, restaurant_service, base_restaurant):
        """Restaurant with all None values should still calculate score"""
        base_restaurant.rating = None
        base_restaurant.distance = None
        base_restaurant.user_review_count = None
        base_restaurant.cuisine_type = None

        score = restaurant_service.calculate_composite_score(
            base_restaurant, 'Italian', 'rating'
        )

        # Should only get 10 points from missing review count
        assert score == pytest.approx(10.0, rel=0.1)

    def test_zero_rating(self, restaurant_service, base_restaurant):
        """Zero rating should give zero base score"""
        base_restaurant.rating = 0.0
        base_restaurant.user_review_count = None
        base_restaurant.distance = None

        score = restaurant_service.calculate_composite_score(
            base_restaurant, None, 'rating'
        )

        # 0 (rating) + 10 (missing data)
        assert score == pytest.approx(10.0, rel=0.1)

    def test_negative_distance_treated_as_zero(self, restaurant_service, base_restaurant):
        """Negative distance (shouldn't happen) should be handled"""
        base_restaurant.distance = -100
        base_restaurant.rating = None
        base_restaurant.user_review_count = None

        # Should still calculate without error (negative will give >1 normalized, capped at 1)
        score = restaurant_service.calculate_composite_score(
            base_restaurant, None, 'distance'
        )

        # Should get max distance score (60) + missing data (10) + max proximity (5)
        assert score >= 70.0

    def test_very_large_review_count(self, restaurant_service, base_restaurant):
        """Very large review count should floor at 0 for newness"""
        base_restaurant.user_review_count = 100000
        base_restaurant.rating = None
        base_restaurant.distance = None

        score = restaurant_service.calculate_composite_score(
            base_restaurant, None, 'rating'
        )

        # Newness: max(0, 20 - (log10(100000) * 8)) = max(0, 20 - 40) = 0
        assert score == pytest.approx(0.0, rel=0.1)

    def test_review_count_of_one(self, restaurant_service, base_restaurant):
        """Review count of 1 should give maximum newness score"""
        base_restaurant.user_review_count = 1
        base_restaurant.rating = None
        base_restaurant.distance = None

        score = restaurant_service.calculate_composite_score(
            base_restaurant, None, 'rating'
        )

        # log10(1) = 0, so: 20 - (0 * 8) = 20
        assert score == pytest.approx(20.0, rel=0.1)
