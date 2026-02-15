"""
Random coordinate generation module.

This module provides functionality to generate random coordinates within:
- Countries (by name or ISO code)
- Continents
- Circular areas (by center point and radius)

Features:
- Uniform distribution across regions
- Point-in-polygon validation
- Support for multi-polygon regions (islands, territories)
- Reproducible results with seed support
"""

import random
import math
from typing import List, Tuple, Union, Optional, Literal
from dataclasses import dataclass
from .api import resolve
from .data_loader import get_loader
from .pip import point_in_polygon_with_holes
from .polygon_utils import calculate_bounding_box


@dataclass
class RandomCoordinateResult:
    """Result object for random coordinate generation."""
    coordinates: List[Tuple[float, float]]
    region: str
    region_type: Literal['country', 'continent', 'area']
    total_requested: int
    total_generated: int
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'coordinates': self.coordinates,
            'region': self.region,
            'region_type': self.region_type,
            'total_requested': self.total_requested,
            'total_generated': self.total_generated
        }
    
    def __repr__(self) -> str:
        return (
            f"RandomCoordinateResult("
            f"region={self.region!r}, "
            f"type={self.region_type}, "
            f"generated={self.total_generated}/{self.total_requested}"
            f")"
        )


def _detect_region_type(region: str, data_dir: Optional[str] = None) -> Literal['country', 'continent']:
    """
    Detect if region is a country or continent.
    
    Args:
        region: Region name or ISO code
        data_dir: Optional custom data directory path
    
    Returns:
        'country' or 'continent'
    
    Raises:
        ValueError: If region cannot be determined
    """
    # Try resolving as country first
    try:
        result = resolve(region, data_dir=data_dir)
        # If it has latitude/longitude, it's a country (reverse geocoding result)
        if hasattr(result, 'latitude') and result.latitude is not None:
            return 'country'
    except (ValueError, AttributeError):
        pass
    
    # Check if it's a known continent
    known_continents = {
        'africa', 'asia', 'europe', 'north america', 'south america',
        'oceania', 'antarctica', 'australia'
    }
    
    if region.lower().strip() in known_continents:
        return 'continent'
    
    # Default to country (will fail later if invalid)
    return 'country'


def _get_country_polygons(
    country_input: str,
    data_dir: Optional[str] = None
) -> List[Tuple[List[Tuple[float, float]], List[List[Tuple[float, float]]]]]:
    """
    Get polygon data for a country.
    
    Args:
        country_input: Country name or ISO code
        data_dir: Optional custom data directory path
    
    Returns:
        List of (exterior, holes) tuples for all polygons in the country
    """
    from .reverse_resolver import _find_country_by_name_or_iso
    
    loader = get_loader(data_dir)
    result = _find_country_by_name_or_iso(country_input, data_dir)
    
    if result is None:
        raise ValueError(f"Country not found: {country_input}")
    
    country_id, _ = result
    polygon_data = loader.get_polygon(country_id)
    
    if not polygon_data:
        raise ValueError(f"No polygon data found for country: {country_input}")
    
    polygons = []
    
    # Handle MultiPolygon
    is_multi = polygon_data.get('multi', False)
    exteriors_data = polygon_data.get('exteriors', [])
    
    if is_multi and exteriors_data:
        # MultiPolygon: multiple exteriors
        for exterior in exteriors_data:
            exterior_tuples = [(p[0], p[1]) for p in exterior]
            holes = polygon_data.get('holes', [])
            holes_tuples = [[(p[0], p[1]) for p in hole] for hole in holes] if holes else []
            polygons.append((exterior_tuples, holes_tuples))
    else:
        # Single polygon
        exterior = polygon_data.get('exterior', [])
        if exterior:
            exterior_tuples = [(p[0], p[1]) for p in exterior]
            holes = polygon_data.get('holes', [])
            holes_tuples = [[(p[0], p[1]) for p in hole] for hole in holes] if holes else []
            polygons.append((exterior_tuples, holes_tuples))
    
    if not polygons:
        raise ValueError(f"No valid polygons found for country: {country_input}")
    
    return polygons


def _get_continent_polygons(
    continent_name: str,
    data_dir: Optional[str] = None
) -> List[Tuple[List[Tuple[float, float]], List[List[Tuple[float, float]]]]]:
    """
    Get polygon data for all countries in a continent.
    
    Args:
        continent_name: Continent name
        data_dir: Optional custom data directory path
    
    Returns:
        List of (exterior, holes) tuples for all polygons in the continent
    """
    from .data_loader import get_loader
    
    loader = get_loader(data_dir)
    metadata = loader.metadata
    
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
    
    all_polygons = []
    
    # Collect polygons from all countries in this continent
    for country_id, country_meta in metadata.items():
        country_continent = country_meta.get('continent', '')
        if country_continent and country_continent.lower() == continent_standard.lower():
            polygon_data = loader.get_polygon(country_id)
            if not polygon_data:
                continue
            
            # Handle MultiPolygon
            is_multi = polygon_data.get('multi', False)
            exteriors_data = polygon_data.get('exteriors', [])
            
            if is_multi and exteriors_data:
                for exterior in exteriors_data:
                    exterior_tuples = [(p[0], p[1]) for p in exterior]
                    holes = polygon_data.get('holes', [])
                    holes_tuples = [[(p[0], p[1]) for p in hole] for hole in holes] if holes else []
                    all_polygons.append((exterior_tuples, holes_tuples))
            else:
                exterior = polygon_data.get('exterior', [])
                if exterior:
                    exterior_tuples = [(p[0], p[1]) for p in exterior]
                    holes = polygon_data.get('holes', [])
                    holes_tuples = [[(p[0], p[1]) for p in hole] for hole in holes] if holes else []
                    all_polygons.append((exterior_tuples, holes_tuples))
    
    if not all_polygons:
        raise ValueError(f"No countries found for continent: {continent_name}")
    
    return all_polygons


def _calculate_bounding_box_for_polygons(
    polygons: List[Tuple[List[Tuple[float, float]], List[List[Tuple[float, float]]]]]
) -> Tuple[float, float, float, float]:
    """
    Calculate combined bounding box for multiple polygons.
    
    Args:
        polygons: List of (exterior, holes) tuples
    
    Returns:
        Tuple of (min_lat, max_lat, min_lon, max_lon)
    """
    if not polygons:
        raise ValueError("No polygons provided")
    
    min_lat = 90.0
    max_lat = -90.0
    min_lon = 180.0
    max_lon = -180.0
    
    for exterior, _ in polygons:
        if not exterior:
            continue
        
        bbox = calculate_bounding_box(exterior)
        poly_min_lat, poly_max_lat, poly_min_lon, poly_max_lon = bbox
        
        min_lat = min(min_lat, poly_min_lat)
        max_lat = max(max_lat, poly_max_lat)
        min_lon = min(min_lon, poly_min_lon)
        max_lon = max(max_lon, poly_max_lon)
    
    return (min_lat, max_lat, min_lon, max_lon)


def _generate_single_coordinate_in_polygons(
    polygons: List[Tuple[List[Tuple[float, float]], List[List[Tuple[float, float]]]]],
    bounding_box: Tuple[float, float, float, float],
    max_attempts: int = 1000
) -> Optional[Tuple[float, float]]:
    """
    Generate a single random coordinate within polygons using rejection sampling.
    
    Args:
        polygons: List of (exterior, holes) tuples
        bounding_box: (min_lat, max_lat, min_lon, max_lon)
        max_attempts: Maximum number of attempts before giving up
    
    Returns:
        Tuple of (lat, lon) or None if generation failed
    """
    min_lat, max_lat, min_lon, max_lon = bounding_box
    
    for attempt in range(max_attempts):
        # Generate random point in bounding box
        lat = random.uniform(min_lat, max_lat)
        lon = random.uniform(min_lon, max_lon)
        point = (lat, lon)
        
        # Check if point is in any polygon
        for exterior, holes in polygons:
            if point_in_polygon_with_holes(point, exterior, holes if holes else None):
                return point
    
    # Failed to generate after max_attempts
    return None


def generate_random_coordinates_by_region(
    region: str,
    count: int,
    region_type: Optional[Literal['country', 'continent']] = None,
    seed: Optional[int] = None,
    max_attempts: int = 1000,
    data_dir: Optional[str] = None
) -> RandomCoordinateResult:
    """
    Generate random coordinates within a country or continent.
    
    Uses rejection sampling: generates random points in the bounding box
    and validates them using point-in-polygon checks. This ensures all
    generated coordinates are actually within the region.
    
    Args:
        region: Country name, ISO code, or continent name
        count: Number of coordinates to generate
        region_type: 'country' or 'continent' (auto-detected if None)
        seed: Random seed for reproducibility
        max_attempts: Maximum attempts per coordinate (to avoid infinite loops)
        data_dir: Optional custom data directory path
    
    Returns:
        RandomCoordinateResult with generated coordinates
    
    Raises:
        ValueError: If region is invalid or cannot generate enough coordinates
    
    Example:
        >>> # Generate 10 random coordinates in United States
        >>> result = generate_random_coordinates_by_region("United States", 10)
        >>> print(f"Generated {result.total_generated} coordinates")
        >>> for lat, lon in result.coordinates:
        ...     print(f"  ({lat:.4f}, {lon:.4f})")
        
        >>> # Generate coordinates in a continent
        >>> result = generate_random_coordinates_by_region("Europe", 50)
        >>> print(f"Generated {result.total_generated} coordinates in Europe")
        
        >>> # With seed for reproducibility
        >>> result1 = generate_random_coordinates_by_region("US", 10, seed=42)
        >>> result2 = generate_random_coordinates_by_region("US", 10, seed=42)
        >>> assert result1.coordinates == result2.coordinates  # Same results
    """
    if count <= 0:
        raise ValueError(f"Count must be positive, got {count}")
    
    # Set random seed for reproducibility
    if seed is not None:
        random.seed(seed)
    
    # Determine region type if not specified
    if region_type is None:
        region_type = _detect_region_type(region, data_dir)
    
    # Get polygon data for region
    if region_type == 'country':
        polygons = _get_country_polygons(region, data_dir)
    elif region_type == 'continent':
        polygons = _get_continent_polygons(region, data_dir)
    else:
        raise ValueError(f"Invalid region_type: {region_type}. Must be 'country' or 'continent'")
    
    if not polygons:
        raise ValueError(f"No polygons found for region: {region}")
    
    # Calculate bounding box for efficient generation
    bounding_box = _calculate_bounding_box_for_polygons(polygons)
    
    # Generate random coordinates
    coordinates = []
    failed_count = 0
    
    for i in range(count):
        coord = _generate_single_coordinate_in_polygons(polygons, bounding_box, max_attempts)
        if coord:
            coordinates.append(coord)
        else:
            failed_count += 1
            # If too many failures, raise error
            if failed_count > count * 0.5:  # More than 50% failure rate
                raise ValueError(
                    f"Failed to generate coordinates for region '{region}'. "
                    f"Only generated {len(coordinates)}/{count} coordinates. "
                    f"This may indicate the region is too small or complex. "
                    f"Try increasing max_attempts or using a different region."
                )
    
    return RandomCoordinateResult(
        coordinates=coordinates,
        region=region,
        region_type=region_type,
        total_requested=count,
        total_generated=len(coordinates)
    )


def _meters_to_degrees(meters: float, latitude: float) -> float:
    """
    Convert meters to degrees, accounting for Earth's curvature.
    
    At equator: 1 degree latitude ≈ 111 km
    At poles: 1 degree latitude ≈ 111 km (same)
    Longitude varies: 1 degree longitude ≈ 111 km * cos(latitude)
    
    Args:
        meters: Distance in meters
        latitude: Latitude for longitude conversion (degrees)
    
    Returns:
        Approximate distance in degrees
    """
    # Average degree size (latitude)
    # 1 degree latitude ≈ 111,000 meters everywhere
    degrees_lat = meters / 111000.0
    
    # For longitude, account for latitude
    # 1 degree longitude ≈ 111,000 * cos(latitude) meters
    lat_rad = math.radians(latitude)
    degrees_lon = meters / (111000.0 * abs(math.cos(lat_rad)))
    
    # Return average (for circular area, use the larger value to ensure coverage)
    return max(degrees_lat, degrees_lon)


def _generate_coordinate_in_circle(
    center: Tuple[float, float],
    radius_deg: float
) -> Tuple[float, float]:
    """
    Generate random coordinate within circle using polar coordinates.
    
    Uses uniform distribution in polar space, then converts to lat/lon.
    This ensures uniform distribution within the circular area.
    
    Args:
        center: Center point (lat, lon)
        radius_deg: Radius in degrees
    
    Returns:
        Random coordinate (lat, lon) within the circle
    """
    center_lat, center_lon = center
    
    # Generate random angle and distance
    angle = random.uniform(0, 2 * math.pi)
    
    # For uniform distribution in circle, use sqrt of uniform random for radius
    # (simple uniform r would cluster points near center)
    r = math.sqrt(random.uniform(0, 1)) * radius_deg
    
    # Convert polar to lat/lon offset
    # Approximate: treat as flat plane (good for small radii)
    lat_offset = r * math.cos(angle)
    lon_offset = r * math.sin(angle)
    
    # Account for longitude convergence at poles
    # Longitude degrees get smaller as we move away from equator
    lat_rad = math.radians(center_lat)
    lon_offset = lon_offset / abs(math.cos(lat_rad)) if abs(math.cos(lat_rad)) > 0.01 else lon_offset
    
    # Calculate new coordinates
    new_lat = center_lat + lat_offset
    new_lon = center_lon + lon_offset
    
    # Normalize coordinates
    new_lat = max(-90.0, min(90.0, new_lat))
    new_lon = ((new_lon + 180.0) % 360.0) - 180.0
    
    return (new_lat, new_lon)


def generate_random_coordinates_by_area(
    center: Tuple[float, float],
    radius: float,
    count: int,
    radius_unit: Literal['m', 'km', 'mile', 'degree'] = 'm',
    seed: Optional[int] = None
) -> RandomCoordinateResult:
    """
    Generate random coordinates within a circular area.
    
    Uses polar coordinate generation with uniform distribution to ensure
    coordinates are evenly distributed within the circular area.
    
    Args:
        center: Center point (latitude, longitude)
        radius: Radius of the circular area
        count: Number of coordinates to generate
        radius_unit: Unit for radius ('m', 'km', 'mile', 'degree')
        seed: Random seed for reproducibility
    
    Returns:
        RandomCoordinateResult with generated coordinates
    
    Raises:
        ValueError: If inputs are invalid
    
    Example:
        >>> # Generate 10 random coordinates within 10km of NYC
        >>> result = generate_random_coordinates_by_area(
        ...     (40.7128, -74.0060),  # NYC
        ...     10,  # 10 km
        ...     10,
        ...     radius_unit='km'
        ... )
        >>> print(f"Generated {result.total_generated} coordinates")
        >>> for lat, lon in result.coordinates:
        ...     print(f"  ({lat:.4f}, {lon:.4f})")
        
        >>> # With seed for reproducibility
        >>> result1 = generate_random_coordinates_by_area(
        ...     (40.7128, -74.0060), 10, 5, radius_unit='km', seed=42
        ... )
        >>> result2 = generate_random_coordinates_by_area(
        ...     (40.7128, -74.0060), 10, 5, radius_unit='km', seed=42
        ... )
        >>> assert result1.coordinates == result2.coordinates  # Same results
    """
    if count <= 0:
        raise ValueError(f"Count must be positive, got {count}")
    
    if not (-90 <= center[0] <= 90) or not (-180 <= center[1] <= 180):
        raise ValueError(
            f"Invalid center coordinates: {center}. "
            f"Latitude must be -90 to 90, longitude must be -180 to 180."
        )
    
    if radius < 0:
        raise ValueError(f"Radius must be non-negative, got {radius}")
    
    # Set random seed for reproducibility
    if seed is not None:
        random.seed(seed)
    
    # Convert radius to degrees
    if radius_unit == 'degree':
        radius_deg = radius
    else:
        # Convert to meters first
        if radius_unit == 'm' or radius_unit == 'meter' or radius_unit == 'meters':
            radius_m = radius
        elif radius_unit == 'km' or radius_unit == 'kilometer' or radius_unit == 'kilometers':
            radius_m = radius * 1000.0
        elif radius_unit == 'mile' or radius_unit == 'miles' or radius_unit == 'mi':
            radius_m = radius * 1609.34
        else:
            raise ValueError(
                f"Unknown radius_unit: {radius_unit}. "
                f"Supported: 'm', 'km', 'mile', 'degree'"
            )
        
        # Convert meters to degrees
        radius_deg = _meters_to_degrees(radius_m, center[0])
    
    # Generate random coordinates
    coordinates = []
    for _ in range(count):
        coord = _generate_coordinate_in_circle(center, radius_deg)
        coordinates.append(coord)
    
    return RandomCoordinateResult(
        coordinates=coordinates,
        region=f"Area around ({center[0]}, {center[1]})",
        region_type='area',
        total_requested=count,
        total_generated=len(coordinates)
    )
