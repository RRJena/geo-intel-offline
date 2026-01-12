#!/usr/bin/env python3
"""
Verification script to test geo_intel_offline setup.

This script:
1. Generates minimal test data if missing
2. Tests basic resolution functionality
3. Validates data files
"""

import sys
from pathlib import Path

def verify_setup():
    """Verify library setup and test basic functionality."""
    print("=" * 60)
    print("geo_intel_offline - Setup Verification")
    print("=" * 60)
    print()
    
    # Check if data files exist
    data_dir = Path("geo_intel_offline/data")
    required_files = ["geohash_index.json", "polygons.json", "metadata.json"]
    
    missing_files = [f for f in required_files if not (data_dir / f).exists()]
    
    if missing_files:
        print(f"⚠ Data files missing: {', '.join(missing_files)}")
        print("Generating minimal test data...")
        
        try:
            from geo_intel_offline.data_builder_minimal import main as build_minimal
            import sys as _sys
            old_argv = _sys.argv
            _sys.argv = ["data_builder_minimal", str(data_dir)]
            build_minimal()
            _sys.argv = old_argv
            print("✓ Minimal test data generated")
        except Exception as e:
            print(f"✗ Failed to generate test data: {e}")
            print("\nPlease run manually:")
            print(f"  python -m geo_intel_offline.data_builder_minimal {data_dir}")
            return False
    else:
        print("✓ All data files present")
    
    # Test imports
    print("\nTesting imports...")
    try:
        from geo_intel_offline import resolve, GeoIntelResult
        print("✓ Core imports successful")
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False
    
    # Test resolution (if we have test data)
    print("\nTesting resolution...")
    try:
        result = resolve(40.7128, -74.0060)  # NYC
        
        if result.country is not None:
            print(f"✓ Resolution successful")
            print(f"  Country: {result.country}")
            print(f"  ISO2: {result.iso2}")
            print(f"  Confidence: {result.confidence:.2f}")
        else:
            print("⚠ Resolution returned None (may be ocean or outside test data)")
            print("  This is normal if using minimal test data with limited coverage")
    except Exception as e:
        print(f"✗ Resolution failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test geohash module
    print("\nTesting geohash module...")
    try:
        from geo_intel_offline.geohash import encode, decode
        
        geohash = encode(40.7128, -74.0060)
        lat, lon, _, _ = decode(geohash)
        
        print(f"✓ Geohash encode/decode working")
        print(f"  Encoded: {geohash}")
        print(f"  Decoded: ({lat:.4f}, {lon:.4f})")
    except Exception as e:
        print(f"✗ Geohash test failed: {e}")
        return False
    
    # Test PIP module
    print("\nTesting point-in-polygon module...")
    try:
        from geo_intel_offline.pip import point_in_polygon
        
        # Simple square
        polygon = [(0, 0), (2, 0), (2, 2), (0, 2)]
        
        assert point_in_polygon((1, 1), polygon) == True
        assert point_in_polygon((3, 3), polygon) == False
        
        print("✓ Point-in-polygon working")
    except Exception as e:
        print(f"✗ PIP test failed: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✓ All verification tests passed!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. For production: Generate full data using data_builder.py")
    print("  2. See QUICKSTART.md for usage examples")
    print("  3. See ARCHITECTURE.md for design details")
    
    return True


if __name__ == '__main__':
    success = verify_setup()
    sys.exit(0 if success else 1)
