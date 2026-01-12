#!/usr/bin/env python3
"""
Diagnose why specific countries have 0% accuracy.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from geo_intel_offline.data_loader import get_loader
from geo_intel_offline.pip import point_in_polygon_with_holes
import json


def diagnose_country(country_name_or_iso2):
    """Diagnose a specific country."""
    loader = get_loader()
    
    # Find country
    country_id = None
    metadata = None
    for cid, meta in loader.metadata.items():
        if (country_name_or_iso2.lower() in meta.get('name', '').lower() or 
            country_name_or_iso2.upper() == meta.get('iso2', '').upper()):
            country_id = cid
            metadata = meta
            break
    
    if not country_id:
        print(f"Country '{country_name_or_iso2}' not found")
        return
    
    print(f"\n{'='*70}")
    print(f"Diagnosing: {metadata['name']} (ISO2: {metadata.get('iso2', 'N/A')})")
    print(f"{'='*70}\n")
    
    polygon = loader.get_polygon(country_id)
    if not polygon:
        print("⚠ No polygon data!")
        return
    
    # Check polygon structure
    exterior = polygon.get('exterior', [])
    is_multi = polygon.get('multi', False)
    exteriors = polygon.get('exteriors', [])
    holes = polygon.get('holes', [])
    
    print(f"Polygon Type: {'MultiPolygon' if is_multi else 'Polygon'}")
    
    if is_multi and exteriors:
        print(f"MultiPolygon parts: {len(exteriors)}")
        for i, ext in enumerate(exteriors[:5]):  # Show first 5
            print(f"  Part {i+1}: {len(ext)} vertices")
            if len(ext) < 3:
                print(f"    ⚠ INVALID (need at least 3 vertices)")
        
        if len(exteriors) > 5:
            print(f"  ... and {len(exteriors) - 5} more parts")
        
        # Test with centroid of first part
        if exteriors and len(exteriors[0]) >= 3:
            ext_tuples = [(p[0], p[1]) for p in exteriors[0]]
            lats = [p[0] for p in ext_tuples]
            lons = [p[1] for p in ext_tuples]
            centroid = (sum(lats) / len(lats), sum(lons) / len(lons))
            
            print(f"\nTesting centroid of first part: {centroid}")
            is_inside = point_in_polygon_with_holes(centroid, ext_tuples, None)
            print(f"  Point in polygon: {is_inside}")
    else:
        print(f"Exterior vertices: {len(exterior)}")
        
        if len(exterior) < 3:
            print(f"  ⚠ INVALID (need at least 3 vertices)")
            print(f"  This is why no test points can be generated!")
            return
        
        # Convert to tuples
        ext_tuples = [(p[0], p[1]) for p in exterior]
        holes_tuples = [[(p[0], p[1]) for p in hole] for hole in holes] if holes else None
        
        # Test with centroid
        lats = [p[0] for p in ext_tuples]
        lons = [p[1] for p in ext_tuples]
        centroid = (sum(lats) / len(lats), sum(lons) / len(lons))
        
        print(f"\nCentroid: {centroid}")
        is_inside = point_in_polygon_with_holes(centroid, ext_tuples, holes_tuples)
        print(f"  Point in polygon: {is_inside}")
    
    # Check geohash index
    geohash_index = loader.geohash_index
    country_geohashes = [gh for gh, ids in geohash_index.items() if country_id in ids]
    print(f"\nGeohash index coverage: {len(country_geohashes)} geohashes")
    
    if len(country_geohashes) == 0:
        print("  ⚠ NO GEOHASHES INDEXED - This is why resolution fails!")
    
    print()


if __name__ == '__main__':
    target_countries = ['VA', 'MV', 'Vatican', 'Maldives', 'Coral Sea', 'Spratly', 'Bajo Nuevo', 'Serranilla', 'Scarborough']
    
    if len(sys.argv) > 1:
        target_countries = sys.argv[1:]
    
    for country in target_countries:
        try:
            diagnose_country(country)
        except Exception as e:
            print(f"Error diagnosing {country}: {e}")
            import traceback
            traceback.print_exc()
