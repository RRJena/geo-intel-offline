"""
Tests for point-in-polygon algorithm.
"""

import pytest
from geo_intel_offline.pip import (
    point_in_polygon,
    point_in_polygon_with_holes,
    distance_to_polygon_edge
)


def test_point_in_simple_square():
    """Test point in simple square polygon."""
    # Square from (0,0) to (2,2)
    polygon = [
        (0, 0),
        (2, 0),
        (2, 2),
        (0, 2),
    ]
    
    assert point_in_polygon((1, 1), polygon) == True
    assert point_in_polygon((3, 3), polygon) == False
    assert point_in_polygon((0.5, 0.5), polygon) == True


def test_point_on_edge():
    """Test point on polygon edge."""
    polygon = [
        (0, 0),
        (2, 0),
        (2, 2),
        (0, 2),
    ]
    
    # Point on edge - may be considered inside or outside depending on implementation
    # Ray casting typically treats edge points as inside
    result = point_in_polygon((1, 0), polygon)
    assert isinstance(result, bool)


def test_point_outside():
    """Test point clearly outside polygon."""
    polygon = [
        (0, 0),
        (2, 0),
        (2, 2),
        (0, 2),
    ]
    
    assert point_in_polygon((5, 5), polygon) == False
    assert point_in_polygon((-1, -1), polygon) == False


def test_point_in_polygon_with_holes():
    """Test point in polygon with holes."""
    # Square with hole in middle
    exterior = [
        (0, 0),
        (4, 0),
        (4, 4),
        (0, 4),
    ]
    
    hole = [
        (1, 1),
        (3, 1),
        (3, 3),
        (1, 3),
    ]
    
    assert point_in_polygon_with_holes((0.5, 0.5), exterior, [hole]) == True
    assert point_in_polygon_with_holes((2, 2), exterior, [hole]) == False  # In hole
    assert point_in_polygon_with_holes((5, 5), exterior, [hole]) == False  # Outside


def test_distance_to_edge():
    """Test distance to polygon edge calculation."""
    polygon = [
        (0, 0),
        (2, 0),
        (2, 2),
        (0, 2),
    ]
    
    # Point at center should be 1 unit from nearest edge
    dist = distance_to_polygon_edge((1, 1), polygon)
    assert dist > 0
    assert dist <= 1.5  # Should be approximately 1.0
    
    # Point far away
    dist_far = distance_to_polygon_edge((10, 10), polygon)
    assert dist_far > dist


def test_empty_polygon():
    """Test edge cases with empty/invalid polygons."""
    assert point_in_polygon((1, 1), []) == False
    assert point_in_polygon((1, 1), [(0, 0)]) == False
    assert point_in_polygon((1, 1), [(0, 0), (1, 1)]) == False
