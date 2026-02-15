"""
Geo-fencing module for proximity detection and movement tracking.

This module provides functionality to:
- Detect when a location is within a geofence (circular area around destination)
- Track movement direction (inward/outward relative to destination)
- Generate alerts based on configurable thresholds
- Support both stateless and stateful monitoring

Features:
- Configurable geofence radius
- Multiple radius units (meters, kilometers, miles)
- State tracking (outside, approaching, inside, leaving)
- Alert generation (reached, entered, exited, approaching, leaving)
- Flexible input types (coordinates, country names, ISO codes)
"""

from typing import Optional, Tuple, Union, List, Literal
from dataclasses import dataclass
from enum import Enum
from .distance import calculate_distance, normalize_location


class GeofenceState(Enum):
    """Geofence state enumeration."""
    OUTSIDE = "outside"  # Location is outside the geofence
    APPROACHING = "approaching"  # Location is outside but moving closer
    INSIDE = "inside"  # Location is inside the geofence
    LEAVING = "leaving"  # Location is inside but moving away


@dataclass
class GeofenceAlert:
    """Alert object for geofence events."""
    alert_type: Literal['reached', 'entered', 'exited', 'approaching', 'leaving']
    distance: float
    unit: str  # 'm', 'km', or 'mile'
    state: GeofenceState
    previous_distance: Optional[float] = None
    distance_change: Optional[float] = None
    distance_change_percent: Optional[float] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'alert_type': self.alert_type,
            'distance': self.distance,
            'unit': self.unit,
            'state': self.state.value,
            'previous_distance': self.previous_distance,
            'distance_change': self.distance_change,
            'distance_change_percent': self.distance_change_percent
        }
    
    def __repr__(self) -> str:
        return (
            f"GeofenceAlert("
            f"type={self.alert_type}, "
            f"distance={self.distance:.2f} {self.unit}, "
            f"state={self.state.value}"
            f")"
        )


@dataclass
class GeofenceResult:
    """Result object for geofence checks."""
    is_inside: bool
    distance: float
    unit: str  # 'm', 'km', or 'mile'
    state: GeofenceState
    alerts: List[GeofenceAlert]
    current_location: Union[Tuple[float, float], str]
    destination: Union[Tuple[float, float], str]
    radius: float
    radius_unit: str
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'is_inside': self.is_inside,
            'distance': self.distance,
            'unit': self.unit,
            'state': self.state.value,
            'alerts': [alert.to_dict() for alert in self.alerts],
            'current_location': self.current_location,
            'destination': self.destination,
            'radius': self.radius,
            'radius_unit': self.radius_unit
        }
    
    def __repr__(self) -> str:
        return (
            f"GeofenceResult("
            f"is_inside={self.is_inside}, "
            f"distance={self.distance:.2f} {self.unit}, "
            f"state={self.state.value}, "
            f"alerts={len(self.alerts)}"
            f")"
        )


@dataclass
class GeofenceConfig:
    """Configuration for geofence alerts and behavior."""
    radius: float  # Detection radius
    radius_unit: Literal['m', 'km', 'mile'] = 'm'  # Unit for radius
    
    # Alert thresholds
    reached_threshold: float = 0.0  # Distance to trigger "reached" alert (in same unit as radius)
    approaching_threshold_percent: Optional[float] = None  # Distance change % to trigger "approaching"
    leaving_threshold_percent: Optional[float] = None  # Distance change % to trigger "leaving"
    
    # State transition thresholds (to prevent flickering)
    inside_buffer: float = 0.0  # Buffer for "inside" state (in same unit as radius)
    outside_buffer: float = 0.0  # Buffer for "outside" state (in same unit as radius)


def _convert_to_meters(value: float, unit: str) -> float:
    """
    Convert distance value to meters.
    
    Args:
        value: Distance value
        unit: Unit ('m', 'km', 'mile')
    
    Returns:
        Distance in meters
    """
    unit_lower = unit.lower()
    if unit_lower == 'm' or unit_lower == 'meter' or unit_lower == 'meters':
        return value
    elif unit_lower == 'km' or unit_lower == 'kilometer' or unit_lower == 'kilometers':
        return value * 1000.0
    elif unit_lower == 'mile' or unit_lower == 'miles' or unit_lower == 'mi':
        return value * 1609.34
    else:
        raise ValueError(f"Unknown unit: {unit}. Supported: 'm', 'km', 'mile'")


def _convert_from_meters(value: float, unit: str) -> float:
    """
    Convert distance value from meters to specified unit.
    
    Args:
        value: Distance in meters
        unit: Target unit ('m', 'km', 'mile')
    
    Returns:
        Distance in target unit
    """
    unit_lower = unit.lower()
    if unit_lower == 'm' or unit_lower == 'meter' or unit_lower == 'meters':
        return value
    elif unit_lower == 'km' or unit_lower == 'kilometer' or unit_lower == 'kilometers':
        return value / 1000.0
    elif unit_lower == 'mile' or unit_lower == 'miles' or unit_lower == 'mi':
        return value / 1609.34
    else:
        raise ValueError(f"Unknown unit: {unit}. Supported: 'm', 'km', 'mile'")


def _determine_state(
    is_inside: bool,
    previous_state: Optional[GeofenceState],
    distance_m: float,
    radius_m: float,
    inside_buffer_m: float,
    outside_buffer_m: float,
    previous_distance_m: Optional[float]
) -> GeofenceState:
    """
    Determine current geofence state based on position and previous state.
    
    Args:
        is_inside: Whether location is currently inside geofence
        previous_state: Previous geofence state (None for first check)
        distance_m: Current distance in meters
        radius_m: Geofence radius in meters
        inside_buffer_m: Buffer for inside state in meters
        outside_buffer_m: Buffer for outside state in meters
        previous_distance_m: Previous distance in meters (None for first check)
    
    Returns:
        Current geofence state
    """
    # Apply buffers to prevent flickering
    effective_inside_threshold = radius_m + inside_buffer_m
    effective_outside_threshold = radius_m - outside_buffer_m
    
    # Determine if actually inside (with buffers)
    actually_inside = distance_m <= effective_inside_threshold
    
    # If no previous state, determine based on current position
    if previous_state is None:
        if actually_inside:
            return GeofenceState.INSIDE
        else:
            return GeofenceState.OUTSIDE
    
    # If we have previous distance, check movement direction
    if previous_distance_m is not None:
        distance_change = previous_distance_m - distance_m  # Positive = getting closer
        distance_change_percent = (distance_change / previous_distance_m * 100.0) if previous_distance_m > 0 else 0.0
        
        if actually_inside:
            # Inside geofence
            if previous_state == GeofenceState.OUTSIDE or previous_state == GeofenceState.APPROACHING:
                # Just entered
                return GeofenceState.INSIDE
            elif distance_change > 0:
                # Moving closer while inside (shouldn't happen, but handle it)
                return GeofenceState.INSIDE
            elif distance_change < 0:
                # Moving away while inside
                return GeofenceState.LEAVING
            else:
                return GeofenceState.INSIDE
        else:
            # Outside geofence
            if previous_state == GeofenceState.INSIDE or previous_state == GeofenceState.LEAVING:
                # Just exited
                return GeofenceState.OUTSIDE
            elif distance_change < 0:
                # Moving away while outside
                return GeofenceState.OUTSIDE
            elif distance_change > 0:
                # Moving closer while outside
                return GeofenceState.APPROACHING
            else:
                return GeofenceState.OUTSIDE
    
    # Fallback: determine based on current position only
    if actually_inside:
        return GeofenceState.INSIDE
    else:
        return GeofenceState.OUTSIDE


def _generate_alerts(
    state: GeofenceState,
    previous_state: Optional[GeofenceState],
    distance: float,
    distance_unit: str,
    radius: float,
    radius_unit: str,
    config: GeofenceConfig,
    previous_distance: Optional[float]
) -> List[GeofenceAlert]:
    """
    Generate alerts based on state transitions and thresholds.
    
    Args:
        state: Current geofence state
        previous_state: Previous geofence state
        distance: Current distance
        distance_unit: Unit of distance
        radius: Geofence radius
        radius_unit: Unit of radius
        config: Geofence configuration
        previous_distance: Previous distance (None for first check)
    
    Returns:
        List of alerts generated
    """
    alerts = []
    
    # Convert everything to meters for comparison
    distance_m = _convert_to_meters(distance, distance_unit)
    radius_m = _convert_to_meters(radius, radius_unit)
    reached_threshold_m = _convert_to_meters(config.reached_threshold, radius_unit)
    previous_distance_m = _convert_to_meters(previous_distance, distance_unit) if previous_distance is not None else None
    
    # State transition alerts
    if previous_state is not None:
        if previous_state != state:
            if state == GeofenceState.INSIDE and (previous_state == GeofenceState.OUTSIDE or previous_state == GeofenceState.APPROACHING):
                # Entered geofence
                alerts.append(GeofenceAlert(
                    alert_type='entered',
                    distance=distance,
                    unit=distance_unit,
                    state=state,
                    previous_distance=previous_distance,
                    distance_change=previous_distance - distance if previous_distance is not None else None,
                    distance_change_percent=((previous_distance - distance) / previous_distance * 100.0) if previous_distance is not None and previous_distance > 0 else None
                ))
            
            elif state == GeofenceState.OUTSIDE and (previous_state == GeofenceState.INSIDE or previous_state == GeofenceState.LEAVING):
                # Exited geofence
                alerts.append(GeofenceAlert(
                    alert_type='exited',
                    distance=distance,
                    unit=distance_unit,
                    state=state,
                    previous_distance=previous_distance,
                    distance_change=distance - previous_distance if previous_distance is not None else None,
                    distance_change_percent=((distance - previous_distance) / previous_distance * 100.0) if previous_distance is not None and previous_distance > 0 else None
                ))
    
    # Reached alert (within threshold)
    if distance_m <= reached_threshold_m and state == GeofenceState.INSIDE:
        alerts.append(GeofenceAlert(
            alert_type='reached',
            distance=distance,
            unit=distance_unit,
            state=state,
            previous_distance=previous_distance
        ))
    
    # Approaching alert (moving closer by threshold %)
    if state == GeofenceState.APPROACHING and previous_distance_m is not None:
        if config.approaching_threshold_percent is not None:
            distance_change_percent = ((previous_distance_m - distance_m) / previous_distance_m * 100.0) if previous_distance_m > 0 else 0.0
            if distance_change_percent >= config.approaching_threshold_percent:
                alerts.append(GeofenceAlert(
                    alert_type='approaching',
                    distance=distance,
                    unit=distance_unit,
                    state=state,
                    previous_distance=previous_distance,
                    distance_change=previous_distance - distance if previous_distance is not None else None,
                    distance_change_percent=distance_change_percent
                ))
    
    # Leaving alert (moving away by threshold %)
    if state == GeofenceState.LEAVING and previous_distance_m is not None:
        if config.leaving_threshold_percent is not None:
            distance_change_percent = ((distance_m - previous_distance_m) / previous_distance_m * 100.0) if previous_distance_m > 0 else 0.0
            if distance_change_percent >= config.leaving_threshold_percent:
                alerts.append(GeofenceAlert(
                    alert_type='leaving',
                    distance=distance,
                    unit=distance_unit,
                    state=state,
                    previous_distance=previous_distance,
                    distance_change=distance - previous_distance if previous_distance is not None else None,
                    distance_change_percent=distance_change_percent
                ))
    
    return alerts


class GeofenceMonitor:
    """
    Geofence monitor for tracking location relative to destination.
    
    Maintains state between calls to detect state transitions and generate alerts.
    This is the stateful API - use this when you want to track location over time.
    
    Example:
        >>> from geo_intel_offline.geofence import GeofenceMonitor, GeofenceConfig
        >>> 
        >>> config = GeofenceConfig(
        ...     radius=1000,  # 1 km radius
        ...     radius_unit='m',
        ...     reached_threshold=100,  # Alert when within 100m
        ...     approaching_threshold_percent=10  # Alert when 10% closer
        ... )
        >>> monitor = GeofenceMonitor(config)
        >>> 
        >>> # First check
        >>> result = monitor.check((40.7128, -74.0060), (40.7130, -74.0060))
        >>> print(result.state)  # OUTSIDE or INSIDE
        >>> 
        >>> # Subsequent checks (state is tracked)
        >>> result = monitor.check((40.7129, -74.0060), (40.7130, -74.0060))
        >>> print(result.alerts)  # May include 'approaching' or 'entered' alerts
    """
    
    def __init__(self, config: GeofenceConfig):
        """
        Initialize geofence monitor.
        
        Args:
            config: Geofence configuration
        """
        self.config = config
        self.previous_state: Optional[GeofenceState] = None
        self.previous_distance: Optional[float] = None
        self.previous_distance_unit: Optional[str] = None
    
    def check(
        self,
        current_location: Union[Tuple[float, float], str],
        destination: Union[Tuple[float, float], str],
        data_dir: Optional[str] = None
    ) -> GeofenceResult:
        """
        Check current location against geofence.
        
        Args:
            current_location: Current location - can be:
                - Tuple[float, float]: (latitude, longitude)
                - str: Country name, ISO code, or location identifier
            destination: Destination location - can be:
                - Tuple[float, float]: (latitude, longitude)
                - str: Country name, ISO code, or location identifier
            data_dir: Optional custom data directory path
        
        Returns:
            GeofenceResult with current state and alerts
        """
        # Step 1: Calculate current distance
        distance_result = calculate_distance(
            current_location,
            destination,
            data_dir=data_dir
        )
        current_distance = distance_result.distance
        current_distance_unit = distance_result.unit
        
        # Convert to meters for comparison
        current_distance_m = _convert_to_meters(current_distance, current_distance_unit)
        
        # Convert radius to meters
        radius_m = _convert_to_meters(self.config.radius, self.config.radius_unit)
        
        # Convert buffers to meters
        inside_buffer_m = _convert_to_meters(self.config.inside_buffer, self.config.radius_unit)
        outside_buffer_m = _convert_to_meters(self.config.outside_buffer, self.config.radius_unit)
        
        # Step 2: Determine if inside geofence (with buffers)
        effective_inside_threshold = radius_m + inside_buffer_m
        is_inside = current_distance_m <= effective_inside_threshold
        
        # Step 3: Determine state
        previous_distance_m = _convert_to_meters(self.previous_distance, self.previous_distance_unit) if self.previous_distance is not None and self.previous_distance_unit is not None else None
        
        state = _determine_state(
            is_inside=is_inside,
            previous_state=self.previous_state,
            distance_m=current_distance_m,
            radius_m=radius_m,
            inside_buffer_m=inside_buffer_m,
            outside_buffer_m=outside_buffer_m,
            previous_distance_m=previous_distance_m
        )
        
        # Step 4: Generate alerts
        alerts = _generate_alerts(
            state=state,
            previous_state=self.previous_state,
            distance=current_distance,
            distance_unit=current_distance_unit,
            radius=self.config.radius,
            radius_unit=self.config.radius_unit,
            config=self.config,
            previous_distance=self.previous_distance
        )
        
        # Step 5: Update previous state
        self.previous_state = state
        self.previous_distance = current_distance
        self.previous_distance_unit = current_distance_unit
        
        return GeofenceResult(
            is_inside=is_inside,
            distance=current_distance,
            unit=current_distance_unit,
            state=state,
            alerts=alerts,
            current_location=current_location,
            destination=destination,
            radius=self.config.radius,
            radius_unit=self.config.radius_unit
        )
    
    def reset(self):
        """Reset monitor state (clear previous state and distance)."""
        self.previous_state = None
        self.previous_distance = None
        self.previous_distance_unit = None


def check_geofence(
    current_location: Union[Tuple[float, float], str],
    destination: Union[Tuple[float, float], str],
    radius: float,
    radius_unit: Literal['m', 'km', 'mile'] = 'm',
    previous_distance: Optional[float] = None,
    previous_state: Optional[GeofenceState] = None,
    previous_distance_unit: Optional[str] = None,
    reached_threshold: float = 0.0,
    approaching_threshold_percent: Optional[float] = None,
    leaving_threshold_percent: Optional[float] = None,
    inside_buffer: float = 0.0,
    outside_buffer: float = 0.0,
    data_dir: Optional[str] = None
) -> GeofenceResult:
    """
    Single-call geofence check (stateless).
    
    This is a convenience function for one-off geofence checks. For continuous
    monitoring with state tracking, use GeofenceMonitor class instead.
    
    Args:
        current_location: Current location - can be:
            - Tuple[float, float]: (latitude, longitude)
            - str: Country name, ISO code, or location identifier
        destination: Destination location - can be:
            - Tuple[float, float]: (latitude, longitude)
            - str: Country name, ISO code, or location identifier
        radius: Geofence radius
        radius_unit: Unit for radius ('m', 'km', 'mile')
        previous_distance: Previous distance (for state tracking, optional)
        previous_state: Previous state (for state tracking, optional)
        previous_distance_unit: Unit of previous_distance (required if previous_distance provided)
        reached_threshold: Distance threshold to trigger "reached" alert (in same unit as radius)
        approaching_threshold_percent: Distance change % to trigger "approaching" alert
        leaving_threshold_percent: Distance change % to trigger "leaving" alert
        inside_buffer: Buffer for "inside" state (to prevent flickering, in same unit as radius)
        outside_buffer: Buffer for "outside" state (to prevent flickering, in same unit as radius)
        data_dir: Optional custom data directory path
    
    Returns:
        GeofenceResult with current state and alerts
    
    Example:
        >>> from geo_intel_offline.geofence import check_geofence
        >>> 
        >>> # Simple check
        >>> result = check_geofence(
        ...     (40.7128, -74.0060),  # Current location
        ...     (40.7130, -74.0060),  # Destination
        ...     radius=1000,  # 1 km radius
        ...     radius_unit='m'
        ... )
        >>> print(result.is_inside)  # True or False
        >>> print(result.state)  # OUTSIDE, APPROACHING, INSIDE, or LEAVING
        >>> 
        >>> # With state tracking
        >>> result1 = check_geofence((40.7128, -74.0060), (40.7130, -74.0060), 1000, 'm')
        >>> result2 = check_geofence(
        ...     (40.7129, -74.0060), (40.7130, -74.0060), 1000, 'm',
        ...     previous_distance=result1.distance,
        ...     previous_state=result1.state,
        ...     previous_distance_unit=result1.unit
        ... )
        >>> print(result2.alerts)  # May include state transition alerts
    """
    config = GeofenceConfig(
        radius=radius,
        radius_unit=radius_unit,
        reached_threshold=reached_threshold,
        approaching_threshold_percent=approaching_threshold_percent,
        leaving_threshold_percent=leaving_threshold_percent,
        inside_buffer=inside_buffer,
        outside_buffer=outside_buffer
    )
    
    monitor = GeofenceMonitor(config)
    
    # Set previous state if provided
    if previous_distance is not None:
        monitor.previous_distance = previous_distance
        monitor.previous_distance_unit = previous_distance_unit or 'km'  # Default to km if not specified
    
    if previous_state is not None:
        monitor.previous_state = previous_state
    
    return monitor.check(current_location, destination, data_dir=data_dir)
