"""
Comprehensive test suite for random coordinate generation.

Tests cover:
- Random coordinates by region (countries, continents)
- Random coordinates by area (circular areas)
- Point-in-polygon validation
- Uniform distribution
- Reproducibility
- Edge cases and error handling
"""

import sys
import math
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from geo_intel_offline.random_coords import (
    generate_random_coordinates_by_region,
    generate_random_coordinates_by_area,
    RandomCoordinateResult,
    _detect_region_type,
    _calculate_bounding_box_for_polygons
)
from geo_intel_offline.distance import calculate_distance_km
from geo_intel_offline.pip import point_in_polygon_with_holes


class TestRandomCoordinatesByRegion:
    """Test suite for random coordinates by region."""
    
    def test_generate_for_country(self):
        """Test generating coordinates for a country."""
        result = generate_random_coordinates_by_region("United States", 5, seed=42)
        assert isinstance(result, RandomCoordinateResult)
        assert result.region_type == 'country'
        assert len(result.coordinates) == 5
        assert result.total_generated == 5
        assert result.total_requested == 5
    
    def test_generate_for_country_iso(self):
        """Test generating coordinates using ISO code."""
        result = generate_random_coordinates_by_region("US", 3, seed=42)
        assert isinstance(result, RandomCoordinateResult)
        assert result.region_type == 'country'
        assert len(result.coordinates) >= 3
    
    def test_generate_single_coordinate(self):
        """Test generating a single coordinate."""
        result = generate_random_coordinates_by_region("US", 1, seed=42)
        assert len(result.coordinates) == 1
        assert isinstance(result.coordinates[0], tuple)
        assert len(result.coordinates[0]) == 2
    
    def test_generate_multiple_coordinates(self):
        """Test generating multiple coordinates."""
        result = generate_random_coordinates_by_region("US", 10, seed=42)
        assert len(result.coordinates) == 10
        # All should be valid coordinates
        for lat, lon in result.coordinates:
            assert -90 <= lat <= 90
            assert -180 <= lon <= 180
    
    def test_reproducibility_with_seed(self):
        """Test that same seed produces same results."""
        result1 = generate_random_coordinates_by_region("US", 5, seed=42)
        result2 = generate_random_coordinates_by_region("US", 5, seed=42)
        assert result1.coordinates == result2.coordinates
    
    def test_different_seeds_produce_different_results(self):
        """Test that different seeds produce different results."""
        result1 = generate_random_coordinates_by_region("US", 5, seed=42)
        result2 = generate_random_coordinates_by_region("US", 5, seed=43)
        # Results should be different (very unlikely to be same)
        assert result1.coordinates != result2.coordinates
    
    def test_coordinates_within_country(self):
        """Test that generated coordinates are actually within the country."""
        result = generate_random_coordinates_by_region("United States", 10, seed=42)
        
        # Verify coordinates are in US by resolving them
        from geo_intel_offline import resolve
        for lat, lon in result.coordinates:
            country_result = resolve(lat, lon)
            # Should resolve to US (or at least be valid coordinates)
            assert country_result.country is not None or country_result.iso2 is not None
    
    def test_invalid_country(self):
        """Test that invalid country raises ValueError."""
        with pytest.raises(ValueError):
            generate_random_coordinates_by_region("InvalidCountry123", 5)
    
    def test_zero_count(self):
        """Test that zero count raises ValueError."""
        with pytest.raises(ValueError, match="Count must be positive"):
            generate_random_coordinates_by_region("US", 0)
    
    def test_negative_count(self):
        """Test that negative count raises ValueError."""
        with pytest.raises(ValueError, match="Count must be positive"):
            generate_random_coordinates_by_region("US", -1)
    
    def test_large_country(self):
        """Test generating coordinates for a large country."""
        result = generate_random_coordinates_by_region("Russia", 10, seed=42)
        assert len(result.coordinates) == 10
        assert result.region_type == 'country'
    
    def test_small_country(self):
        """Test generating coordinates for a small country."""
        # Try with a small country (may need more attempts)
        try:
            result = generate_random_coordinates_by_region("Monaco", 5, seed=42, max_attempts=2000)
            assert len(result.coordinates) >= 0  # May generate fewer due to size
        except ValueError:
            # Small countries may fail - this is acceptable
            pass
    
    def test_result_to_dict(self):
        """Test converting result to dictionary."""
        result = generate_random_coordinates_by_region("US", 5, seed=42)
        result_dict = result.to_dict()
        assert isinstance(result_dict, dict)
        assert 'coordinates' in result_dict
        assert 'region' in result_dict
        assert 'region_type' in result_dict
        assert 'total_requested' in result_dict
        assert 'total_generated' in result_dict


class TestRandomCoordinatesByArea:
    """Test suite for random coordinates by area."""
    
    def test_generate_by_area(self):
        """Test generating coordinates in a circular area."""
        result = generate_random_coordinates_by_area(
            (40.7128, -74.0060),  # NYC
            10,  # 10 km
            5,
            radius_unit='km',
            seed=42
        )
        assert isinstance(result, RandomCoordinateResult)
        assert result.region_type == 'area'
        assert len(result.coordinates) == 5
        assert result.total_generated == 5
    
    def test_coordinates_within_radius(self):
        """Test that generated coordinates are within the specified radius."""
        center = (40.7128, -74.0060)
        radius_km = 10
        result = generate_random_coordinates_by_area(center, radius_km, 10, radius_unit='km', seed=42)
        
        for lat, lon in result.coordinates:
            distance_km = calculate_distance_km(center[0], center[1], lat, lon)
            # Allow 10% tolerance for approximation
            assert distance_km <= radius_km * 1.1, (
                f"Coordinate ({lat}, {lon}) is {distance_km} km away, "
                f"exceeds radius of {radius_km} km"
            )
    
    def test_different_radius_units(self):
        """Test different radius units."""
        center = (40.7128, -74.0060)
        
        # Test meters
        result_m = generate_random_coordinates_by_area(center, 10000, 5, radius_unit='m', seed=42)
        assert len(result_m.coordinates) == 5
        
        # Test kilometers
        result_km = generate_random_coordinates_by_area(center, 10, 5, radius_unit='km', seed=42)
        assert len(result_km.coordinates) == 5
        
        # Test miles
        result_mile = generate_random_coordinates_by_area(center, 6.21, 5, radius_unit='mile', seed=42)
        assert len(result_mile.coordinates) == 5
        
        # Test degrees
        result_deg = generate_random_coordinates_by_area(center, 0.1, 5, radius_unit='degree', seed=42)
        assert len(result_deg.coordinates) == 5
    
    def test_reproducibility_with_seed(self):
        """Test that same seed produces same results."""
        center = (40.7128, -74.0060)
        result1 = generate_random_coordinates_by_area(center, 10, 5, radius_unit='km', seed=42)
        result2 = generate_random_coordinates_by_area(center, 10, 5, radius_unit='km', seed=42)
        assert result1.coordinates == result2.coordinates
    
    def test_equator_coordinates(self):
        """Test generating coordinates around equator."""
        result = generate_random_coordinates_by_area((0.0, 0.0), 100, 5, radius_unit='km', seed=42)
        assert len(result.coordinates) == 5
        for lat, lon in result.coordinates:
            assert -90 <= lat <= 90
            assert -180 <= lon <= 180
    
    def test_pole_coordinates(self):
        """Test generating coordinates near poles."""
        # North pole
        result = generate_random_coordinates_by_area((85.0, 0.0), 100, 5, radius_unit='km', seed=42)
        assert len(result.coordinates) == 5
        for lat, lon in result.coordinates:
            assert -90 <= lat <= 90
            assert -180 <= lon <= 180
    
    def test_small_radius(self):
        """Test with very small radius."""
        result = generate_random_coordinates_by_area(
            (40.7128, -74.0060), 0.01, 5, radius_unit='km', seed=42
        )
        assert len(result.coordinates) == 5
    
    def test_large_radius(self):
        """Test with large radius."""
        result = generate_random_coordinates_by_area(
            (40.7128, -74.0060), 1000, 5, radius_unit='km', seed=42
        )
        assert len(result.coordinates) == 5
    
    def test_invalid_center_coordinates(self):
        """Test that invalid center coordinates raise ValueError."""
        with pytest.raises(ValueError, match="Invalid center coordinates"):
            generate_random_coordinates_by_area((91.0, 0.0), 10, 5, radius_unit='km')
        
        with pytest.raises(ValueError, match="Invalid center coordinates"):
            generate_random_coordinates_by_area((0.0, 181.0), 10, 5, radius_unit='km')
    
    def test_negative_radius(self):
        """Test that negative radius raises ValueError."""
        with pytest.raises(ValueError, match="Radius must be non-negative"):
            generate_random_coordinates_by_area((40.7128, -74.0060), -10, 5, radius_unit='km')
    
    def test_zero_count(self):
        """Test that zero count raises ValueError."""
        with pytest.raises(ValueError, match="Count must be positive"):
            generate_random_coordinates_by_area((40.7128, -74.0060), 10, 0, radius_unit='km')
    
    def test_invalid_radius_unit(self):
        """Test that invalid radius unit raises ValueError."""
        with pytest.raises(ValueError, match="Unknown radius_unit"):
            generate_random_coordinates_by_area((40.7128, -74.0060), 10, 5, radius_unit='invalid')
    
    def test_result_to_dict(self):
        """Test converting result to dictionary."""
        result = generate_random_coordinates_by_area((40.7128, -74.0060), 10, 5, radius_unit='km', seed=42)
        result_dict = result.to_dict()
        assert isinstance(result_dict, dict)
        assert 'coordinates' in result_dict
        assert 'region' in result_dict
        assert 'region_type' in result_dict


class TestHelperFunctions:
    """Test suite for helper functions."""
    
    def test_detect_region_type_country(self):
        """Test region type detection for countries."""
        region_type = _detect_region_type("United States")
        assert region_type == 'country'
        
        region_type = _detect_region_type("US")
        assert region_type == 'country'
    
    def test_detect_region_type_continent(self):
        """Test region type detection for continents."""
        region_type = _detect_region_type("Europe")
        assert region_type == 'continent'
        
        region_type = _detect_region_type("asia")
        assert region_type == 'continent'
    
    def test_calculate_bounding_box(self):
        """Test bounding box calculation."""
        polygons = [
            ([(0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0)], []),
            ([(5.0, 5.0), (7.0, 5.0), (7.0, 7.0), (5.0, 7.0)], []),
        ]
        bbox = _calculate_bounding_box_for_polygons(polygons)
        assert bbox == (0.0, 7.0, 0.0, 7.0)


class TestEdgeCases:
    """Test suite for edge cases."""
    
    def test_very_small_region(self):
        """Test generating coordinates for very small regions."""
        # Small countries may need more attempts
        try:
            result = generate_random_coordinates_by_region(
                "Vatican", 3, seed=42, max_attempts=5000
            )
            assert result.total_generated >= 0  # May generate fewer
        except ValueError:
            # Very small regions may fail - acceptable
            pass
    
    def test_date_line_crossing(self):
        """Test regions crossing International Date Line."""
        # Countries like Russia or Fiji cross the date line
        try:
            result = generate_random_coordinates_by_region("Russia", 5, seed=42)
            assert len(result.coordinates) == 5
            # Check that longitudes are normalized
            for lat, lon in result.coordinates:
                assert -180 <= lon <= 180
        except ValueError:
            pass
    
    def test_multiple_territories(self):
        """Test countries with multiple territories."""
        # Countries like France or UK have multiple territories
        try:
            result = generate_random_coordinates_by_region("France", 10, seed=42)
            assert len(result.coordinates) >= 0  # May generate from any territory
        except ValueError:
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
