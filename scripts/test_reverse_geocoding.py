#!/usr/bin/env python3
"""
Comprehensive test script for reverse geocoding functionality.

Tests resolve_by_country() for all countries using:
- Country names
- ISO2 codes
- ISO3 codes

Generates detailed test report with success/failure statistics.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from geo_intel_offline import resolve_by_country
from geo_intel_offline.data_loader import get_loader
from datetime import datetime


def test_reverse_geocoding():
    """Test reverse geocoding for all countries."""
    
    print("=" * 70)
    print("REVERSE GEOCODING - COMPREHENSIVE TEST")
    print("=" * 70)
    print()
    
    # Load metadata to get all countries
    loader = get_loader()
    metadata = loader.metadata
    
    total_countries = len(metadata)
    print(f"Testing {total_countries} countries...")
    print()
    
    # Test results
    results = {
        'by_name': {'passed': 0, 'failed': 0, 'errors': []},
        'by_iso2': {'passed': 0, 'failed': 0, 'errors': []},
        'by_iso3': {'passed': 0, 'failed': 0, 'errors': []},
        'total_tested': 0,
        'total_passed': 0,
        'total_failed': 0
    }
    
    # Collect all countries with their metadata
    countries_to_test = []
    for country_id, meta in metadata.items():
        name = meta.get('name', '')
        iso2 = meta.get('iso2', '').upper()
        iso3 = meta.get('iso3', '').upper()
        
        if name or iso2 or iso3:
            countries_to_test.append({
                'id': country_id,
                'name': name,
                'iso2': iso2,
                'iso3': iso3,
                'continent': meta.get('continent', ''),
                'timezone': meta.get('timezone', '')
            })
    
    print(f"Found {len(countries_to_test)} countries with valid data")
    print()
    print("Testing...")
    print("-" * 70)
    
    # Test each country
    for idx, country in enumerate(countries_to_test, 1):
        country_id = country['id']
        name = country['name']
        iso2 = country['iso2']
        iso3 = country['iso3']
        
        # Progress indicator
        if idx % 50 == 0:
            print(f"Progress: {idx}/{len(countries_to_test)} countries tested...")
        
        # Test 1: By country name
        if name:
            try:
                result = resolve_by_country(name)
                if result.country and result.latitude is not None and result.longitude is not None:
                    # Verify it's the correct country
                    if (result.iso2 == iso2 or result.country == name or 
                        (not iso2 and result.country == name)):
                        results['by_name']['passed'] += 1
                    else:
                        results['by_name']['failed'] += 1
                        results['by_name']['errors'].append({
                            'input': name,
                            'expected_iso2': iso2,
                            'got_iso2': result.iso2,
                            'got_country': result.country
                        })
                else:
                    results['by_name']['failed'] += 1
                    results['by_name']['errors'].append({
                        'input': name,
                        'error': 'Missing coordinates or country name'
                    })
            except Exception as e:
                results['by_name']['failed'] += 1
                results['by_name']['errors'].append({
                    'input': name,
                    'error': str(e)
                })
        
        # Test 2: By ISO2 code
        if iso2:
            try:
                result = resolve_by_country(iso2)
                if result.iso2 == iso2 and result.latitude is not None and result.longitude is not None:
                    results['by_iso2']['passed'] += 1
                else:
                    results['by_iso2']['failed'] += 1
                    results['by_iso2']['errors'].append({
                        'input': iso2,
                        'expected_iso2': iso2,
                        'got_iso2': result.iso2 if result else None
                    })
            except Exception as e:
                results['by_iso2']['failed'] += 1
                results['by_iso2']['errors'].append({
                    'input': iso2,
                    'error': str(e)
                })
        
        # Test 3: By ISO3 code
        if iso3:
            try:
                result = resolve_by_country(iso3)
                if result.iso3 == iso3 and result.latitude is not None and result.longitude is not None:
                    results['by_iso3']['passed'] += 1
                else:
                    results['by_iso3']['failed'] += 1
                    results['by_iso3']['errors'].append({
                        'input': iso3,
                        'expected_iso3': iso3,
                        'got_iso3': result.iso3 if result else None
                    })
            except Exception as e:
                results['by_iso3']['failed'] += 1
                results['by_iso3']['errors'].append({
                    'input': iso3,
                    'error': str(e)
                })
        
        results['total_tested'] += 1
    
    # Calculate totals
    results['total_passed'] = (
        results['by_name']['passed'] +
        results['by_iso2']['passed'] +
        results['by_iso3']['passed']
    )
    results['total_failed'] = (
        results['by_name']['failed'] +
        results['by_iso2']['failed'] +
        results['by_iso3']['failed']
    )
    
    # Print results
    print()
    print("=" * 70)
    print("TEST RESULTS SUMMARY")
    print("=" * 70)
    print()
    
    print(f"Total Countries Tested: {results['total_tested']}")
    print()
    
    print("By Country Name:")
    total_name_tests = results['by_name']['passed'] + results['by_name']['failed']
    if total_name_tests > 0:
        accuracy = (results['by_name']['passed'] / total_name_tests) * 100
        print(f"  Passed: {results['by_name']['passed']}/{total_name_tests} ({accuracy:.2f}%)")
        print(f"  Failed: {results['by_name']['failed']}/{total_name_tests}")
    else:
        print("  No tests performed")
    
    print()
    print("By ISO2 Code:")
    total_iso2_tests = results['by_iso2']['passed'] + results['by_iso2']['failed']
    if total_iso2_tests > 0:
        accuracy = (results['by_iso2']['passed'] / total_iso2_tests) * 100
        print(f"  Passed: {results['by_iso2']['passed']}/{total_iso2_tests} ({accuracy:.2f}%)")
        print(f"  Failed: {results['by_iso2']['failed']}/{total_iso2_tests}")
    else:
        print("  No tests performed")
    
    print()
    print("By ISO3 Code:")
    total_iso3_tests = results['by_iso3']['passed'] + results['by_iso3']['failed']
    if total_iso3_tests > 0:
        accuracy = (results['by_iso3']['passed'] / total_iso3_tests) * 100
        print(f"  Passed: {results['by_iso3']['passed']}/{total_iso3_tests} ({accuracy:.2f}%)")
        print(f"  Failed: {results['by_iso3']['failed']}/{total_iso3_tests}")
    else:
        print("  No tests performed")
    
    print()
    print("Overall Statistics:")
    total_tests = results['total_passed'] + results['total_failed']
    if total_tests > 0:
        overall_accuracy = (results['total_passed'] / total_tests) * 100
        print(f"  Total Tests: {total_tests}")
        print(f"  Passed: {results['total_passed']} ({overall_accuracy:.2f}%)")
        print(f"  Failed: {results['total_failed']}")
    else:
        print("  No tests performed")
    
    # Print errors if any
    all_errors = (
        results['by_name']['errors'] +
        results['by_iso2']['errors'] +
        results['by_iso3']['errors']
    )
    
    if all_errors:
        print()
        print("=" * 70)
        print("FAILURES DETAIL")
        print("=" * 70)
        print()
        
        # Group errors by type
        print(f"Total Failures: {len(all_errors)}")
        print()
        
        # Show first 20 errors
        print("First 20 failures:")
        for i, error in enumerate(all_errors[:20], 1):
            print(f"  {i}. Input: '{error.get('input', 'N/A')}'")
            if 'error' in error:
                print(f"     Error: {error['error']}")
            elif 'expected_iso2' in error:
                print(f"     Expected ISO2: {error['expected_iso2']}, Got: {error.get('got_iso2', 'N/A')}")
            elif 'expected_iso3' in error:
                print(f"     Expected ISO3: {error['expected_iso3']}, Got: {error.get('got_iso3', 'N/A')}")
            print()
        
        if len(all_errors) > 20:
            print(f"  ... and {len(all_errors) - 20} more failures")
    
    print()
    print("=" * 70)
    
    # Return success status
    return results['total_failed'] == 0


if __name__ == '__main__':
    try:
        success = test_reverse_geocoding()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test script error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
