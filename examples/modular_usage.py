"""
Example usage of modular data loading.

Demonstrates:
- Loading specific countries
- Loading by continent
- Excluding countries
- Memory efficiency
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from geo_intel_offline import resolve
from geo_intel_offline.modular_data_loader import ModularDataLoader


def example_load_specific_countries():
    """Example: Load only specific countries."""
    print("=" * 60)
    print("Example 1: Load Specific Countries")
    print("=" * 60)
    
    # Load only US, Canada, and Mexico
    result = resolve(
        40.7128, -74.0060,  # New York
        countries=["US", "CA", "MX"]
    )
    
    print(f"New York: {result.country} ({result.iso2})")
    print(f"Loaded countries: US, CA, MX")
    print()


def example_load_by_continent():
    """Example: Load entire continent."""
    print("=" * 60)
    print("Example 2: Load by Continent")
    print("=" * 60)
    
    # Load all North American countries
    result = resolve(
        40.7128, -74.0060,  # New York
        continents=["North America"]
    )
    
    print(f"New York: {result.country} ({result.iso2})")
    print(f"Loaded continent: North America")
    print()


def example_exclude_countries():
    """Example: Load all except specific countries."""
    print("=" * 60)
    print("Example 3: Exclude Countries")
    print("=" * 60)
    
    # Load all countries except Russia and China
    result = resolve(
        40.7128, -74.0060,  # New York
        exclude_countries=["RU", "CN"]
    )
    
    print(f"New York: {result.country} ({result.iso2})")
    print(f"Excluded: RU, CN")
    print()


def example_memory_efficiency():
    """Example: Check memory efficiency."""
    print("=" * 60)
    print("Example 4: Memory Efficiency")
    print("=" * 60)
    
    # Loader with only North America
    loader_na = ModularDataLoader(continents=["North America"])
    print(f"Countries loaded (North America): {loader_na.get_loaded_count()}")
    
    # Loader with all countries
    loader_all = ModularDataLoader()
    print(f"Countries loaded (All): {loader_all.get_loaded_count()}")
    print()


def example_loader_reuse():
    """Example: Reuse loader instance for multiple lookups."""
    print("=" * 60)
    print("Example 5: Reuse Loader Instance")
    print("=" * 60)
    
    # Create loader once (loads data)
    loader = ModularDataLoader(continents=["Europe"])
    
    # Reuse for multiple lookups (data already loaded)
    locations = [
        (51.5074, -0.1278, "London"),
        (48.8566, 2.3522, "Paris"),
        (52.5200, 13.4050, "Berlin"),
    ]
    
    for lat, lon, name in locations:
        result = resolve(lat, lon, loader=loader)
        print(f"{name}: {result.country} ({result.iso2})")
    print()


def main():
    """Run all examples."""
    print("\nModular Data Loading Examples\n")
    
    try:
        example_load_specific_countries()
        example_load_by_continent()
        example_exclude_countries()
        example_memory_efficiency()
        example_loader_reuse()
    except FileNotFoundError as e:
        print(f"\n⚠ Error: {e}")
        print("\nNote: Modular data format not found.")
        print("To use modular data loading, build modular format:")
        print("  python3 -m geo_intel_offline.data_builder_modular source.geojson output/")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
