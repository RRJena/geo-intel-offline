#!/usr/bin/env python3
"""
Detailed comprehensive test script for reverse geocoding.

Tests resolve_by_country() for all countries and generates detailed report.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from geo_intel_offline import resolve_by_country
from geo_intel_offline.data_loader import get_loader


def test_all_countries_detailed():
    """Test reverse geocoding for all countries with detailed reporting."""
    
    print("=" * 70)
    print("REVERSE GEOCODING - DETAILED COMPREHENSIVE TEST")
    print("=" * 70)
    print()
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Load metadata
    loader = get_loader()
    metadata = loader.metadata
    polygons = loader.polygons
    
    total_countries = len(metadata)
    print(f"Total countries in dataset: {total_countries}")
    print()
    
    # Test results
    test_results = []
    stats = {
        'total_countries': total_countries,
        'by_name': {'passed': 0, 'failed': 0},
        'by_iso2': {'passed': 0, 'failed': 0},
        'by_iso3': {'passed': 0, 'failed': 0},
        'countries_with_coordinates': 0,
        'countries_without_coordinates': 0
    }
    
    # Test each country
    print("Testing all countries...")
    print("-" * 70)
    
    for country_id, meta in sorted(metadata.items()):
        name = meta.get('name', '')
        iso2 = meta.get('iso2', '').upper()
        iso3 = meta.get('iso3', '').upper()
        continent = meta.get('continent', '')
        timezone = meta.get('timezone', '')
        
        country_result = {
            'country_id': country_id,
            'name': name,
            'iso2': iso2,
            'iso3': iso3,
            'continent': continent,
            'timezone': timezone,
            'tests': {
                'by_name': {'status': 'not_tested', 'result': None, 'error': None},
                'by_iso2': {'status': 'not_tested', 'result': None, 'error': None},
                'by_iso3': {'status': 'not_tested', 'result': None, 'error': None}
            }
        }
        
        # Test by country name
        if name:
            try:
                result = resolve_by_country(name)
                if result and result.latitude is not None and result.longitude is not None:
                    # Verify correctness
                    if result.iso2 == iso2 or (not iso2 and result.country == name):
                        country_result['tests']['by_name'] = {
                            'status': 'passed',
                            'result': {
                                'latitude': result.latitude,
                                'longitude': result.longitude,
                                'country': result.country,
                                'iso2': result.iso2,
                                'iso3': result.iso3
                            }
                        }
                        stats['by_name']['passed'] += 1
                        if country_id not in [r['country_id'] for r in test_results if r.get('has_coordinates')]:
                            stats['countries_with_coordinates'] += 1
                    else:
                        country_result['tests']['by_name'] = {
                            'status': 'failed',
                            'error': f"ISO2 mismatch: expected {iso2}, got {result.iso2}"
                        }
                        stats['by_name']['failed'] += 1
                else:
                    country_result['tests']['by_name'] = {
                        'status': 'failed',
                        'error': 'Missing coordinates or country name'
                    }
                    stats['by_name']['failed'] += 1
            except Exception as e:
                country_result['tests']['by_name'] = {
                    'status': 'failed',
                    'error': str(e)
                }
                stats['by_name']['failed'] += 1
        
        # Test by ISO2
        if iso2 and iso2 != '-99':
            try:
                result = resolve_by_country(iso2)
                if result and result.iso2 == iso2 and result.latitude is not None:
                    country_result['tests']['by_iso2'] = {
                        'status': 'passed',
                        'result': {
                            'latitude': result.latitude,
                            'longitude': result.longitude,
                            'country': result.country
                        }
                    }
                    stats['by_iso2']['passed'] += 1
                else:
                    country_result['tests']['by_iso2'] = {
                        'status': 'failed',
                        'error': f"ISO2 mismatch or missing coordinates"
                    }
                    stats['by_iso2']['failed'] += 1
            except Exception as e:
                country_result['tests']['by_iso2'] = {
                    'status': 'failed',
                    'error': str(e)
                }
                stats['by_iso2']['failed'] += 1
        
        # Test by ISO3
        if iso3 and iso3 != '-99':
            try:
                result = resolve_by_country(iso3)
                if result and result.iso3 == iso3 and result.latitude is not None:
                    country_result['tests']['by_iso3'] = {
                        'status': 'passed',
                        'result': {
                            'latitude': result.latitude,
                            'longitude': result.longitude,
                            'country': result.country
                        }
                    }
                    stats['by_iso3']['passed'] += 1
                else:
                    country_result['tests']['by_iso3'] = {
                        'status': 'failed',
                        'error': f"ISO3 mismatch or missing coordinates"
                    }
                    stats['by_iso3']['failed'] += 1
            except Exception as e:
                country_result['tests']['by_iso3'] = {
                    'status': 'failed',
                    'error': str(e)
                }
                stats['by_iso3']['failed'] += 1
        
        # Check if country has coordinates
        has_coords = any(
            test.get('status') == 'passed' and test.get('result', {}).get('latitude') is not None
            for test in country_result['tests'].values()
        )
        country_result['has_coordinates'] = has_coords
        
        if not has_coords:
            stats['countries_without_coordinates'] += 1
        
        test_results.append(country_result)
        
        # Progress indicator
        if len(test_results) % 50 == 0:
            print(f"  Tested {len(test_results)}/{total_countries} countries...")
    
    # Calculate totals
    total_tests = (
        stats['by_name']['passed'] + stats['by_name']['failed'] +
        stats['by_iso2']['passed'] + stats['by_iso2']['failed'] +
        stats['by_iso3']['passed'] + stats['by_iso3']['failed']
    )
    total_passed = (
        stats['by_name']['passed'] +
        stats['by_iso2']['passed'] +
        stats['by_iso3']['passed']
    )
    total_failed = (
        stats['by_name']['failed'] +
        stats['by_iso2']['failed'] +
        stats['by_iso3']['failed']
    )
    
    # Print summary
    print()
    print("=" * 70)
    print("TEST RESULTS SUMMARY")
    print("=" * 70)
    print()
    print(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print(f"Total Countries: {total_countries}")
    print(f"Countries with Coordinates: {stats['countries_with_coordinates']}")
    print(f"Countries without Coordinates: {stats['countries_without_coordinates']}")
    print()
    
    print("Test Results by Input Type:")
    print("-" * 70)
    
    # By name
    name_total = stats['by_name']['passed'] + stats['by_name']['failed']
    if name_total > 0:
        name_acc = (stats['by_name']['passed'] / name_total) * 100
        print(f"By Country Name: {stats['by_name']['passed']}/{name_total} passed ({name_acc:.2f}%)")
    
    # By ISO2
    iso2_total = stats['by_iso2']['passed'] + stats['by_iso2']['failed']
    if iso2_total > 0:
        iso2_acc = (stats['by_iso2']['passed'] / iso2_total) * 100
        print(f"By ISO2 Code:    {stats['by_iso2']['passed']}/{iso2_total} passed ({iso2_acc:.2f}%)")
    
    # By ISO3
    iso3_total = stats['by_iso3']['passed'] + stats['by_iso3']['failed']
    if iso3_total > 0:
        iso3_acc = (stats['by_iso3']['passed'] / iso3_total) * 100
        print(f"By ISO3 Code:    {stats['by_iso3']['passed']}/{iso3_total} passed ({iso3_acc:.2f}%)")
    
    print()
    print("Overall Statistics:")
    print("-" * 70)
    if total_tests > 0:
        overall_acc = (total_passed / total_tests) * 100
        print(f"Total Tests:      {total_tests}")
        print(f"Passed:           {total_passed} ({overall_acc:.2f}%)")
        print(f"Failed:           {total_failed}")
    else:
        print("No tests performed")
    
    # Find failures
    failures = []
    for result in test_results:
        for test_type, test_data in result['tests'].items():
            if test_data['status'] == 'failed':
                failures.append({
                    'country': result['name'],
                    'iso2': result['iso2'],
                    'test_type': test_type,
                    'error': test_data.get('error', 'Unknown error')
                })
    
    if failures:
        print()
        print("=" * 70)
        print("FAILURES DETAIL")
        print("=" * 70)
        print()
        print(f"Total Failures: {len(failures)}")
        print()
        
        # Group by test type
        failures_by_type = {}
        for failure in failures:
            test_type = failure['test_type']
            if test_type not in failures_by_type:
                failures_by_type[test_type] = []
            failures_by_type[test_type].append(failure)
        
        for test_type, type_failures in failures_by_type.items():
            print(f"{test_type.upper()} Failures ({len(type_failures)}):")
            for failure in type_failures[:10]:  # Show first 10
                print(f"  - {failure['country']} ({failure['iso2']}): {failure['error']}")
            if len(type_failures) > 10:
                print(f"  ... and {len(type_failures) - 10} more")
            print()
    
    # Sample successful results
    print("=" * 70)
    print("SAMPLE SUCCESSFUL RESULTS")
    print("=" * 70)
    print()
    
    successful = [r for r in test_results if r['has_coordinates']][:10]
    for result in successful:
        # Find a successful test
        for test_type, test_data in result['tests'].items():
            if test_data['status'] == 'passed':
                test_result = test_data['result']
                print(f"{result['name']} ({result['iso2']}):")
                print(f"  Input: {test_type}")
                print(f"  Coordinates: ({test_result['latitude']:.4f}, {test_result['longitude']:.4f})")
                print()
                break
    
    print("=" * 70)
    
    # Save detailed report to file
    report_file = Path(__file__).parent.parent / "REVERSE_GEOCODING_TEST_RESULTS.md"
    
    with open(report_file, 'w') as f:
        f.write("# Reverse Geocoding Test Results\n\n")
        f.write(f"**Test Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("## Summary\n\n")
        f.write(f"- **Total Countries**: {total_countries}\n")
        f.write(f"- **Countries with Coordinates**: {stats['countries_with_coordinates']}\n")
        f.write(f"- **Total Tests**: {total_tests}\n")
        f.write(f"- **Passed**: {total_passed} ({overall_acc:.2f}%)\n")
        f.write(f"- **Failed**: {total_failed}\n\n")
        
        f.write("## Test Results by Type\n\n")
        f.write("| Input Type | Passed | Failed | Accuracy |\n")
        f.write("|------------|--------|--------|----------|\n")
        if name_total > 0:
            f.write(f"| Country Name | {stats['by_name']['passed']} | {stats['by_name']['failed']} | {name_acc:.2f}% |\n")
        if iso2_total > 0:
            f.write(f"| ISO2 Code | {stats['by_iso2']['passed']} | {stats['by_iso2']['failed']} | {iso2_acc:.2f}% |\n")
        if iso3_total > 0:
            f.write(f"| ISO3 Code | {stats['by_iso3']['passed']} | {stats['by_iso3']['failed']} | {iso3_acc:.2f}% |\n")
        
        if failures:
            f.write("\n## Failures\n\n")
            for failure in failures:
                f.write(f"- **{failure['country']}** ({failure['iso2']}) - {failure['test_type']}: {failure['error']}\n")
    
    print(f"\n✅ Detailed report saved to: {report_file}")
    
    return total_failed == 0


if __name__ == '__main__':
    try:
        success = test_all_countries_detailed()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test script error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
