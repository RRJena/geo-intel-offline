#!/usr/bin/env python3
"""
Quick test script for validating the library with known locations.

Tests a curated list of locations across all continents.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from geo_intel_offline import resolve


# Comprehensive test locations: (lat, lon, name, expected_country, expected_iso2)
TEST_LOCATIONS = [
    # North America
    (40.7128, -74.0060, "New York, USA", "United States", "US"),
    (34.0522, -118.2437, "Los Angeles, USA", "United States", "US"),
    (43.6532, -79.3832, "Toronto, Canada", "Canada", "CA"),
    (19.4326, -99.1332, "Mexico City, Mexico", "Mexico", "MX"),
    
    # South America
    (-23.5505, -46.6333, "São Paulo, Brazil", "Brazil", "BR"),
    (-34.6037, -58.3816, "Buenos Aires, Argentina", "Argentina", "AR"),
    
    # Europe
    (51.5074, -0.1278, "London, UK", "United Kingdom", "GB"),
    (48.8566, 2.3522, "Paris, France", "France", "FR"),
    (52.5200, 13.4050, "Berlin, Germany", "Germany", "DE"),
    (41.9028, 12.4964, "Rome, Italy", "Italy", "IT"),
    (40.4168, -3.7038, "Madrid, Spain", "Spain", "ES"),
    (55.7558, 37.6173, "Moscow, Russia", "Russia", "RU"),
    
    # Asia
    (35.6762, 139.6503, "Tokyo, Japan", "Japan", "JP"),
    (39.9042, 116.4074, "Beijing, China", "China", "CN"),
    (28.6139, 77.2090, "New Delhi, India", "India", "IN"),
    (1.3521, 103.8198, "Singapore", "Singapore", "SG"),
    (37.5665, 126.9780, "Seoul, South Korea", "South Korea", "KR"),
    
    # Middle East
    (24.7136, 46.6753, "Riyadh, Saudi Arabia", "Saudi Arabia", "SA"),
    (31.7683, 35.2137, "Jerusalem, Israel", "Israel", "IL"),
    
    # Africa
    (-25.7461, 28.1881, "Pretoria, South Africa", "South Africa", "ZA"),
    (30.0444, 31.2357, "Cairo, Egypt", "Egypt", "EG"),
    (9.0765, 7.3986, "Abuja, Nigeria", "Nigeria", "NG"),
    
    # Oceania
    (-33.8688, 151.2093, "Sydney, Australia", "Australia", "AU"),
    (-41.2865, 174.7762, "Wellington, New Zealand", "New Zealand", "NZ"),
]


def test_location(lat, lon, name, expected_country, expected_iso2):
    """Test a single location."""
    try:
        result = resolve(lat, lon)
        
        if result.country is None:
            return False, f"No result", None
        
        # Flexible matching (case-insensitive, partial)
        country_match = (
            expected_country.lower() in result.country.lower() or
            result.country.lower() in expected_country.lower() or
            result.iso2 == expected_iso2
        )
        
        iso_match = result.iso2 == expected_iso2
        
        if country_match and iso_match:
            return True, f"{result.country} ({result.iso2})", result.confidence
        elif country_match or iso_match:
            return True, f"{result.country} ({result.iso2}) [partial]", result.confidence
        else:
            return False, f"{result.country} ({result.iso2})", result.confidence
    
    except Exception as e:
        return False, f"Error: {e}", None


def main():
    """Run quick test suite."""
    print("=" * 70)
    print("Quick Test Suite - Worldwide Locations")
    print("=" * 70)
    print()
    
    print(f"{'Location':<35} {'Expected':<25} {'Result':<30} {'Status'}")
    print("-" * 100)
    
    passed = 0
    failed = 0
    skipped = 0
    
    for lat, lon, name, expected_country, expected_iso2 in TEST_LOCATIONS:
        success, result_str, confidence = test_location(lat, lon, name, expected_country, expected_iso2)
        
        if result_str.startswith("No result"):
            status = "SKIP"
            skipped += 1
            symbol = "⚠"
        elif success:
            status = "PASS"
            passed += 1
            symbol = "✓"
        else:
            status = "FAIL"
            failed += 1
            symbol = "✗"
        
        conf_str = f"conf={confidence:.2f}" if confidence else ""
        print(f"{symbol} {name:<33} {expected_country:<23} {result_str:<28} {status} {conf_str}")
    
    print()
    print("=" * 70)
    print(f"Results: {passed} passed, {failed} failed, {skipped} skipped")
    print("=" * 70)
    
    if skipped > len(TEST_LOCATIONS) * 0.5:
        print("\n⚠ Warning: More than 50% of tests skipped.")
        print("  This likely means you're using minimal test data.")
        print("  For comprehensive testing, run:")
        print("    python3 scripts/prepare_full_data.py")
    
    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
