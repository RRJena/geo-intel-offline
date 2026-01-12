"""
Public API for geo_intel_offline library.

Clean, simple interface that hides implementation details.
"""

from typing import Dict, Optional, List
from .resolver import resolve as _resolve, ResolutionResult


class GeoIntelResult:
    """
    Result object for geo-intelligence resolution.
    
    Provides both dictionary-like access and attribute access.
    """
    
    def __init__(self, result: ResolutionResult):
        self._result = result
    
    @property
    def country(self) -> Optional[str]:
        """Country name."""
        return self._result.country_name
    
    @property
    def iso2(self) -> Optional[str]:
        """ISO 3166-1 alpha-2 code."""
        return self._result.iso2
    
    @property
    def iso3(self) -> Optional[str]:
        """ISO 3166-1 alpha-3 code."""
        return self._result.iso3
    
    @property
    def continent(self) -> Optional[str]:
        """Continent name."""
        return self._result.continent
    
    @property
    def timezone(self) -> Optional[str]:
        """IANA timezone identifier."""
        return self._result.timezone
    
    @property
    def confidence(self) -> float:
        """Confidence score (0.0-1.0)."""
        return self._result.confidence
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return self._result.to_dict()
    
    def __repr__(self) -> str:
        return (
            f"GeoIntelResult("
            f"country={self.country!r}, "
            f"iso2={self.iso2!r}, "
            f"iso3={self.iso3!r}, "
            f"confidence={self.confidence:.2f}"
            f")"
        )


def resolve(
    lat: float,
    lon: float,
    data_dir: Optional[str] = None,
    countries: Optional[List[str]] = None,
    continents: Optional[List[str]] = None,
    exclude_countries: Optional[List[str]] = None
) -> GeoIntelResult:
    """
    Resolve latitude/longitude to geo-intelligence.
    
    This is the main public API function. It resolves a coordinate pair
    to country, ISO codes, continent, timezone, and confidence score.
    
    Args:
        lat: Latitude (-90.0 to 90.0)
        lon: Longitude (-180.0 to 180.0)
        data_dir: Optional custom data directory path
        countries: Optional list of ISO2 codes to load (modular format only)
        continents: Optional list of continent names to load (modular format only)
        exclude_countries: Optional list of ISO2 codes to exclude (modular format only)
    
    Returns:
        GeoIntelResult object with resolved information
    
    Example:
        >>> result = resolve(40.7128, -74.0060)
        >>> print(result.country)
        'United States'
        >>> print(result.confidence)
        0.98
        
        >>> # Load only specific countries
        >>> result = resolve(40.7128, -74.0060, countries=["US", "CA"])
        
        >>> # Load by continent
        >>> result = resolve(40.7128, -74.0060, continents=["North America"])
    
    Raises:
        ValueError: If lat/lon are out of valid range
        FileNotFoundError: If data files are missing
    """
    resolution_result = _resolve(
        lat, lon, data_dir,
        countries=countries,
        continents=continents,
        exclude_countries=exclude_countries
    )
    return GeoIntelResult(resolution_result)
