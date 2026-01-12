#!/usr/bin/env python3
"""
Build script for creating distributable packages.

This script:
1. Cleans previous builds
2. Builds source distribution (sdist) and wheel
3. Places artifacts in build/ folder
4. Validates the package contents
"""

import sys
import subprocess
import shutil
from pathlib import Path


def clean_build():
    """Clean previous build artifacts."""
    print("Cleaning previous builds...")
    
    dirs_to_clean = ['build', 'dist', '*.egg-info']
    
    for pattern in dirs_to_clean:
        for path in Path('.').glob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
                print(f"  ✓ Removed {path}")
            elif path.is_file():
                path.unlink()
                print(f"  ✓ Removed {path}")


def check_required_files():
    """Check that required files exist."""
    print("\nChecking required files...")
    
    required_files = [
        'setup.py',
        'pyproject.toml',
        'MANIFEST.in',
        'README.md',
        'geo_intel_offline/__init__.py',
    ]
    
    required_data = [
        'geo_intel_offline/data/geohash_index.json.gz',
        'geo_intel_offline/data/polygons.json.gz',
        'geo_intel_offline/data/metadata.json.gz',
    ]
    
    all_present = True
    
    for filepath in required_files:
        path = Path(filepath)
        if path.exists():
            print(f"  ✓ {filepath}")
        else:
            print(f"  ✗ {filepath} - MISSING")
            all_present = False
    
    print("\nChecking data files...")
    for filepath in required_data:
        path = Path(filepath)
        if path.exists():
            size_mb = path.stat().st_size / 1024 / 1024
            print(f"  ✓ {filepath} ({size_mb:.2f} MB)")
        else:
            print(f"  ✗ {filepath} - MISSING")
            all_present = False
    
    return all_present


def build_package():
    """Build source distribution and wheel."""
    print("\nBuilding package...")
    print("=" * 70)
    
    # Ensure build directory exists
    Path('build').mkdir(exist_ok=True)
    
    # Try using build module first (Python 3.8+, recommended)
    try:
        import importlib.util
        spec = importlib.util.find_spec("build")
        if spec is not None:
            result = subprocess.run(
                [sys.executable, "-m", "build", "--outdir", "build"],
                check=True,
                capture_output=True,
                text=True
            )
            print(result.stdout)
            if result.stderr:
                print("Build warnings:", result.stderr)
            return True
    except (subprocess.CalledProcessError, ImportError):
        pass
    
    # Fallback to setuptools directly
    print("Using setuptools directly...")
    
    try:
        # Build sdist
        print("  Building source distribution (sdist)...")
        result = subprocess.run(
            [sys.executable, "setup.py", "sdist", "--dist-dir", "build"],
            check=True,
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(result.stdout)
        
        # Build wheel
        print("  Building wheel...")
        result = subprocess.run(
            [sys.executable, "setup.py", "bdist_wheel", "--dist-dir", "build"],
            check=True,
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(result.stdout)
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Build failed:")
        print(e.stdout)
        print(e.stderr)
        return False


def validate_package():
    """Validate built packages."""
    print("\nValidating packages...")
    
    build_dir = Path('build')
    if not build_dir.exists():
        print("  ✗ Build directory not found")
        return False
    
    packages = list(build_dir.glob('*.tar.gz')) + list(build_dir.glob('*.whl'))
    
    if not packages:
        print("  ✗ No packages found in build/")
        return False
    
    print(f"  ✓ Found {len(packages)} package(s):")
    for pkg in packages:
        size_mb = pkg.stat().st_size / 1024 / 1024
        print(f"    - {pkg.name} ({size_mb:.2f} MB)")
    
    # Check package contents (wheel)
    wheel = next((p for p in packages if p.suffix == '.whl'), None)
    if wheel:
        print(f"\n  Checking wheel contents: {wheel.name}")
        import zipfile
        with zipfile.ZipFile(wheel) as z:
            data_files = [f for f in z.namelist() if 'data/' in f and '.gz' in f]
            if data_files:
                print(f"    ✓ Contains {len(data_files)} compressed data files")
            else:
                print(f"    ⚠ No compressed data files found in wheel")
                all_files = [f for f in z.namelist() if 'data/' in f]
                if all_files:
                    print(f"    Found {len(all_files)} data files (uncompressed)")
    
    return True


def main():
    """Main build process."""
    print("=" * 70)
    print("GEO-INTEL-OFFLINE - PACKAGE BUILDER")
    print("=" * 70)
    print()
    
    # Step 1: Clean
    clean_build()
    
    # Step 2: Check files
    if not check_required_files():
        print("\n✗ Missing required files. Cannot build package.")
        return 1
    
    # Step 3: Build
    if not build_package():
        print("\n✗ Build failed.")
        return 1
    
    # Step 4: Validate
    if not validate_package():
        print("\n⚠ Package validation warnings.")
    
    print("\n" + "=" * 70)
    print("BUILD COMPLETE")
    print("=" * 70)
    print("\nPackage artifacts are in the 'build/' directory:")
    build_dir = Path('build')
    if build_dir.exists():
        for pkg in sorted(build_dir.glob('*')):
            size_mb = pkg.stat().st_size / 1024 / 1024
            print(f"  - {pkg.name} ({size_mb:.2f} MB)")
    
    print("\nTo upload to PyPI:")
    print("  twine upload build/*")
    print("\nTo upload to uv repository:")
    print("  uv publish build/*")
    print("\nTo install locally:")
    print("  pip install build/*.whl")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
