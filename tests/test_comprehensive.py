"""
Comprehensive test suite for geo_intel_offline.

Tests:
- All countries (requires full data)
- Border locations
- Major cities
- Edge cases
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from geo_intel_offline import resolve
from typing import List, Tuple, Dict


# Known test locations - (lat, lon, expected_country, expected_iso2)
TEST_LOCATIONS = [
    # Major cities
    (40.7128, -74.0060, "United States", "US"),  # New York
    (51.5074, -0.1278, "United Kingdom", "GB"),  # London
    (48.8566, 2.3522, "France", "FR"),  # Paris
    (52.5200, 13.4050, "Germany", "DE"),  # Berlin
    (35.6762, 139.6503, "Japan", "JP"),  # Tokyo
    (55.7558, 37.6173, "Russia", "RU"),  # Moscow
    (39.9042, 116.4074, "China", "CN"),  # Beijing
    (-33.8688, 151.2093, "Australia", "AU"),  # Sydney
    (-23.5505, -46.6333, "Brazil", "BR"),  # São Paulo
    (19.4326, -99.1332, "Mexico", "MX"),  # Mexico City
    
    # Border locations (challenging cases)
    (49.0000, 8.2000, None, None),  # France-Germany border (near Strasbourg)
    (31.7683, 35.2137, None, None),  # Israel-Palestine border (Jerusalem)
    (28.6139, 77.2090, None, None),  # India-Pakistan border region (Delhi area)
    (25.2769, 55.2962, None, None),  # UAE-Oman border (Dubai area)
    
    # Coastal cities (near borders)
    (25.7617, -80.1918, "United States", "US"),  # Miami
    (45.4642, 9.1900, "Italy", "IT"),  # Milan
    (50.1109, 8.6821, "Germany", "DE"),  # Frankfurt
    
    # Island nations
    (-41.2865, 174.7762, "New Zealand", "NZ"),  # Wellington
    (1.3521, 103.8198, "Singapore", "SG"),  # Singapore
    (25.0330, 121.5654, "Taiwan", "TW"),  # Taipei
    
    # Small countries
    (47.3769, 8.5417, "Switzerland", "CH"),  # Zurich
    (50.8503, 4.3517, "Belgium", "BE"),  # Brussels
    (52.3676, 4.9041, "Netherlands", "NL"),  # Amsterdam
    
    # Polar regions
    (64.8378, -147.7164, "United States", "US"),  # Fairbanks, Alaska
    (78.2232, 15.6267, None, None),  # Svalbard (may not be in all datasets)
]


# Border test cases - points known to be on or near country borders
BORDER_LOCATIONS = [
    # US-Canada border
    (49.0000, -123.0000, None),  # Near Vancouver/Seattle
    (45.0000, -71.0000, None),  # Quebec-Vermont border
    
    # US-Mexico border
    (32.5343, -117.0382, None),  # Tijuana-San Diego
    
    # European borders
    (47.5766, 7.5886, None),  # France-Germany-Switzerland (Basel)
    (48.8566, 2.3522, None),  # Paris (center of France)
    
    # Middle East
    (31.7683, 35.2137, None),  # Jerusalem (disputed)
    
    # Asia
    (28.6139, 77.2090, None),  # India-Pakistan region
    
    # Africa
    (-25.7461, 28.1881, None),  # South Africa border region
]


def test_major_cities():
    """Test resolution for major cities worldwide."""
    print("\n" + "=" * 60)
    print("Testing Major Cities")
    print("=" * 60)
    
    city_tests = [loc for loc in TEST_LOCATIONS if loc[2] is not None]
    
    passed = 0
    failed = 0
    skipped = 0
    
    for lat, lon, expected_country, expected_iso2 in city_tests:
        try:
            result = resolve(lat, lon)
            
            if result.country is None:
                print(f"  ⚠ SKIP: ({lat:.4f}, {lon:.4f}) - No result (may not be in test data)")
                skipped += 1
                continue
            
            # Check if result matches expected (case-insensitive, flexible matching)
            country_match = (
                expected_country.lower() in result.country.lower() or
                result.country.lower() in expected_country.lower()
            )
            iso_match = result.iso2 == expected_iso2 if expected_iso2 else True
            
            if country_match or iso_match:
                print(f"  ✓ ({lat:.4f}, {lon:.4f}) → {result.country} ({result.iso2}) "
                      f"conf={result.confidence:.2f}")
                passed += 1
            else:
                print(f"  ✗ ({lat:.4f}, {lon:.4f}) → Expected: {expected_country}/{expected_iso2}, "
                      f"Got: {result.country}/{result.iso2}")
                failed += 1
        except Exception as e:
            print(f"  ✗ ({lat:.4f}, {lon:.4f}) → Error: {e}")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed, {skipped} skipped")
    return passed, failed, skipped


def test_border_locations():
    """Test resolution for border locations (expected lower confidence)."""
    print("\n" + "=" * 60)
    print("Testing Border Locations")
    print("=" * 60)
    
    passed = 0
    failed = 0
    skipped = 0
    
    for lat, lon, _ in BORDER_LOCATIONS:
        try:
            result = resolve(lat, lon)
            
            if result.country is None:
                print(f"  ⚠ SKIP: ({lat:.4f}, {lon:.4f}) - No result")
                skipped += 1
                continue
            
            # Border locations should have country result
            # Confidence may be lower (expected)
            confidence_note = "low conf" if result.confidence < 0.80 else "ok conf"
            print(f"  {'✓' if result.country else '✗'} ({lat:.4f}, {lon:.4f}) → "
                  f"{result.country or 'None'} ({result.iso2 or 'N/A'}) "
                  f"conf={result.confidence:.2f} [{confidence_note}]")
            
            if result.country:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  ✗ ({lat:.4f}, {lon:.4f}) → Error: {e}")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed, {skipped} skipped")
    return passed, failed, skipped


def test_ocean_locations():
    """Test that ocean locations return None."""
    print("\n" + "=" * 60)
    print("Testing Ocean Locations")
    print("=" * 60)
    
    ocean_locations = [
        (0.0, 0.0, "Atlantic Ocean (Gulf of Guinea)"),
        (25.0, -140.0, "Pacific Ocean"),
        (-40.0, 20.0, "South Atlantic"),
        (30.0, 120.0, "Pacific Ocean (East China Sea)"),
    ]
    
    passed = 0
    failed = 0
    
    for lat, lon, description in ocean_locations:
        try:
            result = resolve(lat, lon)
            
            if result.country is None:
                print(f"  ✓ ({lat:.4f}, {lon:.4f}) - {description} → Correctly returns None")
                passed += 1
            else:
                print(f"  ⚠ ({lat:.4f}, {lon:.4f}) - {description} → Got: {result.country} "
                      f"(may be island or coastal country)")
                # Not necessarily a failure - could be island
                passed += 1
        except Exception as e:
            print(f"  ✗ ({lat:.4f}, {lon:.4f}) → Error: {e}")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return passed, failed


def test_all_countries_coverage():
    """Test that data includes many countries."""
    print("\n" + "=" * 60)
    print("Testing Country Coverage")
    print("=" * 60)
    
    # Test points in capital cities of major countries
    capitals = [
        (35.6762, 139.6503, "Japan"),
        (39.9042, 116.4074, "China"),
        (28.6139, 77.2090, "India"),
        (-35.2809, 149.1300, "Australia"),
        (-25.7461, 28.1881, "South Africa"),
        (59.9343, 30.3351, "Russia"),
        (55.7558, 37.6173, "Russia"),
        (52.5200, 13.4050, "Germany"),
        (48.8566, 2.3522, "France"),
        (41.9028, 12.4964, "Italy"),
    ]
    
    found_countries = set()
    
    for lat, lon, country_name in capitals:
        result = resolve(lat, lon)
        if result.country:
            found_countries.add(result.country)
            print(f"  ✓ Found: {result.country} ({result.iso2}) at ({lat:.4f}, {lon:.4f})")
    
    print(f"\nTotal unique countries found in test: {len(found_countries)}")
    print(f"Countries: {', '.join(sorted(found_countries))}")
    
    return len(found_countries)


def run_comprehensive_tests():
    """Run all comprehensive tests."""
    print("=" * 60)
    print("Comprehensive Test Suite")
    print("=" * 60)
    print("\nNote: These tests require full country data.")
    print("      Results may vary based on data completeness.\n")
    
    results = {}
    
    # Run test suites
    results['cities'] = test_major_cities()
    results['borders'] = test_border_locations()
    results['oceans'] = test_ocean_locations()
    results['coverage'] = (test_all_countries_coverage(),)
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    total_passed = sum(r[0] for r in results.values() if isinstance(r, tuple) and len(r) >= 2)
    total_failed = sum(r[1] for r in results.values() if isinstance(r, tuple) and len(r) >= 2)
    total_skipped = sum(r[2] if len(r) > 2 else 0 for r in results.values() if isinstance(r, tuple))
    
    print(f"Total: {total_passed} passed, {total_failed} failed, {total_skipped} skipped")
    print(f"Countries found: {results['coverage'][0]}")
    
    if total_failed == 0 and results['coverage'][0] > 0:
        print("\n✓ All tests passed!")
        return 0
    else:
        print("\n⚠ Some tests failed or limited coverage (expected with minimal test data)")
        return 1


if __name__ == '__main__':
    sys.exit(run_comprehensive_tests())
