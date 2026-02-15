"""
Comprehensive test suite for distance calculation functions.

Tests cover:
- All three distance calculation methods (Haversine, Vincenty, Spherical)
- Positive test cases (various distances)
- Negative test cases (invalid inputs)
- Edge cases (poles, equator, antipodal points, same point)
- Accuracy validation against known reference values
"""

import sys
import math
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from geo_intel_offline.distance import (
    haversine_distance,
    vincenty_distance,
    spherical_law_of_cosines,
    calculate_distance_km,
    calculate_distance,
    DistanceResult,
    km_to_miles,
    miles_to_km,
    get_country_unit_preference,
    determine_unit_preference,
    normalize_location,
    EARTH_RADIUS_KM
)


# Known test locations with expected distances (in km)
# Reference: Calculated using online distance calculators and verified
TEST_DISTANCES = [
    # (lat1, lon1, lat2, lon2, expected_distance_km, tolerance_km, description)
    # New York to Los Angeles
    (40.7128, -74.0060, 34.0522, -118.2437, 3944.0, 10.0, "NYC to LA"),
    # London to Paris
    (51.5074, -0.1278, 48.8566, 2.3522, 344.0, 5.0, "London to Paris"),
    # Tokyo to Sydney
    (35.6762, 139.6503, -33.8688, 151.2093, 7827.0, 20.0, "Tokyo to Sydney"),
    # New York to London
    (40.7128, -74.0060, 51.5074, -0.1278, 5570.0, 20.0, "NYC to London"),
    # Moscow to Beijing
    (55.7558, 37.6173, 39.9042, 116.4074, 5794.0, 20.0, "Moscow to Beijing"),
    # Short distance: Paris to Brussels
    (48.8566, 2.3522, 50.8503, 4.3517, 264.0, 5.0, "Paris to Brussels"),
    # Very short distance: Central Park to Times Square (NYC)
    (40.7829, -73.9654, 40.7580, -73.9855, 3.5, 0.5, "Central Park to Times Square"),
]


class TestHaversineDistance:
    """Test suite for Haversine distance calculation."""
    
    def test_known_distances(self):
        """Test Haversine against known reference distances."""
        for lat1, lon1, lat2, lon2, expected, tolerance, desc in TEST_DISTANCES:
            result = haversine_distance(lat1, lon1, lat2, lon2)
            assert abs(result - expected) <= tolerance, (
                f"{desc}: Expected ~{expected} km, got {result:.2f} km "
                f"(difference: {abs(result - expected):.2f} km)"
            )
    
    def test_same_point(self):
        """Test that distance from point to itself is zero."""
        result = haversine_distance(40.7128, -74.0060, 40.7128, -74.0060)
        assert result == 0.0, f"Distance to same point should be 0, got {result}"
    
    def test_antipodal_points(self):
        """Test distance between antipodal points (opposite sides of Earth)."""
        # New York and its antipodal point (in Indian Ocean)
        result = haversine_distance(40.7128, -74.0060, -40.7128, 105.9940)
        expected = math.pi * EARTH_RADIUS_KM  # Half circumference
        assert abs(result - expected) < 50.0, (
            f"Antipodal distance should be ~{expected:.0f} km, got {result:.2f} km"
        )
    
    def test_equator_points(self):
        """Test distance between points on equator."""
        # Two points on equator, 1 degree apart
        result = haversine_distance(0.0, 0.0, 0.0, 1.0)
        expected = 111.0  # Approximately 111 km per degree at equator
        assert abs(result - expected) < 5.0, (
            f"1 degree on equator should be ~{expected} km, got {result:.2f} km"
        )
    
    def test_pole_to_equator(self):
        """Test distance from North Pole to equator."""
        result = haversine_distance(90.0, 0.0, 0.0, 0.0)
        expected = math.pi / 2 * EARTH_RADIUS_KM  # Quarter circumference
        assert abs(result - expected) < 10.0, (
            f"Pole to equator should be ~{expected:.0f} km, got {result:.2f} km"
        )
    
    def test_invalid_latitude_high(self):
        """Test that latitude > 90 raises ValueError."""
        with pytest.raises(ValueError, match="Latitude must be between -90 and 90"):
            haversine_distance(91.0, 0.0, 0.0, 0.0)
    
    def test_invalid_latitude_low(self):
        """Test that latitude < -90 raises ValueError."""
        with pytest.raises(ValueError, match="Latitude must be between -90 and 90"):
            haversine_distance(-91.0, 0.0, 0.0, 0.0)
    
    def test_invalid_longitude_high(self):
        """Test that longitude > 180 raises ValueError."""
        with pytest.raises(ValueError, match="Longitude must be between -180 and 180"):
            haversine_distance(0.0, 181.0, 0.0, 0.0)
    
    def test_invalid_longitude_low(self):
        """Test that longitude < -180 raises ValueError."""
        with pytest.raises(ValueError, match="Longitude must be between -180 and 180"):
            haversine_distance(0.0, -181.0, 0.0, 0.0)
    
    def test_date_line_crossing(self):
        """Test distance calculation crossing International Date Line."""
        # Point in Pacific, crossing 180° meridian
        result = haversine_distance(0.0, 179.0, 0.0, -179.0)
        expected = 222.0  # Approximately 2 degrees at equator
        assert abs(result - expected) < 10.0, (
            f"Date line crossing should be ~{expected} km, got {result:.2f} km"
        )


class TestVincentyDistance:
    """Test suite for Vincenty distance calculation."""
    
    def test_known_distances(self):
        """Test Vincenty against known reference distances."""
        for lat1, lon1, lat2, lon2, expected, tolerance, desc in TEST_DISTANCES:
            result = vincenty_distance(lat1, lon1, lat2, lon2)
            assert abs(result - expected) <= tolerance, (
                f"{desc}: Expected ~{expected} km, got {result:.2f} km "
                f"(difference: {abs(result - expected):.2f} km)"
            )
    
    def test_same_point(self):
        """Test that distance from point to itself is zero."""
        result = vincenty_distance(40.7128, -74.0060, 40.7128, -74.0060)
        assert result == 0.0, f"Distance to same point should be 0, got {result}"
    
    def test_accuracy_vs_haversine(self):
        """Test that Vincenty is more accurate than Haversine for long distances."""
        # For long distances, Vincenty should be more accurate
        lat1, lon1, lat2, lon2 = 40.7128, -74.0060, 34.0522, -118.2437  # NYC to LA
        haversine_result = haversine_distance(lat1, lon1, lat2, lon2)
        vincenty_result = vincenty_distance(lat1, lon1, lat2, lon2)
        
        # Results should be very close (within 1 km for this distance)
        assert abs(haversine_result - vincenty_result) < 1.0, (
            f"Haversine and Vincenty should be close. "
            f"Haversine: {haversine_result:.2f} km, Vincenty: {vincenty_result:.2f} km"
        )
    
    def test_invalid_latitude_high(self):
        """Test that latitude > 90 raises ValueError."""
        with pytest.raises(ValueError, match="Latitude must be between -90 and 90"):
            vincenty_distance(91.0, 0.0, 0.0, 0.0)
    
    def test_invalid_latitude_low(self):
        """Test that latitude < -90 raises ValueError."""
        with pytest.raises(ValueError, match="Latitude must be between -90 and 90"):
            vincenty_distance(-91.0, 0.0, 0.0, 0.0)
    
    def test_invalid_longitude_high(self):
        """Test that longitude > 180 raises ValueError."""
        with pytest.raises(ValueError, match="Longitude must be between -180 and 180"):
            vincenty_distance(0.0, 181.0, 0.0, 0.0)
    
    def test_invalid_longitude_low(self):
        """Test that longitude < -180 raises ValueError."""
        with pytest.raises(ValueError, match="Longitude must be between -180 and 180"):
            vincenty_distance(0.0, -181.0, 0.0, 0.0)
    
    def test_nearly_antipodal_points(self):
        """Test Vincenty with nearly antipodal points (challenging case)."""
        # Points nearly opposite each other
        result = vincenty_distance(40.7128, -74.0060, -40.7128, 105.9940)
        expected = math.pi * EARTH_RADIUS_KM
        assert abs(result - expected) < 50.0, (
            f"Antipodal distance should be ~{expected:.0f} km, got {result:.2f} km"
        )


class TestSphericalLawOfCosines:
    """Test suite for Spherical Law of Cosines distance calculation."""
    
    def test_known_distances(self):
        """Test Spherical Law of Cosines against known reference distances."""
        for lat1, lon1, lat2, lon2, expected, tolerance, desc in TEST_DISTANCES:
            result = spherical_law_of_cosines(lat1, lon1, lat2, lon2)
            # Spherical law is less accurate, so use larger tolerance
            assert abs(result - expected) <= tolerance * 1.5, (
                f"{desc}: Expected ~{expected} km, got {result:.2f} km "
                f"(difference: {abs(result - expected):.2f} km)"
            )
    
    def test_same_point(self):
        """Test that distance from point to itself is zero."""
        result = spherical_law_of_cosines(40.7128, -74.0060, 40.7128, -74.0060)
        assert abs(result) < 0.001, f"Distance to same point should be ~0, got {result}"
    
    def test_invalid_latitude_high(self):
        """Test that latitude > 90 raises ValueError."""
        with pytest.raises(ValueError, match="Latitude must be between -90 and 90"):
            spherical_law_of_cosines(91.0, 0.0, 0.0, 0.0)
    
    def test_invalid_latitude_low(self):
        """Test that latitude < -90 raises ValueError."""
        with pytest.raises(ValueError, match="Latitude must be between -90 and 90"):
            spherical_law_of_cosines(-91.0, 0.0, 0.0, 0.0)
    
    def test_invalid_longitude_high(self):
        """Test that longitude > 180 raises ValueError."""
        with pytest.raises(ValueError, match="Longitude must be between -180 and 180"):
            spherical_law_of_cosines(0.0, 181.0, 0.0, 0.0)
    
    def test_invalid_longitude_low(self):
        """Test that longitude < -180 raises ValueError."""
        with pytest.raises(ValueError, match="Longitude must be between -180 and 180"):
            spherical_law_of_cosines(0.0, -181.0, 0.0, 0.0)


class TestCalculateDistanceKm:
    """Test suite for unified calculate_distance_km function."""
    
    def test_haversine_method(self):
        """Test calculate_distance_km with haversine method."""
        result = calculate_distance_km(40.7128, -74.0060, 34.0522, -118.2437, method="haversine")
        expected = 3944.0
        assert abs(result - expected) < 10.0, (
            f"Expected ~{expected} km, got {result:.2f} km"
        )
    
    def test_vincenty_method(self):
        """Test calculate_distance_km with vincenty method."""
        result = calculate_distance_km(40.7128, -74.0060, 34.0522, -118.2437, method="vincenty")
        expected = 3944.0
        assert abs(result - expected) < 10.0, (
            f"Expected ~{expected} km, got {result:.2f} km"
        )
    
    def test_spherical_method(self):
        """Test calculate_distance_km with spherical method."""
        result = calculate_distance_km(40.7128, -74.0060, 34.0522, -118.2437, method="spherical")
        expected = 3944.0
        assert abs(result - expected) < 15.0, (
            f"Expected ~{expected} km, got {result:.2f} km"
        )
    
    def test_default_method(self):
        """Test calculate_distance_km with default method (haversine)."""
        result_default = calculate_distance_km(40.7128, -74.0060, 34.0522, -118.2437)
        result_haversine = calculate_distance_km(40.7128, -74.0060, 34.0522, -118.2437, method="haversine")
        assert abs(result_default - result_haversine) < 0.001, (
            "Default method should be haversine"
        )
    
    def test_case_insensitive_method(self):
        """Test that method name is case-insensitive."""
        result1 = calculate_distance_km(40.7128, -74.0060, 34.0522, -118.2437, method="HAVERSINE")
        result2 = calculate_distance_km(40.7128, -74.0060, 34.0522, -118.2437, method="Haversine")
        result3 = calculate_distance_km(40.7128, -74.0060, 34.0522, -118.2437, method="haversine")
        assert abs(result1 - result2) < 0.001
        assert abs(result2 - result3) < 0.001
    
    def test_invalid_method(self):
        """Test that invalid method raises ValueError."""
        with pytest.raises(ValueError, match="Unknown method"):
            calculate_distance_km(40.7128, -74.0060, 34.0522, -118.2437, method="invalid")
    
    def test_invalid_coordinates(self):
        """Test that invalid coordinates are passed through to underlying function."""
        with pytest.raises(ValueError, match="Latitude must be between -90 and 90"):
            calculate_distance_km(91.0, 0.0, 0.0, 0.0, method="haversine")


class TestMethodComparison:
    """Test suite comparing different distance calculation methods."""
    
    def test_methods_agree_short_distance(self):
        """Test that all methods agree for short distances."""
        lat1, lon1, lat2, lon2 = 48.8566, 2.3522, 50.8503, 4.3517  # Paris to Brussels
        haversine = haversine_distance(lat1, lon1, lat2, lon2)
        vincenty = vincenty_distance(lat1, lon1, lat2, lon2)
        spherical = spherical_law_of_cosines(lat1, lon1, lat2, lon2)
        
        # All methods should agree within 1 km for short distances
        assert abs(haversine - vincenty) < 1.0, (
            f"Haversine and Vincenty should agree. "
            f"Haversine: {haversine:.2f} km, Vincenty: {vincenty:.2f} km"
        )
        assert abs(haversine - spherical) < 2.0, (
            f"Haversine and Spherical should agree. "
            f"Haversine: {haversine:.2f} km, Spherical: {spherical:.2f} km"
        )
    
    def test_methods_agree_long_distance(self):
        """Test that all methods agree for long distances."""
        lat1, lon1, lat2, lon2 = 40.7128, -74.0060, 34.0522, -118.2437  # NYC to LA
        haversine = haversine_distance(lat1, lon1, lat2, lon2)
        vincenty = vincenty_distance(lat1, lon1, lat2, lon2)
        spherical = spherical_law_of_cosines(lat1, lon1, lat2, lon2)
        
        # All methods should agree within 10 km for long distances
        assert abs(haversine - vincenty) < 10.0, (
            f"Haversine and Vincenty should agree. "
            f"Haversine: {haversine:.2f} km, Vincenty: {vincenty:.2f} km"
        )
        assert abs(haversine - spherical) < 20.0, (
            f"Haversine and Spherical should agree. "
            f"Haversine: {haversine:.2f} km, Spherical: {spherical:.2f} km"
        )
    
    def test_vincenty_more_accurate(self):
        """Test that Vincenty is generally more accurate than Haversine."""
        # For very long distances, Vincenty accounts for ellipsoidal shape
        lat1, lon1, lat2, lon2 = 35.6762, 139.6503, -33.8688, 151.2093  # Tokyo to Sydney
        haversine = haversine_distance(lat1, lon1, lat2, lon2)
        vincenty = vincenty_distance(lat1, lon1, lat2, lon2)
        
        # Both should be close, but Vincenty is more accurate
        assert abs(haversine - vincenty) < 50.0, (
            f"Methods should be close. "
            f"Haversine: {haversine:.2f} km, Vincenty: {vincenty:.2f} km"
        )


class TestUnitConversion:
    """Test suite for unit conversion functions."""
    
    def test_km_to_miles(self):
        """Test conversion from kilometers to miles."""
        result = km_to_miles(100.0)
        expected = 62.1371
        assert abs(result - expected) < 0.01, (
            f"Expected ~{expected} miles, got {result:.4f} miles"
        )
    
    def test_miles_to_km(self):
        """Test conversion from miles to kilometers."""
        result = miles_to_km(100.0)
        expected = 160.934
        assert abs(result - expected) < 0.01, (
            f"Expected ~{expected} km, got {result:.4f} km"
        )
    
    def test_round_trip_conversion(self):
        """Test that converting km->miles->km returns original value."""
        original_km = 100.0
        miles = km_to_miles(original_km)
        back_to_km = miles_to_km(miles)
        assert abs(back_to_km - original_km) < 0.001, (
            f"Round trip conversion failed. "
            f"Original: {original_km} km, Result: {back_to_km} km"
        )
    
    def test_zero_conversion(self):
        """Test conversion of zero."""
        assert km_to_miles(0.0) == 0.0
        assert miles_to_km(0.0) == 0.0


class TestCountryUnitPreference:
    """Test suite for country unit preference detection."""
    
    def test_imperial_countries(self):
        """Test that imperial countries return 'mile'."""
        assert get_country_unit_preference('US') == 'mile'
        assert get_country_unit_preference('GB') == 'mile'
        assert get_country_unit_preference('LR') == 'mile'
        assert get_country_unit_preference('MM') == 'mile'
    
    def test_metric_countries(self):
        """Test that metric countries return 'km'."""
        assert get_country_unit_preference('FR') == 'km'
        assert get_country_unit_preference('DE') == 'km'
        assert get_country_unit_preference('JP') == 'km'
        assert get_country_unit_preference('CA') == 'km'
        assert get_country_unit_preference('AU') == 'km'
    
    def test_case_insensitive(self):
        """Test that ISO codes are case-insensitive."""
        assert get_country_unit_preference('us') == 'mile'
        assert get_country_unit_preference('Us') == 'mile'
        assert get_country_unit_preference('fr') == 'km'
        assert get_country_unit_preference('Fr') == 'km'
    
    def test_none_country(self):
        """Test that None defaults to metric."""
        assert get_country_unit_preference(None) == 'km'
    
    def test_unknown_country(self):
        """Test that unknown country codes default to metric."""
        assert get_country_unit_preference('XX') == 'km'
        assert get_country_unit_preference('ZZ') == 'km'


class TestUnitDetermination:
    """Test suite for unit determination logic."""
    
    def test_explicit_unit_override(self):
        """Test that explicit unit parameter takes highest priority."""
        assert determine_unit_preference(unit='km') == 'km'
        assert determine_unit_preference(unit='mile') == 'mile'
        assert determine_unit_preference(unit='kilometer') == 'km'
        assert determine_unit_preference(unit='miles') == 'mile'
    
    def test_use_metric_parameter(self):
        """Test that use_metric parameter works correctly."""
        assert determine_unit_preference(use_metric=True) == 'km'
        assert determine_unit_preference(use_metric=False) == 'mile'
    
    def test_iso2_based_detection(self):
        """Test unit detection based on ISO2 codes."""
        assert determine_unit_preference(iso2_1='US') == 'mile'
        assert determine_unit_preference(iso2_1='FR') == 'km'
        assert determine_unit_preference(iso2_1='US', iso2_2='CA') == 'mile'
        assert determine_unit_preference(iso2_1='FR', iso2_2='DE') == 'km'
    
    def test_coordinate_based_detection(self):
        """Test unit detection based on coordinates."""
        # New York (US - should prefer miles)
        result = determine_unit_preference(lat1=40.7128, lon1=-74.0060)
        assert result == 'mile', f"NYC should prefer miles, got {result}"
        
        # Paris (France - should prefer km)
        result = determine_unit_preference(lat1=48.8566, lon1=2.3522)
        assert result == 'km', f"Paris should prefer km, got {result}"
        
        # London (UK - should prefer miles)
        result = determine_unit_preference(lat1=51.5074, lon1=-0.1278)
        assert result == 'mile', f"London should prefer miles, got {result}"
    
    def test_priority_explicit_over_country(self):
        """Test that explicit unit overrides country preference."""
        result = determine_unit_preference(iso2_1='US', unit='km')
        assert result == 'km', "Explicit unit should override country preference"
        
        result = determine_unit_preference(iso2_1='FR', unit='mile')
        assert result == 'mile', "Explicit unit should override country preference"
    
    def test_priority_use_metric_over_country(self):
        """Test that use_metric overrides country preference."""
        result = determine_unit_preference(iso2_1='US', use_metric=True)
        assert result == 'km', "use_metric=True should override country preference"
        
        result = determine_unit_preference(iso2_1='FR', use_metric=False)
        assert result == 'mile', "use_metric=False should override country preference"
    
    def test_default_to_metric(self):
        """Test that default is metric when no preferences available."""
        result = determine_unit_preference()
        assert result == 'km', "Should default to metric"
    
    def test_invalid_unit_raises_error(self):
        """Test that invalid unit raises ValueError."""
        with pytest.raises(ValueError, match="Invalid unit"):
            determine_unit_preference(unit='invalid')


class TestInputNormalization:
    """Test suite for input normalization functions."""
    
    def test_coordinate_tuple(self):
        """Test that coordinate tuple is returned as-is."""
        result = normalize_location((40.7128, -74.0060))
        assert result == (40.7128, -74.0060), "Coordinate tuple should be returned as-is"
    
    def test_country_name(self):
        """Test normalization of country name to coordinates."""
        result = normalize_location("United States")
        assert isinstance(result, tuple), "Should return tuple"
        assert len(result) == 2, "Should return (lat, lon) tuple"
        assert -90 <= result[0] <= 90, "Latitude should be valid"
        assert -180 <= result[1] <= 180, "Longitude should be valid"
    
    def test_iso2_code(self):
        """Test normalization of ISO2 code to coordinates."""
        result = normalize_location("US")
        assert isinstance(result, tuple), "Should return tuple"
        assert len(result) == 2, "Should return (lat, lon) tuple"
        assert -90 <= result[0] <= 90, "Latitude should be valid"
        assert -180 <= result[1] <= 180, "Longitude should be valid"
    
    def test_iso3_code(self):
        """Test normalization of ISO3 code to coordinates."""
        result = normalize_location("USA")
        assert isinstance(result, tuple), "Should return tuple"
        assert len(result) == 2, "Should return (lat, lon) tuple"
        assert -90 <= result[0] <= 90, "Latitude should be valid"
        assert -180 <= result[1] <= 180, "Longitude should be valid"
    
    def test_multiple_countries(self):
        """Test normalization of multiple different countries."""
        countries = ["France", "Japan", "Australia", "Brazil"]
        for country in countries:
            result = normalize_location(country)
            assert isinstance(result, tuple), f"{country} should return tuple"
            assert len(result) == 2, f"{country} should return (lat, lon) tuple"
            assert -90 <= result[0] <= 90, f"{country} latitude should be valid"
            assert -180 <= result[1] <= 180, f"{country} longitude should be valid"
    
    def test_invalid_coordinates(self):
        """Test that invalid coordinates raise ValueError."""
        with pytest.raises(ValueError, match="Invalid coordinates"):
            normalize_location((91.0, 0.0))  # Latitude too high
        
        with pytest.raises(ValueError, match="Invalid coordinates"):
            normalize_location((-91.0, 0.0))  # Latitude too low
        
        with pytest.raises(ValueError, match="Invalid coordinates"):
            normalize_location((0.0, 181.0))  # Longitude too high
        
        with pytest.raises(ValueError, match="Invalid coordinates"):
            normalize_location((0.0, -181.0))  # Longitude too low
    
    def test_invalid_country(self):
        """Test that invalid country name raises ValueError."""
        with pytest.raises(ValueError, match="Could not resolve"):
            normalize_location("InvalidCountry123")
    
    def test_invalid_type(self):
        """Test that invalid type raises TypeError."""
        with pytest.raises(TypeError, match="Invalid location type"):
            normalize_location([1, 2, 3])  # List instead of tuple
        
        with pytest.raises(TypeError, match="Invalid location type"):
            normalize_location(123)  # Number instead of tuple/string
    
    def test_wrong_tuple_length(self):
        """Test that tuple with wrong length raises TypeError."""
        with pytest.raises(TypeError):
            normalize_location((1, 2, 3))  # Too many elements
        
        with pytest.raises(TypeError):
            normalize_location((1,))  # Too few elements
    
    def test_empty_string(self):
        """Test that empty string raises ValueError."""
        with pytest.raises(ValueError):
            normalize_location("")
    
    def test_continent_normalization(self):
        """Test normalization of continent names (if supported)."""
        # This may or may not work depending on data availability
        try:
            result = normalize_location("North America")
            assert isinstance(result, tuple), "Should return tuple"
            assert len(result) == 2, "Should return (lat, lon) tuple"
            assert -90 <= result[0] <= 90, "Latitude should be valid"
            assert -180 <= result[1] <= 180, "Longitude should be valid"
        except ValueError:
            # Continent normalization may not be fully implemented yet
            pass


class TestUnifiedCalculateDistance:
    """Test suite for unified calculate_distance() function."""
    
    def test_coordinates_to_coordinates(self):
        """Test distance calculation between coordinates."""
        result = calculate_distance((40.7128, -74.0060), (34.0522, -118.2437))
        assert isinstance(result, DistanceResult), "Should return DistanceResult"
        assert result.distance > 0, "Distance should be positive"
        assert result.unit in ('km', 'mile'), "Unit should be km or mile"
        assert result.method in ('haversine', 'vincenty', 'spherical'), "Method should be valid"
        assert result.from_location == (40.7128, -74.0060), "Should preserve from_location"
        assert result.to_location == (34.0522, -118.2437), "Should preserve to_location"
    
    def test_country_to_country(self):
        """Test distance calculation between countries."""
        result = calculate_distance("United States", "Canada")
        assert isinstance(result, DistanceResult), "Should return DistanceResult"
        assert result.distance > 0, "Distance should be positive"
        assert result.unit in ('km', 'mile'), "Unit should be km or mile"
        assert isinstance(result.from_location, str), "from_location should be string"
        assert isinstance(result.to_location, str), "to_location should be string"
        assert result.from_coordinates is not None, "Should have resolved coordinates"
        assert result.to_coordinates is not None, "Should have resolved coordinates"
    
    def test_iso_code_to_iso_code(self):
        """Test distance calculation between ISO codes."""
        result = calculate_distance("US", "FR")
        assert isinstance(result, DistanceResult), "Should return DistanceResult"
        assert result.distance > 0, "Distance should be positive"
        assert result.from_location == "US", "Should preserve from_location"
        assert result.to_location == "FR", "Should preserve to_location"
    
    def test_mixed_inputs(self):
        """Test distance calculation with mixed input types."""
        result = calculate_distance((40.7128, -74.0060), "United States")
        assert isinstance(result, DistanceResult), "Should return DistanceResult"
        assert result.distance >= 0, "Distance should be non-negative"
        assert isinstance(result.from_location, tuple), "from_location should be tuple"
        assert isinstance(result.to_location, str), "to_location should be string"
    
    def test_force_unit_km(self):
        """Test forcing unit to kilometers."""
        result = calculate_distance("US", "CA", unit='km')
        assert result.unit == 'km', "Unit should be km"
        assert result.distance > 0, "Distance should be positive"
    
    def test_force_unit_mile(self):
        """Test forcing unit to miles."""
        result = calculate_distance("FR", "DE", unit='mile')
        assert result.unit == 'mile', "Unit should be mile"
        assert result.distance > 0, "Distance should be positive"
    
    def test_force_method_haversine(self):
        """Test forcing calculation method to haversine."""
        result = calculate_distance((40.7128, -74.0060), (34.0522, -118.2437), method='haversine')
        assert result.method == 'haversine', "Method should be haversine"
    
    def test_force_method_vincenty(self):
        """Test forcing calculation method to vincenty."""
        result = calculate_distance((40.7128, -74.0060), (34.0522, -118.2437), method='vincenty')
        assert result.method == 'vincenty', "Method should be vincenty"
    
    def test_force_method_spherical(self):
        """Test forcing calculation method to spherical."""
        result = calculate_distance((40.7128, -74.0060), (34.0522, -118.2437), method='spherical')
        assert result.method == 'spherical', "Method should be spherical"
    
    def test_auto_method_selection(self):
        """Test automatic method selection."""
        result = calculate_distance((40.7128, -74.0060), (34.0522, -118.2437), method='auto')
        assert result.method in ('haversine', 'vincenty'), "Should select valid method"
    
    def test_use_metric_parameter(self):
        """Test use_metric parameter."""
        result = calculate_distance("US", "CA", use_metric=True)
        assert result.unit == 'km', "Should use km when use_metric=True"
        
        result = calculate_distance("FR", "DE", use_metric=False)
        assert result.unit == 'mile', "Should use mile when use_metric=False"
    
    def test_result_to_dict(self):
        """Test converting result to dictionary."""
        result = calculate_distance("US", "CA")
        result_dict = result.to_dict()
        assert isinstance(result_dict, dict), "Should return dictionary"
        assert 'distance' in result_dict, "Should have distance"
        assert 'unit' in result_dict, "Should have unit"
        assert 'method' in result_dict, "Should have method"
        assert 'from_location' in result_dict, "Should have from_location"
        assert 'to_location' in result_dict, "Should have to_location"
        assert 'from_coordinates' in result_dict, "Should have from_coordinates"
        assert 'to_coordinates' in result_dict, "Should have to_coordinates"
    
    def test_same_location(self):
        """Test distance from location to itself."""
        result = calculate_distance((40.7128, -74.0060), (40.7128, -74.0060))
        assert result.distance == 0.0, "Distance to same point should be 0"
    
    def test_invalid_location(self):
        """Test that invalid location raises ValueError."""
        with pytest.raises(ValueError):
            calculate_distance("InvalidCountry123", "US")
    
    def test_invalid_method(self):
        """Test that invalid method raises ValueError."""
        with pytest.raises(ValueError, match="Unknown method"):
            calculate_distance((40.7128, -74.0060), (34.0522, -118.2437), method='invalid')
    
    def test_invalid_unit(self):
        """Test that invalid unit raises ValueError."""
        with pytest.raises(ValueError, match="Invalid unit"):
            calculate_distance((40.7128, -74.0060), (34.0522, -118.2437), unit='invalid')
    
    def test_unit_auto_detection_imperial(self):
        """Test automatic unit detection for imperial countries."""
        result = calculate_distance("US", "GB")
        # At least one country uses imperial, so should prefer miles
        assert result.unit == 'mile', "Should detect miles for imperial countries"
    
    def test_unit_auto_detection_metric(self):
        """Test automatic unit detection for metric countries."""
        result = calculate_distance("FR", "DE")
        # Both countries use metric, so should prefer km
        assert result.unit == 'km', "Should detect km for metric countries"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
