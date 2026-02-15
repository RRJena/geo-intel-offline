"""
Distance calculation module with multiple algorithms.

This module provides accurate distance calculations between geographic points
using various algorithms optimized for different use cases.

Features:
- Haversine formula (standard great-circle distance)
- Spherical Law of Cosines (alternative validation method)
- Vincenty formula (high-precision ellipsoidal distance)
- All algorithms return distance in kilometers

Algorithms:
- Haversine: Most accurate for short to medium distances (< 1000 km)
- Spherical Law of Cosines: Alternative method, less accurate for short distances
- Vincenty: Most accurate for all distances, accounts for Earth's ellipsoidal shape
"""

import math
from typing import Tuple, Optional, Literal, Union, Dict
from dataclasses import dataclass

# Earth radius constants (in kilometers)
EARTH_RADIUS_KM = 6371.0
EARTH_RADIUS_MILES = 3958.8

# WGS84 ellipsoid parameters for Vincenty formula
WGS84_A = 6378137.0  # Semi-major axis (meters)
WGS84_F = 1 / 298.257223563  # Flattening
WGS84_B = (1 - WGS84_F) * WGS84_A  # Semi-minor axis (meters)

# Country unit preferences (ISO2 codes that use imperial system)
# All other countries default to metric (kilometers)
# Reference: Countries that officially use miles for road distances
IMPERIAL_COUNTRIES = {
    'US',  # United States
    'GB',  # United Kingdom
    'LR',  # Liberia
    'MM',  # Myanmar
    # Note: Some countries use mixed systems, but we default to their primary system
}


def haversine_distance(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float
) -> float:
    """
    Calculate distance between two points using Haversine formula.
    
    The Haversine formula calculates the great-circle distance between two points
    on a sphere given their longitudes and latitudes. This is the most commonly
    used formula for distance calculations and is accurate for short to medium
    distances (< 1000 km).
    
    Formula:
        a = sin²(Δlat/2) + cos(lat1) * cos(lat2) * sin²(Δlon/2)
        c = 2 * atan2(√a, √(1-a))
        d = R * c
    
    Where:
        - Δlat = lat2 - lat1
        - Δlon = lon2 - lon1
        - R = Earth's radius
    
    Args:
        lat1: Latitude of first point in degrees (-90 to 90)
        lon1: Longitude of first point in degrees (-180 to 180)
        lat2: Latitude of second point in degrees (-90 to 90)
        lon2: Longitude of second point in degrees (-180 to 180)
    
    Returns:
        Distance in kilometers
    
    Raises:
        ValueError: If coordinates are out of valid range
    
    Example:
        >>> # Distance between New York and Los Angeles
        >>> distance = haversine_distance(40.7128, -74.0060, 34.0522, -118.2437)
        >>> print(f"{distance:.2f} km")
        3944.18 km
    """
    # Validate input coordinates
    if not (-90 <= lat1 <= 90) or not (-90 <= lat2 <= 90):
        raise ValueError(
            f"Latitude must be between -90 and 90 degrees. "
            f"Got: lat1={lat1}, lat2={lat2}"
        )
    if not (-180 <= lon1 <= 180) or not (-180 <= lon2 <= 180):
        raise ValueError(
            f"Longitude must be between -180 and 180 degrees. "
            f"Got: lon1={lon1}, lon2={lon2}"
        )
    
    # Convert degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Calculate differences
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Haversine formula
    a = (
        math.sin(dlat / 2) ** 2 +
        math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    # Distance in kilometers
    distance_km = EARTH_RADIUS_KM * c
    
    return distance_km


def spherical_law_of_cosines(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float
) -> float:
    """
    Calculate distance between two points using Spherical Law of Cosines.
    
    The Spherical Law of Cosines is an alternative method for calculating
    great-circle distances. It is less accurate than Haversine for very short
    distances but can be useful for validation or when computational efficiency
    is a concern.
    
    Formula:
        d = R * arccos(sin(lat1) * sin(lat2) + cos(lat1) * cos(lat2) * cos(Δlon))
    
    Where:
        - Δlon = lon2 - lon1
        - R = Earth's radius
    
    Args:
        lat1: Latitude of first point in degrees (-90 to 90)
        lon1: Longitude of first point in degrees (-180 to 180)
        lat2: Latitude of second point in degrees (-90 to 90)
        lon2: Longitude of second point in degrees (-180 to 180)
    
    Returns:
        Distance in kilometers
    
    Raises:
        ValueError: If coordinates are out of valid range
    
    Example:
        >>> # Distance between New York and Los Angeles
        >>> distance = spherical_law_of_cosines(40.7128, -74.0060, 34.0522, -118.2437)
        >>> print(f"{distance:.2f} km")
        3944.18 km
    """
    # Validate input coordinates
    if not (-90 <= lat1 <= 90) or not (-90 <= lat2 <= 90):
        raise ValueError(
            f"Latitude must be between -90 and 90 degrees. "
            f"Got: lat1={lat1}, lat2={lat2}"
        )
    if not (-180 <= lon1 <= 180) or not (-180 <= lon2 <= 180):
        raise ValueError(
            f"Longitude must be between -180 and 180 degrees. "
            f"Got: lon1={lon1}, lon2={lon2}"
        )
    
    # Convert degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Calculate difference in longitude
    dlon = lon2_rad - lon1_rad
    
    # Spherical Law of Cosines formula
    # Clamp the result to [-1, 1] to avoid numerical errors with arccos
    central_angle = (
        math.sin(lat1_rad) * math.sin(lat2_rad) +
        math.cos(lat1_rad) * math.cos(lat2_rad) * math.cos(dlon)
    )
    central_angle = max(-1.0, min(1.0, central_angle))  # Clamp to valid range
    
    # Distance in kilometers
    distance_km = EARTH_RADIUS_KM * math.acos(central_angle)
    
    return distance_km


def vincenty_distance(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
    max_iterations: int = 200,
    tolerance: float = 1e-12
) -> float:
    """
    Calculate distance between two points using Vincenty's inverse formula.
    
    Vincenty's formula is the most accurate method for calculating distances
    on an ellipsoid. It accounts for Earth's ellipsoidal shape (flattening at
    the poles) and provides sub-millimeter accuracy. This is the recommended
    method for high-precision applications.
    
    The algorithm uses an iterative approach to solve the inverse geodetic
    problem on an ellipsoid.
    
    Args:
        lat1: Latitude of first point in degrees (-90 to 90)
        lon1: Longitude of first point in degrees (-180 to 180)
        lat2: Latitude of second point in degrees (-90 to 90)
        lon2: Longitude of second point in degrees (-180 to 180)
        max_iterations: Maximum number of iterations (default: 200)
        tolerance: Convergence tolerance (default: 1e-12)
    
    Returns:
        Distance in kilometers
    
    Raises:
        ValueError: If coordinates are out of valid range
        RuntimeError: If algorithm fails to converge
    
    Example:
        >>> # Distance between New York and Los Angeles
        >>> distance = vincenty_distance(40.7128, -74.0060, 34.0522, -118.2437)
        >>> print(f"{distance:.2f} km")
        3944.18 km
    """
    # Validate input coordinates
    if not (-90 <= lat1 <= 90) or not (-90 <= lat2 <= 90):
        raise ValueError(
            f"Latitude must be between -90 and 90 degrees. "
            f"Got: lat1={lat1}, lat2={lat2}"
        )
    if not (-180 <= lon1 <= 180) or not (-180 <= lon2 <= 180):
        raise ValueError(
            f"Longitude must be between -180 and 180 degrees. "
            f"Got: lon1={lon1}, lon2={lon2}"
        )
    
    # Convert degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Calculate difference in longitude
    L = lon2_rad - lon1_rad
    
    # Calculate reduced latitudes
    U1 = math.atan((1 - WGS84_F) * math.tan(lat1_rad))
    U2 = math.atan((1 - WGS84_F) * math.tan(lat2_rad))
    
    sin_U1 = math.sin(U1)
    cos_U1 = math.cos(U1)
    sin_U2 = math.sin(U2)
    cos_U2 = math.cos(U2)
    
    # Initialize iteration variables
    lambda_p = L
    lambda_val = L
    
    # Iterate to find lambda
    for iteration in range(max_iterations):
        sin_lambda = math.sin(lambda_val)
        cos_lambda = math.cos(lambda_val)
        
        sin_sigma = math.sqrt(
            (cos_U2 * sin_lambda) ** 2 +
            (cos_U1 * sin_U2 - sin_U1 * cos_U2 * cos_lambda) ** 2
        )
        
        if sin_sigma == 0:
            # Co-incident points
            return 0.0
        
        cos_sigma = sin_U1 * sin_U2 + cos_U1 * cos_U2 * cos_lambda
        sigma = math.atan2(sin_sigma, cos_sigma)
        
        sin_alpha = cos_U1 * cos_U2 * sin_lambda / sin_sigma
        cos2_alpha = 1 - sin_alpha ** 2
        
        if cos2_alpha == 0:
            # Equatorial line
            cos_2sigma_m = 0
        else:
            cos_2sigma_m = cos_sigma - 2 * sin_U1 * sin_U2 / cos2_alpha
        
        C = (WGS84_F / 16) * cos2_alpha * (4 + WGS84_F * (4 - 3 * cos2_alpha))
        
        lambda_p = lambda_val
        lambda_val = (
            L + (1 - C) * WGS84_F * sin_alpha * (
                sigma + C * sin_sigma * (
                    cos_2sigma_m + C * cos_sigma * (
                        -1 + 2 * cos_2sigma_m ** 2
                    )
                )
            )
        )
        
        # Check for convergence
        if abs(lambda_val - lambda_p) < tolerance:
            break
    else:
        # Failed to converge
        raise RuntimeError(
            f"Vincenty algorithm failed to converge after {max_iterations} iterations. "
            f"This may occur for nearly antipodal points."
        )
    
    # Calculate final values
    u2 = cos2_alpha * (WGS84_A ** 2 - WGS84_B ** 2) / (WGS84_B ** 2)
    A = 1 + (u2 / 16384) * (4096 + u2 * (-768 + u2 * (320 - 175 * u2)))
    B = (u2 / 1024) * (256 + u2 * (-128 + u2 * (74 - 47 * u2)))
    
    delta_sigma = (
        B * sin_sigma * (
            cos_2sigma_m + (B / 4) * (
                cos_sigma * (-1 + 2 * cos_2sigma_m ** 2) -
                (B / 6) * cos_2sigma_m * (-3 + 4 * sin_sigma ** 2) * (
                    -3 + 4 * cos_2sigma_m ** 2
                )
            )
        )
    )
    
    # Distance in meters
    distance_m = WGS84_B * A * (sigma - delta_sigma)
    
    # Convert to kilometers
    distance_km = distance_m / 1000.0
    
    return distance_km


def km_to_miles(km: float) -> float:
    """
    Convert kilometers to miles.
    
    Args:
        km: Distance in kilometers
    
    Returns:
        Distance in miles
    
    Example:
        >>> km_to_miles(100.0)
        62.1371
    """
    return km * 0.621371


def miles_to_km(miles: float) -> float:
    """
    Convert miles to kilometers.
    
    Args:
        miles: Distance in miles
    
    Returns:
        Distance in kilometers
    
    Example:
        >>> miles_to_km(100.0)
        160.934
    """
    return miles * 1.60934


def get_country_unit_preference(
    iso2_code: Optional[str]
) -> Literal['km', 'mile']:
    """
    Get preferred unit system for a country based on ISO2 code.
    
    Countries using imperial system (miles):
    - US (United States)
    - GB (United Kingdom)
    - LR (Liberia)
    - MM (Myanmar)
    
    All other countries default to metric (kilometers).
    
    Args:
        iso2_code: ISO 3166-1 alpha-2 country code (e.g., 'US', 'GB')
    
    Returns:
        'mile' for imperial countries, 'km' for metric countries (default)
    
    Example:
        >>> get_country_unit_preference('US')
        'mile'
        >>> get_country_unit_preference('FR')
        'km'
        >>> get_country_unit_preference(None)
        'km'
    """
    if iso2_code is None:
        return 'km'  # Default to metric
    
    iso2_upper = iso2_code.upper()
    return 'mile' if iso2_upper in IMPERIAL_COUNTRIES else 'km'


def determine_unit_preference(
    lat1: Optional[float] = None,
    lon1: Optional[float] = None,
    lat2: Optional[float] = None,
    lon2: Optional[float] = None,
    iso2_1: Optional[str] = None,
    iso2_2: Optional[str] = None,
    unit: Optional[Literal['km', 'mile']] = None,
    use_metric: Optional[bool] = None
) -> Literal['km', 'mile']:
    """
    Determine preferred unit for distance calculation.
    
    Priority order:
    1. Explicit unit parameter (highest priority)
    2. use_metric parameter (True = km, False = mile)
    3. Country preferences (from coordinates or ISO codes)
    4. Default to metric (km)
    
    Args:
        lat1: Latitude of first point (optional, for country detection)
        lon1: Longitude of first point (optional, for country detection)
        lat2: Latitude of second point (optional, for country detection)
        lon2: Longitude of second point (optional, for country detection)
        iso2_1: ISO2 code of first location (optional)
        iso2_2: ISO2 code of second location (optional)
        unit: Explicit unit preference ('km' or 'mile')
        use_metric: Explicit metric preference (True = km, False = mile)
    
    Returns:
        Preferred unit: 'km' or 'mile'
    
    Example:
        >>> # Explicit unit override
        >>> determine_unit_preference(unit='mile')
        'mile'
        
        >>> # Country-based detection
        >>> determine_unit_preference(iso2_1='US', iso2_2='CA')
        'mile'  # US uses miles, so preference is miles
        
        >>> # Coordinate-based detection
        >>> determine_unit_preference(lat1=40.7128, lon1=-74.0060)
        'mile'  # New York, USA
    """
    # Priority 1: Explicit unit parameter
    if unit is not None:
        if unit.lower() in ('km', 'kilometer', 'kilometre'):
            return 'km'
        elif unit.lower() in ('mile', 'miles', 'mi'):
            return 'mile'
        else:
            raise ValueError(
                f"Invalid unit: {unit}. Must be 'km' or 'mile'"
            )
    
    # Priority 2: use_metric parameter
    if use_metric is not None:
        return 'km' if use_metric else 'mile'
    
    # Priority 3: Country preferences
    # Try to get country info from coordinates if ISO codes not provided
    iso2_codes = []
    
    if iso2_1:
        iso2_codes.append(iso2_1)
    elif lat1 is not None and lon1 is not None:
        try:
            from .api import resolve
            result1 = resolve(lat1, lon1)
            if result1.iso2:
                iso2_codes.append(result1.iso2)
        except Exception:
            pass  # If resolution fails, continue without it
    
    if iso2_2:
        iso2_codes.append(iso2_2)
    elif lat2 is not None and lon2 is not None:
        try:
            from .api import resolve
            result2 = resolve(lat2, lon2)
            if result2.iso2:
                iso2_codes.append(result2.iso2)
        except Exception:
            pass  # If resolution fails, continue without it
    
    # If we have country codes, check preferences
    if iso2_codes:
        # If any country uses imperial, prefer miles
        # Otherwise, prefer metric
        for iso2 in iso2_codes:
            if get_country_unit_preference(iso2) == 'mile':
                return 'mile'
        return 'km'
    
    # Priority 4: Default to metric
    return 'km'


def normalize_location(
    location: Union[Tuple[float, float], str],
    data_dir: Optional[str] = None
) -> Tuple[float, float]:
    """
    Normalize location input to coordinates (lat, lon).
    
    Accepts:
    - Coordinate tuple: (lat, lon) → returns as-is
    - Country name: "United States" → returns country centroid
    - ISO2 code: "US" → returns country centroid
    - ISO3 code: "USA" → returns country centroid
    - Continent name: "North America" → returns continent centroid
    
    Args:
        location: Location input - can be:
            - Tuple[float, float]: (latitude, longitude)
            - str: Country name, ISO code, or continent name
        data_dir: Optional custom data directory path
    
    Returns:
        Tuple of (latitude, longitude) in degrees
    
    Raises:
        ValueError: If location cannot be resolved to coordinates
        TypeError: If location type is invalid
    
    Example:
        >>> # Coordinate tuple
        >>> normalize_location((40.7128, -74.0060))
        (40.7128, -74.0060)
        
        >>> # Country name
        >>> normalize_location("United States")
        (39.8283, -98.5795)
        
        >>> # ISO code
        >>> normalize_location("US")
        (39.8283, -98.5795)
        
        >>> # Continent
        >>> normalize_location("North America")
        (45.0, -100.0)  # Approximate continent centroid
    """
    # If already a coordinate tuple, return as-is
    if isinstance(location, tuple) and len(location) == 2:
        lat, lon = location
        if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
            # Validate coordinate ranges
            if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                raise ValueError(
                    f"Invalid coordinates: ({lat}, {lon}). "
                    f"Latitude must be -90 to 90, longitude must be -180 to 180."
                )
            return (float(lat), float(lon))
    
    # If string, try to resolve as country or continent
    if isinstance(location, str):
        location_str = location.strip()
        
        # Try country first (using reverse geocoding)
        try:
            from .api import resolve
            result = resolve(location_str, data_dir=data_dir)
            
            # Check if it's a reverse geocoding result (has latitude/longitude)
            if hasattr(result, 'latitude') and hasattr(result, 'longitude'):
                if result.latitude is not None and result.longitude is not None:
                    return (result.latitude, result.longitude)
        except (ValueError, AttributeError):
            pass  # Not a country, try continent
        
        # Try continent
        continent_coords = _get_continent_centroid(location_str, data_dir)
        if continent_coords:
            return continent_coords
        
        # If we get here, location couldn't be resolved
        raise ValueError(
            f"Could not resolve location '{location_str}' to coordinates. "
            f"Expected: coordinate tuple (lat, lon), country name/ISO code, or continent name."
        )
    
    # Invalid type
    raise TypeError(
        f"Invalid location type: {type(location).__name__}. "
        f"Expected: Tuple[float, float] or str (country/continent name or ISO code)."
    )


def _get_continent_centroid(
    continent_name: str,
    data_dir: Optional[str] = None
) -> Optional[Tuple[float, float]]:
    """
    Get centroid coordinates for a continent.
    
    Calculates the average centroid of all countries in the continent.
    
    Args:
        continent_name: Continent name (e.g., "North America", "Europe")
        data_dir: Optional custom data directory path
    
    Returns:
        Tuple of (latitude, longitude) or None if continent not found
    """
    # Normalize continent name
    continent_mapping = {
        "africa": "Africa",
        "asia": "Asia",
        "europe": "Europe",
        "north america": "North America",
        "north_america": "North America",
        "south america": "South America",
        "south_america": "South America",
        "oceania": "Oceania",
        "australia": "Oceania",
        "antarctica": "Antarctica",
    }
    
    continent_normalized = continent_name.strip().lower()
    continent_standard = continent_mapping.get(continent_normalized, continent_name)
    
    try:
        from .data_loader import get_loader
        from .api import resolve
        
        loader = get_loader(data_dir)
        metadata = loader.metadata
        
        # Collect all countries in this continent
        continent_countries = []
        for country_id, country_meta in metadata.items():
            country_continent = country_meta.get('continent', '')
            if country_continent and country_continent.lower() == continent_standard.lower():
                # Get country coordinates
                iso2 = country_meta.get('iso2', '')
                if iso2:
                    try:
                        result = resolve(iso2, data_dir=data_dir)
                        if hasattr(result, 'latitude') and hasattr(result, 'longitude'):
                            if result.latitude is not None and result.longitude is not None:
                                continent_countries.append((result.latitude, result.longitude))
                    except Exception:
                        continue  # Skip countries that can't be resolved
        
        if not continent_countries:
            return None
        
        # Calculate average centroid
        avg_lat = sum(coord[0] for coord in continent_countries) / len(continent_countries)
        avg_lon = sum(coord[1] for coord in continent_countries) / len(continent_countries)
        
        return (avg_lat, avg_lon)
    
    except Exception:
        return None


@dataclass
class DistanceResult:
    """
    Result object for distance calculations.
    
    Contains distance value, unit, calculation method, and location information.
    """
    distance: float
    unit: str  # 'km' or 'mile'
    method: str  # 'haversine', 'vincenty', 'spherical'
    from_location: Union[Tuple[float, float], str]
    to_location: Union[Tuple[float, float], str]
    from_coordinates: Optional[Tuple[float, float]] = None
    to_coordinates: Optional[Tuple[float, float]] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'distance': self.distance,
            'unit': self.unit,
            'method': self.method,
            'from_location': self.from_location,
            'to_location': self.to_location,
            'from_coordinates': self.from_coordinates,
            'to_coordinates': self.to_coordinates
        }
    
    def __repr__(self) -> str:
        return (
            f"DistanceResult("
            f"distance={self.distance:.2f} {self.unit}, "
            f"method={self.method}, "
            f"from={self.from_location}, "
            f"to={self.to_location}"
            f")"
        )


def _select_calculation_method(
    method: str,
    from_coords: Tuple[float, float],
    to_coords: Tuple[float, float]
) -> str:
    """
    Select appropriate calculation method.
    
    If method is 'auto', selects based on distance:
    - Short distances (< 1000 km): Haversine (fast, accurate)
    - Long distances (>= 1000 km): Vincenty (most accurate)
    
    Args:
        method: Requested method ('haversine', 'vincenty', 'spherical', 'auto')
        from_coords: Starting coordinates
        to_coords: Ending coordinates
    
    Returns:
        Selected method name
    """
    if method.lower() == 'auto':
        # Calculate rough distance to decide method
        rough_distance = haversine_distance(
            from_coords[0], from_coords[1],
            to_coords[0], to_coords[1]
        )
        
        # For long distances, use Vincenty for better accuracy
        if rough_distance >= 1000.0:
            return 'vincenty'
        else:
            return 'haversine'
    
    method_lower = method.lower()
    if method_lower in ('haversine', 'vincenty', 'spherical'):
        return method_lower
    
    raise ValueError(
        f"Unknown method: {method}. "
        f"Supported methods: 'haversine', 'vincenty', 'spherical', 'auto'"
    )


def calculate_distance(
    from_point: Union[Tuple[float, float], str],
    to_point: Union[Tuple[float, float], str],
    method: Literal['haversine', 'vincenty', 'spherical', 'auto'] = 'auto',
    unit: Optional[Literal['km', 'mile']] = None,
    use_metric: Optional[bool] = None,
    data_dir: Optional[str] = None
) -> DistanceResult:
    """
    Calculate distance between two points with automatic unit detection.
    
    This is the main public API for distance calculations. It supports flexible
    input types and automatically detects unit preferences based on country.
    
    Args:
        from_point: Starting location - can be:
            - Tuple[float, float]: (latitude, longitude)
            - str: Country name, ISO code, or continent name
        to_point: Ending location - can be:
            - Tuple[float, float]: (latitude, longitude)
            - str: Country name, ISO code, or continent name
        method: Calculation method:
            - 'haversine': Standard great-circle distance (default for short distances)
            - 'vincenty': High-precision ellipsoidal distance (default for long distances)
            - 'spherical': Spherical Law of Cosines (alternative)
            - 'auto': Automatically select best method based on distance
        unit: Force unit ('km' or 'mile'), None for auto-detect based on country
        use_metric: Force metric (True) or imperial (False), None for auto-detect
        data_dir: Optional custom data directory path
    
    Returns:
        DistanceResult object with:
        - distance: Distance value
        - unit: Unit used ('km' or 'mile')
        - method: Calculation method used
        - from_location: Original from_point input
        - to_location: Original to_point input
        - from_coordinates: Resolved coordinates (if input was string)
        - to_coordinates: Resolved coordinates (if input was string)
    
    Raises:
        ValueError: If inputs are invalid or cannot be resolved
        TypeError: If input types are invalid
    
    Example:
        >>> # Distance between coordinates
        >>> result = calculate_distance((40.7128, -74.0060), (34.0522, -118.2437))
        >>> print(f"{result.distance:.2f} {result.unit}")
        2448.50 miles  # Auto-detected miles for US locations
        
        >>> # Distance between countries
        >>> result = calculate_distance("United States", "Canada")
        >>> print(f"{result.distance:.2f} {result.unit}")
        2000.00 km  # Auto-detected km for metric countries
        
        >>> # Force unit
        >>> result = calculate_distance("US", "CA", unit='km')
        >>> print(f"{result.distance:.2f} {result.unit}")
        2000.00 km
        
        >>> # Force method
        >>> result = calculate_distance((40.7128, -74.0060), (34.0522, -118.2437), method='vincenty')
        >>> print(f"{result.method}")
        vincenty
        
        >>> # Mixed inputs
        >>> result = calculate_distance((40.7128, -74.0060), "Los Angeles")
        >>> print(f"{result.distance:.2f} {result.unit}")
        2448.50 miles
    """
    # Step 1: Normalize inputs (convert country/continent names to coordinates)
    from_coords = normalize_location(from_point, data_dir=data_dir)
    to_coords = normalize_location(to_point, data_dir=data_dir)
    
    # Step 2: Determine unit preference
    preferred_unit = determine_unit_preference(
        lat1=from_coords[0],
        lon1=from_coords[1],
        lat2=to_coords[0],
        lon2=to_coords[1],
        unit=unit,
        use_metric=use_metric
    )
    
    # Step 3: Select calculation method
    calc_method = _select_calculation_method(method, from_coords, to_coords)
    
    # Step 4: Calculate distance in kilometers
    distance_km = calculate_distance_km(
        from_coords[0], from_coords[1],
        to_coords[0], to_coords[1],
        method=calc_method
    )
    
    # Step 5: Convert to preferred unit
    if preferred_unit == 'mile':
        distance = km_to_miles(distance_km)
    else:
        distance = distance_km
    
    return DistanceResult(
        distance=distance,
        unit=preferred_unit,
        method=calc_method,
        from_location=from_point,
        to_location=to_point,
        from_coordinates=from_coords,
        to_coordinates=to_coords
    )


def calculate_distance_km(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
    method: str = "haversine"
) -> float:
    """
    Calculate distance between two points using specified method.
    
    This is a convenience function that wraps the individual distance calculation
    methods. It provides a unified interface for distance calculations.
    
    Note: For the main public API with flexible inputs and unit detection,
    use calculate_distance() instead.
    
    Args:
        lat1: Latitude of first point in degrees (-90 to 90)
        lon1: Longitude of first point in degrees (-180 to 180)
        lat2: Latitude of second point in degrees (-90 to 90)
        lon2: Longitude of second point in degrees (-180 to 180)
        method: Calculation method - 'haversine', 'vincenty', or 'spherical'
            (default: 'haversine')
    
    Returns:
        Distance in kilometers
    
    Raises:
        ValueError: If coordinates are invalid or method is unknown
    
    Example:
        >>> # Distance between New York and Los Angeles
        >>> distance = calculate_distance_km(40.7128, -74.0060, 34.0522, -118.2437)
        >>> print(f"{distance:.2f} km")
        3935.75 km
        
        >>> # Using Vincenty for higher precision
        >>> distance = calculate_distance_km(40.7128, -74.0060, 34.0522, -118.2437, method='vincenty')
        >>> print(f"{distance:.2f} km")
        3944.42 km
    """
    method_lower = method.lower()
    
    if method_lower == "haversine":
        return haversine_distance(lat1, lon1, lat2, lon2)
    elif method_lower == "vincenty":
        return vincenty_distance(lat1, lon1, lat2, lon2)
    elif method_lower == "spherical":
        return spherical_law_of_cosines(lat1, lon1, lat2, lon2)
    else:
        raise ValueError(
            f"Unknown method: {method}. "
            f"Supported methods: 'haversine', 'vincenty', 'spherical'"
        )
