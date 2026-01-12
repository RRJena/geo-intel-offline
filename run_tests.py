#!/usr/bin/env python3
"""
Simple test runner (doesn't require pytest).
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def run_geohash_tests():
    """Run geohash tests."""
    print("Testing geohash module...")
    from geo_intel_offline.geohash import encode, decode, get_neighbors
    
    # Test encoding
    geohash = encode(40.7128, -74.0060)
    assert isinstance(geohash, str)
    assert len(geohash) == 6
    print("  ✓ Encoding works")
    
    # Test decoding
    lat, lon, lat_range, lon_range = decode(geohash)
    assert -90 <= lat <= 90
    assert -180 <= lon <= 180
    print("  ✓ Decoding works")
    
    # Test neighbors
    neighbors = get_neighbors(geohash)
    assert len(neighbors) == 8
    print("  ✓ Neighbor generation works")
    
    return True

def run_pip_tests():
    """Run point-in-polygon tests."""
    print("Testing point-in-polygon module...")
    from geo_intel_offline.pip import point_in_polygon, point_in_polygon_with_holes
    
    # Simple square
    polygon = [(0, 0), (2, 0), (2, 2), (0, 2)]
    
    assert point_in_polygon((1, 1), polygon) == True
    assert point_in_polygon((3, 3), polygon) == False
    print("  ✓ Basic PIP works")
    
    # With holes
    exterior = [(0, 0), (4, 0), (4, 4), (0, 4)]
    hole = [(1, 1), (3, 1), (3, 3), (1, 3)]
    
    assert point_in_polygon_with_holes((0.5, 0.5), exterior, [hole]) == True
    assert point_in_polygon_with_holes((2, 2), exterior, [hole]) == False
    print("  ✓ PIP with holes works")
    
    return True

def run_resolution_tests():
    """Run resolution tests."""
    print("Testing resolution pipeline...")
    from geo_intel_offline import resolve
    
    # Test resolution
    result = resolve(40.7128, -74.0060)
    assert result is not None
    print(f"  ✓ Resolution works (got: {result.country})")
    
    # Test dictionary access
    result_dict = result.to_dict()
    assert isinstance(result_dict, dict)
    assert 'country' in result_dict
    print("  ✓ Dictionary access works")
    
    return True

def main():
    """Run all tests."""
    print("=" * 60)
    print("Running Tests")
    print("=" * 60)
    print()
    
    tests = [
        ("Geohash", run_geohash_tests),
        ("Point-in-Polygon", run_pip_tests),
        ("Resolution", run_resolution_tests),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            print(f"\n[{name}]")
            test_func()
            passed += 1
        except Exception as e:
            print(f"  ✗ FAILED: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print()
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return 0 if failed == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
