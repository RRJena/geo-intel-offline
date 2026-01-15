"""
geo_intel_offline - Production-ready offline geo-intelligence library.

Resolves latitude/longitude coordinates to:
- Country name
- ISO2/ISO3 codes
- Continent
- Timezone
- Confidence score
"""

from .api import resolve, GeoIntelResult, resolve_by_country, ReverseGeoIntelResult

__version__ = "1.0.2"
__all__ = ["resolve", "GeoIntelResult", "resolve_by_country", "ReverseGeoIntelResult"]
