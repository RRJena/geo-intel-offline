"""
Hierarchical resolver for country → state → city resolution.

Extends the base resolver to support multi-level geo-intelligence.
"""

from typing import Optional, Dict, List, Tuple
from .resolver import resolve as resolve_country, ResolutionResult
from .data_loader import get_loader


class HierarchicalResult:
    """Result with country, state/province, and city information."""
    
    def __init__(
        self,
        country: Optional[str] = None,
        country_iso2: Optional[str] = None,
        country_iso3: Optional[str] = None,
        state: Optional[str] = None,
        state_code: Optional[str] = None,
        city: Optional[str] = None,
        continent: Optional[str] = None,
        timezone: Optional[str] = None,
        confidence: float = 0.0
    ):
        self.country = country
        self.country_iso2 = country_iso2
        self.country_iso3 = country_iso3
        self.state = state
        self.state_code = state_code
        self.city = city
        self.continent = continent
        self.timezone = timezone
        self.confidence = confidence
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "country": self.country,
            "country_iso2": self.country_iso2,
            "country_iso3": self.country_iso3,
            "state": self.state,
            "state_code": self.state_code,
            "city": self.city,
            "continent": self.continent,
            "timezone": self.timezone,
            "confidence": self.confidence
        }


def resolve_hierarchical(
    lat: float,
    lon: float,
    include_states: bool = False,
    include_cities: bool = False,
    data_dir: Optional[str] = None
) -> HierarchicalResult:
    """
    Resolve coordinates hierarchically: country → state → city.
    
    Args:
        lat: Latitude
        lon: Longitude
        include_states: Whether to resolve state/province (requires state data)
        include_cities: Whether to resolve city (requires city data)
        data_dir: Optional custom data directory
    
    Returns:
        HierarchicalResult with country, state, and city information
    """
    # First resolve country (always available)
    country_result = resolve_country(lat, lon, data_dir)
    
    if not country_result.is_valid():
        return HierarchicalResult()
    
    result = HierarchicalResult(
        country=country_result.country_name,
        country_iso2=country_result.iso2,
        country_iso3=country_result.iso3,
        continent=country_result.continent,
        timezone=country_result.timezone,
        confidence=country_result.confidence
    )
    
    # Resolve state/province if requested and data available
    if include_states:
        state_info = _resolve_state(lat, lon, country_result.country_id, data_dir)
        if state_info:
            result.state = state_info.get('name')
            result.state_code = state_info.get('code')
            # Adjust confidence (state resolution may be less accurate)
            result.confidence = min(result.confidence, state_info.get('confidence', result.confidence))
    
    # Resolve city if requested and data available
    if include_cities:
        city_info = _resolve_city(lat, lon, country_result.country_id, data_dir)
        if city_info:
            result.city = city_info.get('name')
            # Adjust confidence
            result.confidence = min(result.confidence, city_info.get('confidence', result.confidence))
    
    return result


def _resolve_state(
    lat: float,
    lon: float,
    country_id: int,
    data_dir: Optional[str]
) -> Optional[Dict]:
    """
    Resolve state/province within a country.
    
    Note: Requires state-level data files (states_index.json, states_polygons.json)
    """
    # This would load state data similar to country resolution
    # For now, return None (state data not yet implemented)
    return None


def _resolve_city(
    lat: float,
    lon: float,
    country_id: int,
    data_dir: Optional[str]
) -> Optional[Dict]:
    """
    Resolve city within a country.
    
    Note: Requires city-level data files (cities_index.json, cities_data.json)
    """
    # This would load city data (points or polygons)
    # For now, return None (city data not yet implemented)
    return None
