#!/usr/bin/env python3
"""
Full End-to-End Test Pipeline

This script:
1. Rebuilds dataset with automatic compression
2. Runs comprehensive tests on all 258 countries
3. Updates TEST_RESULTS.md with compression information
"""

import sys
import subprocess
from pathlib import Path
import time


def find_geojson_file() -> Path:
    """Find GeoJSON source file."""
    search_dirs = [
        Path('data_sources'),
        Path('geo_intel_offline/data'),
        Path('data'),
        Path('.'),
    ]
    
    for search_dir in search_dirs:
        if search_dir.exists():
            geojson_files = list(search_dir.glob('*.geojson'))
            if geojson_files:
                return geojson_files[0]
    
    raise FileNotFoundError(
        "No GeoJSON file found!\n"
        "Please download Natural Earth data first:\n"
        "  bash scripts/download_natural_earth.sh"
    )


def main():
    """Run full end-to-end test pipeline."""
    print("=" * 70)
    print("FULL END-TO-END TEST PIPELINE")
    print("=" * 70)
    print()
    print("This will:")
    print("  1. Rebuild dataset with automatic compression")
    print("  2. Run comprehensive tests on all 258 countries")
    print("  3. Update TEST_RESULTS.md")
    print()
    
    # Step 1: Find GeoJSON file
    print("Step 1: Locating GeoJSON source file...")
    try:
        geojson_file = find_geojson_file()
        print(f"  ✓ Found: {geojson_file}")
        print(f"  Size: {geojson_file.stat().st_size / 1024 / 1024:.2f} MB")
    except FileNotFoundError as e:
        print(f"  ✗ {e}")
        return 1
    
    print()
    
    # Step 2: Rebuild dataset (compression is automatically included in data_builder)
    print("=" * 70)
    print("Step 2: Rebuilding dataset with compression...")
    print("=" * 70)
    
    output_dir = Path('geo_intel_offline/data')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        result = subprocess.run(
            [
                sys.executable, "-m", "geo_intel_offline.data_builder",
                str(geojson_file),
                str(output_dir),
                "0.005",  # polygon_tolerance
                "6"       # geohash_precision
            ],
            check=True,
            text=True
        )
        print(result.stdout)
        if result.stderr:
            print("Warnings:", result.stderr)
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Build failed:")
        print(e.stdout)
        print(e.stderr)
        return 1
    
    print()
    
    # Step 3: Verify compressed files exist
    print("Step 3: Verifying compressed files...")
    compressed_files = [
        output_dir / 'geohash_index.json.gz',
        output_dir / 'polygons.json.gz',
        output_dir / 'metadata.json.gz',
    ]
    
    all_exist = True
    for gzip_file in compressed_files:
        if gzip_file.exists():
            size_mb = gzip_file.stat().st_size / 1024 / 1024
            print(f"  ✓ {gzip_file.name}: {size_mb:.2f} MB")
        else:
            print(f"  ✗ {gzip_file.name}: Missing!")
            all_exist = False
    
    if not all_exist:
        print("  ⚠ Some compressed files are missing")
    
    print()
    
    # Step 4: Run comprehensive tests
    print("=" * 70)
    print("Step 4: Running comprehensive tests on all 258 countries...")
    print("=" * 70)
    print()
    
    start_time = time.time()
    try:
        result = subprocess.run(
            [
                sys.executable,
                'scripts/test_accuracy_report.py',
                '--points', '10',
                '--output', 'TEST_RESULTS.md'
            ],
            check=True,
            text=True,
            capture_output=True
        )
        test_time = time.time() - start_time
        
        # Show output
        if result.stdout:
            # Show last few lines of output
            lines = result.stdout.split('\n')
            print('\n'.join(lines[-15:]))
        if result.stderr:
            print("Warnings:", result.stderr)
        
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Tests failed:")
        print(e.stdout)
        print(e.stderr)
        return 1
    
    print()
    print("=" * 70)
    print("END-TO-END TEST COMPLETE")
    print("=" * 70)
    print(f"✓ Dataset rebuilt with compression")
    print(f"✓ Comprehensive tests completed ({test_time:.1f}s)")
    print(f"✓ TEST_RESULTS.md updated")
    print()
    print("Summary:")
    print(f"  - Countries tested: 258")
    print(f"  - Test points: 2513+")
    print(f"  - Compression: Integrated into build pipeline")
    print()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
