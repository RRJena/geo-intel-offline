#!/usr/bin/env python3
"""
Cleanup script to remove unnecessary files and directories.

Removes:
- Python cache files (__pycache__, *.pyc, *.pyo)
- IDE/editor files (.DS_Store, *.swp, etc.)
- Test artifacts (.pytest_cache, .coverage, htmlcov)
- Build artifacts (*.egg-info, but keeps build/ directory)
- Temporary files

Keeps:
- Source code
- Data files
- Documentation
- Build directory (with packages)
"""

import os
import shutil
from pathlib import Path


def should_skip(path: Path) -> bool:
    """Check if path should be skipped."""
    skip_patterns = [
        '.git',
        'build',  # Keep build directory (has packages)
        'dist',   # Keep dist if exists
        'venv',
        'env',
        '.venv',
    ]
    
    path_str = str(path)
    return any(pattern in path_str for pattern in skip_patterns)


def cleanup_cache_files():
    """Remove Python cache files."""
    removed = []
    
    patterns = [
        '**/__pycache__',
        '**/*.pyc',
        '**/*.pyo',
    ]
    
    for pattern in patterns:
        for path in Path('.').glob(pattern):
            if should_skip(path):
                continue
            
            try:
                if path.is_dir():
                    shutil.rmtree(path)
                    removed.append(('directory', str(path)))
                elif path.is_file():
                    path.unlink()
                    removed.append(('file', str(path)))
            except Exception as e:
                print(f"  ⚠ Could not remove {path}: {e}")
    
    return removed


def cleanup_ide_files():
    """Remove IDE and editor files."""
    removed = []
    
    patterns = [
        '**/.DS_Store',
        '**/*.swp',
        '**/*.swo',
        '**/*~',
        '**/.idea',
        '**/.vscode',
    ]
    
    for pattern in patterns:
        for path in Path('.').glob(pattern):
            if should_skip(path):
                continue
            
            try:
                if path.is_dir():
                    shutil.rmtree(path)
                    removed.append(('directory', str(path)))
                elif path.is_file():
                    path.unlink()
                    removed.append(('file', str(path)))
            except Exception as e:
                print(f"  ⚠ Could not remove {path}: {e}")
    
    return removed


def cleanup_test_artifacts():
    """Remove test artifacts."""
    removed = []
    
    patterns = [
        '.pytest_cache',
        '.coverage',
        'htmlcov',
        '.tox',
        '.nox',
        '.mypy_cache',
        '.ruff_cache',
    ]
    
    for pattern in patterns:
        for path in Path('.').glob(pattern):
            if should_skip(path):
                continue
            
            try:
                if path.is_dir():
                    shutil.rmtree(path)
                    removed.append(('directory', str(path)))
                elif path.is_file():
                    path.unlink()
                    removed.append(('file', str(path)))
            except Exception as e:
                print(f"  ⚠ Could not remove {path}: {e}")
    
    return removed


def cleanup_build_artifacts():
    """Remove build artifacts (but keep build/ directory)."""
    removed = []
    
    patterns = [
        '**/*.egg-info',
    ]
    
    for pattern in patterns:
        for path in Path('.').glob(pattern):
            if should_skip(path):
                continue
            
            try:
                if path.is_dir():
                    shutil.rmtree(path)
                    removed.append(('directory', str(path)))
            except Exception as e:
                print(f"  ⚠ Could not remove {path}: {e}")
    
    return removed


def main():
    """Main cleanup function."""
    print("=" * 70)
    print("CLEANUP - Removing Unnecessary Files")
    print("=" * 70)
    print()
    
    all_removed = {
        'cache': cleanup_cache_files(),
        'ide': cleanup_ide_files(),
        'test_artifacts': cleanup_test_artifacts(),
        'build_artifacts': cleanup_build_artifacts(),
    }
    
    total_removed = sum(len(items) for items in all_removed.values())
    
    if total_removed == 0:
        print("✓ No unnecessary files found - project is clean!")
    else:
        print("Removed files:")
        print()
        for category, items in all_removed.items():
            if items:
                print(f"{category.replace('_', ' ').title()}:")
                for item_type, path in items[:10]:  # Show first 10
                    print(f"  - {path}")
                if len(items) > 10:
                    print(f"  ... and {len(items) - 10} more")
                print()
        
        print(f"Total removed: {total_removed} items")
    
    print()
    print("=" * 70)
    print("CLEANUP COMPLETE")
    print("=" * 70)
    print()
    print("Note: Build directory and packages are preserved.")
    print("      Source code and data files are untouched.")
    print()


if __name__ == '__main__':
    main()
