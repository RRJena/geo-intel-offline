"""
Tests for geohash encoding/decoding.
"""

import pytest
from geo_intel_offline.geohash import encode, decode, get_neighbors


def test_encode_basic():
    """Test basic geohash encoding."""
    # New York City
    geohash = encode(40.7128, -74.0060)
    assert isinstance(geohash, str)
    assert len(geohash) == 6  # Default precision


def test_encode_precision():
    """Test encoding with different precision."""
    geohash_short = encode(40.7128, -74.0060, precision=3)
    geohash_long = encode(40.7128, -74.0060, precision=9)
    
    assert len(geohash_short) == 3
    assert len(geohash_long) == 9


def test_encode_validation():
    """Test input validation."""
    with pytest.raises(ValueError):
        encode(91, 0)  # Invalid latitude
    
    with pytest.raises(ValueError):
        encode(0, 181)  # Invalid longitude


def test_decode_basic():
    """Test basic geohash decoding."""
    geohash = "dr5reg"
    lat, lon, lat_range, lon_range = decode(geohash)
    
    assert -90 <= lat <= 90
    assert -180 <= lon <= 180
    assert lat_range[0] <= lat <= lat_range[1]
    assert lon_range[0] <= lon <= lon_range[1]


def test_encode_decode_roundtrip():
    """Test that encode/decode is consistent."""
    original_lat, original_lon = 40.7128, -74.0060
    geohash = encode(original_lat, original_lon)
    lat, lon, lat_range, lon_range = decode(geohash)
    
    # Check that decoded point is within geohash bounding box
    assert lat_range[0] <= original_lat <= lat_range[1]
    assert lon_range[0] <= original_lon <= lon_range[1]


def test_get_neighbors():
    """Test neighbor geohash generation."""
    geohash = "dr5reg"
    neighbors = get_neighbors(geohash)
    
    assert len(neighbors) == 8
    assert all(isinstance(n, str) for n in neighbors)
    assert all(len(n) == len(geohash) for n in neighbors)
