#!/usr/bin/env python3
"""
Prepare full country data from Natural Earth for comprehensive testing.

This script:
1. Downloads Natural Earth data (if not present)
2. Builds full data files
3. Validates the generated data
"""

import sys
import subprocess
from pathlib import Path
import json


def check_data_exists(data_path: Path) -> bool:
    """Check if Natural Earth data exists."""
    geojson_path = data_path / "ne_10m_admin_0_countries.geojson"
    shapefile_path = data_path / "ne_10m_admin_0_countries.shp"
    return geojson_path.exists() or shapefile_path.exists()


def find_geojson_file(data_dir: Path) -> Path:
    """Find GeoJSON file in data directory."""
    # Try GeoJSON first
    geojson_path = data_dir / "ne_10m_admin_0_countries.geojson"
    if geojson_path.exists():
        return geojson_path
    
    # Try other possible names
    for path in data_dir.glob("*.geojson"):
        return path
    
    raise FileNotFoundError(
        f"No GeoJSON file found in {data_dir}. "
        "Please download Natural Earth data first."
    )


def validate_generated_data(data_dir: Path) -> dict:
    """Validate generated data files (including compressed versions)."""
    print("\nValidating generated data...")
    
    results = {
        'geohash_index': False,
        'polygons': False,
        'metadata': False,
        'compressed_files': False,
        'country_count': 0,
        'geohash_count': 0,
        'total_original_size': 0,
        'total_compressed_size': 0,
    }
    
    import gzip
    
    # Check geohash_index.json (try compressed first, then uncompressed)
    index_path = data_dir / "geohash_index.json"
    index_gzip_path = data_dir / "geohash_index.json.gz"
    
    if index_gzip_path.exists():
        with gzip.open(index_gzip_path, 'rt', encoding='utf-8') as f:
            index = json.load(f)
        results['compressed_files'] = True
        results['total_compressed_size'] += index_gzip_path.stat().st_size
    elif index_path.exists():
        with open(index_path, 'r') as f:
            index = json.load(f)
        results['total_original_size'] += index_path.stat().st_size
    
    if index_path.exists() or index_gzip_path.exists():
        results['geohash_index'] = True
        results['geohash_count'] = len(index)
        if index_path.exists():
            results['total_original_size'] += index_path.stat().st_size
        print(f"  ✓ Geohash index: {len(index):,} entries")
    
    # Check polygons.json
    polygons_path = data_dir / "polygons.json"
    polygons_gzip_path = data_dir / "polygons.json.gz"
    
    if polygons_gzip_path.exists():
        with gzip.open(polygons_gzip_path, 'rt', encoding='utf-8') as f:
            polygons = json.load(f)
        results['compressed_files'] = True
        results['total_compressed_size'] += polygons_gzip_path.stat().st_size
    elif polygons_path.exists():
        with open(polygons_path, 'r') as f:
            polygons = json.load(f)
        results['total_original_size'] += polygons_path.stat().st_size
    
    if polygons_path.exists() or polygons_gzip_path.exists():
        results['polygons'] = True
        results['country_count'] = len(polygons)
        if polygons_path.exists():
            results['total_original_size'] += polygons_path.stat().st_size
        print(f"  ✓ Polygons: {len(polygons)} countries")
    
    # Check metadata.json
    metadata_path = data_dir / "metadata.json"
    metadata_gzip_path = data_dir / "metadata.json.gz"
    
    if metadata_gzip_path.exists():
        with gzip.open(metadata_gzip_path, 'rt', encoding='utf-8') as f:
            metadata = json.load(f)
        results['compressed_files'] = True
        results['total_compressed_size'] += metadata_gzip_path.stat().st_size
    elif metadata_path.exists():
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        results['total_original_size'] += metadata_path.stat().st_size
    
    if metadata_path.exists() or metadata_gzip_path.exists():
        results['metadata'] = True
        if metadata_path.exists():
            results['total_original_size'] += metadata_path.stat().st_size
        print(f"  ✓ Metadata: {len(metadata)} countries")
    
    # Show compression info
    if results['compressed_files']:
        compression_ratio = (results['total_compressed_size'] / results['total_original_size']) * 100 if results['total_original_size'] > 0 else 0
        space_saved = (1 - results['total_compressed_size'] / results['total_original_size']) * 100 if results['total_original_size'] > 0 else 0
        print(f"  ✓ Compressed files: {results['total_original_size']/1024/1024:.2f} MB -> {results['total_compressed_size']/1024/1024:.2f} MB (saved {space_saved:.1f}%)")
    
    return results


def main():
    """Main entry point."""
    print("=" * 60)
    print("Prepare Full Country Data")
    print("=" * 60)
    print()
    
    # Paths
    project_root = Path(__file__).parent.parent
    data_sources_dir = project_root / "data_sources"
    output_dir = project_root / "geo_intel_offline" / "data"
    
    # Step 1: Check for Natural Earth data
    print("Step 1: Checking for Natural Earth data...")
    if not check_data_exists(data_sources_dir):
        print(f"  ⚠ Natural Earth data not found in {data_sources_dir}")
        print("  Run: bash scripts/download_natural_earth.sh")
        print("  Or download manually from:")
        print("  https://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-admin-0-countries/")
        return 1
    
    # Step 2: Find GeoJSON file
    try:
        geojson_path = find_geojson_file(data_sources_dir)
        print(f"  ✓ Found: {geojson_path}")
    except FileNotFoundError as e:
        print(f"  ✗ {e}")
        return 1
    
    # Step 3: Build data files
    print(f"\nStep 2: Building data files...")
    print(f"  Input: {geojson_path}")
    print(f"  Output: {output_dir}")
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        import subprocess
        result = subprocess.run(
            [
                sys.executable, "-m", "geo_intel_offline.data_builder",
                str(geojson_path),
                str(output_dir)
            ],
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.stderr:
            print("Warnings:", result.stderr)
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Failed to build data files:")
        print(e.stdout)
        print(e.stderr)
        return 1
    
    # Step 4: Validate
    validation = validate_generated_data(output_dir)
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Countries: {validation['country_count']}")
    print(f"Geohashes: {validation['geohash_count']:,}")
    print(f"Status: {'✓ Ready' if all([validation['geohash_index'], validation['polygons'], validation['metadata']]) else '✗ Incomplete'}")
    
    if validation['country_count'] > 100:
        print("\n✓ Full country data ready for comprehensive testing!")
        print("\nNext steps:")
        print("  python3 tests/test_comprehensive.py")
    else:
        print("\n⚠ Limited country coverage. Check data source.")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
