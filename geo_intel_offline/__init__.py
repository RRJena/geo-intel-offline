"""
geo_intel_offline - Production-ready offline geo-intelligence library.

Unified API for both forward and reverse geocoding:

Forward Geocoding (Coordinates → Country):
    resolve(lat, lon) returns country, ISO codes, continent, timezone, confidence

Reverse Geocoding (Country → Coordinates):
    resolve(country="...") returns country centroid coordinates and metadata

Distance Calculation:
    calculate_distance(from_point, to_point) returns distance with automatic unit detection

Geo-fencing:
    check_geofence(current_location, destination, radius) detects proximity and movement

Random Coordinates:
    generate_random_coordinates_by_region(region, count) generates coordinates in countries/continents
    generate_random_coordinates_by_area(center, radius, count) generates coordinates in circular areas

Features:
- Country name, ISO2/ISO3 codes
- Continent and timezone information
- Confidence scores
- Distance calculations with multiple algorithms
- Automatic unit detection (km/miles) based on country
- Geo-fencing with state tracking and alerts
- Random coordinate generation with validation
- 99.92% accuracy across 258 countries
- 100% offline, no API keys required
"""

from .api import resolve, GeoIntelResult, resolve_by_country, ReverseGeoIntelResult
from .distance import (
    calculate_distance,
    DistanceResult,
    haversine_distance,
    vincenty_distance,
    spherical_law_of_cosines,
    calculate_distance_km,
    km_to_miles,
    miles_to_km
)
from .geofence import (
    GeofenceState,
    GeofenceConfig,
    GeofenceMonitor,
    GeofenceAlert,
    GeofenceResult,
    check_geofence
)
from .random_coords import (
    generate_random_coordinates_by_region,
    generate_random_coordinates_by_area,
    RandomCoordinateResult
)

__version__ = "1.0.3"
__all__ = [
    # Geocoding
    "resolve",
    "GeoIntelResult",
    "resolve_by_country",
    "ReverseGeoIntelResult",
    # Distance calculation
    "calculate_distance",
    "DistanceResult",
    "haversine_distance",
    "vincenty_distance",
    "spherical_law_of_cosines",
    "calculate_distance_km",
    "km_to_miles",
    "miles_to_km",
    # Geo-fencing
    "GeofenceState",
    "GeofenceConfig",
    "GeofenceMonitor",
    "GeofenceAlert",
    "GeofenceResult",
    "check_geofence",
    # Random coordinates
    "generate_random_coordinates_by_region",
    "generate_random_coordinates_by_area",
    "RandomCoordinateResult",
]
