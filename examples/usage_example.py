"""
Example usage of geo_intel_offline library.

Demonstrates basic usage, edge cases, and performance characteristics.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from geo_intel_offline import resolve


def main():
    """Run example usage scenarios."""
    
    print("=" * 60)
    print("geo_intel_offline - Example Usage")
    print("=" * 60)
    print()
    
    # Example 1: Major city (high confidence)
    print("Example 1: New York City (high confidence expected)")
    result = resolve(40.7128, -74.0060)
    print(f"  Country: {result.country}")
    print(f"  ISO2: {result.iso2}")
    print(f"  ISO3: {result.iso3}")
    print(f"  Continent: {result.continent}")
    print(f"  Timezone: {result.timezone}")
    print(f"  Confidence: {result.confidence:.2f}")
    print()
    
    # Example 2: European city
    print("Example 2: London, UK")
    result = resolve(51.5074, -0.1278)
    print(f"  Country: {result.country}")
    print(f"  ISO2: {result.iso2}")
    print(f"  Confidence: {result.confidence:.2f}")
    print()
    
    # Example 3: Asian city
    print("Example 3: Tokyo, Japan")
    result = resolve(35.6762, 139.6503)
    print(f"  Country: {result.country}")
    print(f"  ISO2: {result.iso2}")
    print(f"  Confidence: {result.confidence:.2f}")
    print()
    
    # Example 4: Border region (may have lower confidence)
    print("Example 4: Near border (lower confidence expected)")
    result = resolve(49.0000, 8.2000)  # Near France-Germany border
    print(f"  Country: {result.country}")
    print(f"  ISO2: {result.iso2}")
    print(f"  Confidence: {result.confidence:.2f}")
    print()
    
    # Example 5: Dictionary access
    print("Example 5: Dictionary access")
    result = resolve(37.7749, -122.4194)  # San Francisco
    result_dict = result.to_dict()
    print(f"  Result as dict: {result_dict}")
    print()
    
    # Performance test
    print("=" * 60)
    print("Performance Test: 1000 lookups")
    print("=" * 60)
    
    import time
    
    test_points = [
        (40.7128, -74.0060),   # NYC
        (51.5074, -0.1278),    # London
        (35.6762, 139.6503),   # Tokyo
        (48.8566, 2.3522),     # Paris
        (-33.8688, 151.2093),  # Sydney
        (55.7558, 37.6173),    # Moscow
        (19.4326, -99.1332),   # Mexico City
        (30.0444, 31.2357),    # Cairo
        (39.9042, 116.4074),   # Beijing
        (-23.5505, -46.6333),  # São Paulo
    ]
    
    start = time.perf_counter()
    for _ in range(100):
        for lat, lon in test_points:
            resolve(lat, lon)
    end = time.perf_counter()
    
    total_time = end - start
    avg_time = (total_time / (100 * len(test_points))) * 1000  # ms
    
    print(f"  Total time: {total_time:.3f}s")
    print(f"  Average per lookup: {avg_time:.3f}ms")
    print(f"  Target: < 1ms per lookup")
    print(f"  Status: {'✓ PASS' if avg_time < 1.0 else '✗ FAIL'}")
    print()


if __name__ == '__main__':
    main()
