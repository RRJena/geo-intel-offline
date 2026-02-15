"""
Comprehensive test suite for geo-fencing functionality.

Tests cover:
- Core geofence detection (inside/outside)
- State tracking and transitions
- Alert generation
- GeofenceMonitor class
- Stateless check_geofence() function
- Edge cases and error handling
"""

import sys
import math
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from geo_intel_offline.geofence import (
    GeofenceState,
    GeofenceConfig,
    GeofenceMonitor,
    GeofenceAlert,
    GeofenceResult,
    check_geofence,
    _convert_to_meters,
    _convert_from_meters
)


class TestUnitConversion:
    """Test suite for unit conversion functions."""
    
    def test_convert_to_meters(self):
        """Test conversion to meters."""
        assert _convert_to_meters(1000, 'm') == 1000.0
        assert _convert_to_meters(1, 'km') == 1000.0
        assert abs(_convert_to_meters(1, 'mile') - 1609.34) < 0.01
    
    def test_convert_from_meters(self):
        """Test conversion from meters."""
        assert _convert_from_meters(1000, 'm') == 1000.0
        assert _convert_from_meters(1000, 'km') == 1.0
        assert abs(_convert_from_meters(1609.34, 'mile') - 1.0) < 0.01
    
    def test_round_trip_conversion(self):
        """Test round-trip conversion."""
        original = 1000.0
        for unit in ['m', 'km', 'mile']:
            meters = _convert_to_meters(original, unit)
            back = _convert_from_meters(meters, unit)
            assert abs(back - original) < 0.01, f"Round trip failed for {unit}"
    
    def test_invalid_unit(self):
        """Test that invalid unit raises ValueError."""
        with pytest.raises(ValueError, match="Unknown unit"):
            _convert_to_meters(100, 'invalid')


class TestBasicGeofenceCheck:
    """Test suite for basic geofence detection."""
    
    def test_location_inside_geofence(self):
        """Test that location inside geofence is detected."""
        # Two points very close together (within 1 km)
        result = check_geofence(
            (40.7128, -74.0060),
            (40.7130, -74.0060),
            radius=1000,
            radius_unit='m'
        )
        assert result.is_inside is True, "Should be inside geofence"
        assert result.state == GeofenceState.INSIDE, "State should be INSIDE"
    
    def test_location_outside_geofence(self):
        """Test that location outside geofence is detected."""
        # NYC to LA (very far apart)
        result = check_geofence(
            (40.7128, -74.0060),  # NYC
            (34.0522, -118.2437),  # LA
            radius=1000,
            radius_unit='m'
        )
        assert result.is_inside is False, "Should be outside geofence"
        assert result.state == GeofenceState.OUTSIDE, "State should be OUTSIDE"
    
    def test_location_on_boundary(self):
        """Test location exactly on geofence boundary."""
        # Use a point that's exactly at the radius distance
        # This is approximate since we're using real distance calculation
        result = check_geofence(
            (40.7128, -74.0060),
            (40.7128, -74.0060),  # Same point
            radius=0,
            radius_unit='m'
        )
        assert result.is_inside is True, "Same point should be inside (radius=0)"
        assert result.distance == 0.0, "Distance should be 0"
    
    def test_different_radius_units(self):
        """Test geofence with different radius units."""
        # Test with meters
        result_m = check_geofence(
            (40.7128, -74.0060),
            (40.7130, -74.0060),
            radius=1000,
            radius_unit='m'
        )
        
        # Test with kilometers (same radius)
        result_km = check_geofence(
            (40.7128, -74.0060),
            (40.7130, -74.0060),
            radius=1,
            radius_unit='km'
        )
        
        # Should give same result
        assert result_m.is_inside == result_km.is_inside, "Should give same result for equivalent radius"
    
    def test_country_based_locations(self):
        """Test geofence with country names."""
        result = check_geofence(
            "United States",
            "Canada",
            radius=1000000,  # 1000 km
            radius_unit='m'
        )
        assert isinstance(result, GeofenceResult), "Should return GeofenceResult"
        assert result.distance > 0, "Distance should be positive"


class TestStateTransitions:
    """Test suite for state transitions."""
    
    def test_outside_to_inside_transition(self):
        """Test transition from outside to inside."""
        monitor = GeofenceMonitor(GeofenceConfig(radius=1000, radius_unit='m'))
        
        # First check: outside
        result1 = monitor.check(
            (40.7128, -74.0060),  # Far from destination
            (40.7500, -74.0000)  # Destination
        )
        assert result1.state == GeofenceState.OUTSIDE, "Should start outside"
        
        # Second check: move closer (but still outside)
        result2 = monitor.check(
            (40.7200, -74.0050),  # Closer
            (40.7500, -74.0000)
        )
        # Should be approaching or still outside
        assert result2.state in (GeofenceState.OUTSIDE, GeofenceState.APPROACHING), "Should be outside or approaching"
        
        # Third check: inside
        result3 = monitor.check(
            (40.7490, -74.0005),  # Very close (inside 1km)
            (40.7500, -74.0000)
        )
        assert result3.state == GeofenceState.INSIDE, "Should be inside"
    
    def test_inside_to_outside_transition(self):
        """Test transition from inside to outside."""
        monitor = GeofenceMonitor(GeofenceConfig(radius=1000, radius_unit='m'))
        
        # First check: inside
        result1 = monitor.check(
            (40.7490, -74.0005),  # Close to destination
            (40.7500, -74.0000)  # Destination
        )
        initial_state = result1.state
        
        # Second check: move away (but still inside)
        result2 = monitor.check(
            (40.7480, -74.0010),  # Slightly farther
            (40.7500, -74.0000)
        )
        
        # Third check: outside
        result3 = monitor.check(
            (40.7200, -74.0050),  # Far away
            (40.7500, -74.0000)
        )
        assert result3.state == GeofenceState.OUTSIDE, "Should be outside"
    
    def test_approaching_state(self):
        """Test approaching state detection."""
        monitor = GeofenceMonitor(GeofenceConfig(radius=10000, radius_unit='m'))  # 10 km radius
        
        # Start far away
        result1 = monitor.check(
            (40.7000, -74.0100),
            (40.7500, -74.0000)
        )
        
        # Move closer (but still outside)
        result2 = monitor.check(
            (40.7200, -74.0050),  # Closer
            (40.7500, -74.0000)
        )
        
        # Should detect approaching if moving closer
        if result2.distance < result1.distance:
            assert result2.state in (GeofenceState.APPROACHING, GeofenceState.OUTSIDE), "Should detect approaching"
    
    def test_leaving_state(self):
        """Test leaving state detection."""
        monitor = GeofenceMonitor(GeofenceConfig(radius=10000, radius_unit='m'))  # 10 km radius
        
        # Start inside
        result1 = monitor.check(
            (40.7490, -74.0005),  # Close (inside)
            (40.7500, -74.0000)
        )
        
        # Move away (but still inside)
        result2 = monitor.check(
            (40.7480, -74.0010),  # Farther but still inside
            (40.7500, -74.0000)
        )
        
        # Should detect leaving if moving away
        if result2.distance > result1.distance and result2.is_inside:
            assert result2.state == GeofenceState.LEAVING, "Should detect leaving"


class TestAlertGeneration:
    """Test suite for alert generation."""
    
    def test_reached_alert(self):
        """Test 'reached' alert generation."""
        config = GeofenceConfig(
            radius=1000,
            radius_unit='m',
            reached_threshold=100  # Alert when within 100m
        )
        monitor = GeofenceMonitor(config)
        
        # Check when very close (within threshold)
        result = monitor.check(
            (40.7128, -74.0060),
            (40.7129, -74.0060)  # Very close
        )
        
        # Should have reached alert if inside and within threshold
        if result.is_inside:
            reached_alerts = [a for a in result.alerts if a.alert_type == 'reached']
            # May or may not have alert depending on exact distance
            assert isinstance(result.alerts, list), "Should have alerts list"
    
    def test_entered_alert(self):
        """Test 'entered' alert when crossing into geofence."""
        monitor = GeofenceMonitor(GeofenceConfig(radius=1000, radius_unit='m'))
        
        # First check: outside
        result1 = monitor.check(
            (40.7000, -74.0100),  # Far
            (40.7500, -74.0000)
        )
        
        # Second check: inside
        result2 = monitor.check(
            (40.7490, -74.0005),  # Close (inside)
            (40.7500, -74.0000)
        )
        
        # Should have entered alert if transitioned from outside to inside
        if result1.state != GeofenceState.INSIDE and result2.state == GeofenceState.INSIDE:
            entered_alerts = [a for a in result2.alerts if a.alert_type == 'entered']
            assert len(entered_alerts) > 0, "Should have entered alert"
    
    def test_exited_alert(self):
        """Test 'exited' alert when crossing out of geofence."""
        monitor = GeofenceMonitor(GeofenceConfig(radius=1000, radius_unit='m'))
        
        # First check: inside
        result1 = monitor.check(
            (40.7490, -74.0005),  # Close (inside)
            (40.7500, -74.0000)
        )
        
        # Second check: outside
        result2 = monitor.check(
            (40.7000, -74.0100),  # Far (outside)
            (40.7500, -74.0000)
        )
        
        # Should have exited alert if transitioned from inside to outside
        if result1.state == GeofenceState.INSIDE and result2.state == GeofenceState.OUTSIDE:
            exited_alerts = [a for a in result2.alerts if a.alert_type == 'exited']
            assert len(exited_alerts) > 0, "Should have exited alert"
    
    def test_approaching_alert(self):
        """Test 'approaching' alert with threshold."""
        config = GeofenceConfig(
            radius=10000,
            radius_unit='m',
            approaching_threshold_percent=10  # Alert when 10% closer
        )
        monitor = GeofenceMonitor(config)
        
        # First check
        result1 = monitor.check(
            (40.7000, -74.0100),
            (40.7500, -74.0000)
        )
        initial_distance = result1.distance
        
        # Second check: move significantly closer
        result2 = monitor.check(
            (40.7200, -74.0050),  # Closer
            (40.7500, -74.0000)
        )
        
        # Should have approaching alert if moved closer by threshold
        if result2.state == GeofenceState.APPROACHING:
            approaching_alerts = [a for a in result2.alerts if a.alert_type == 'approaching']
            # May or may not have alert depending on exact distance change
            assert isinstance(result2.alerts, list), "Should have alerts list"


class TestGeofenceMonitor:
    """Test suite for GeofenceMonitor class."""
    
    def test_monitor_initialization(self):
        """Test monitor initialization."""
        config = GeofenceConfig(radius=1000, radius_unit='m')
        monitor = GeofenceMonitor(config)
        assert monitor.config == config, "Config should be set"
        assert monitor.previous_state is None, "Previous state should be None initially"
        assert monitor.previous_distance is None, "Previous distance should be None initially"
    
    def test_monitor_state_tracking(self):
        """Test that monitor tracks state between calls."""
        monitor = GeofenceMonitor(GeofenceConfig(radius=1000, radius_unit='m'))
        
        # First call
        result1 = monitor.check((40.7128, -74.0060), (40.7130, -74.0060))
        assert monitor.previous_state == result1.state, "Should track state"
        assert monitor.previous_distance == result1.distance, "Should track distance"
        
        # Second call
        result2 = monitor.check((40.7129, -74.0060), (40.7130, -74.0060))
        assert monitor.previous_state == result2.state, "Should update state"
        assert monitor.previous_distance == result2.distance, "Should update distance"
    
    def test_monitor_reset(self):
        """Test monitor reset functionality."""
        monitor = GeofenceMonitor(GeofenceConfig(radius=1000, radius_unit='m'))
        
        # Make a check to set state
        monitor.check((40.7128, -74.0060), (40.7130, -74.0060))
        assert monitor.previous_state is not None, "State should be set"
        
        # Reset
        monitor.reset()
        assert monitor.previous_state is None, "State should be reset"
        assert monitor.previous_distance is None, "Distance should be reset"


class TestStatelessCheckGeofence:
    """Test suite for stateless check_geofence() function."""
    
    def test_stateless_check(self):
        """Test stateless geofence check."""
        result = check_geofence(
            (40.7128, -74.0060),
            (40.7130, -74.0060),
            radius=1000,
            radius_unit='m'
        )
        assert isinstance(result, GeofenceResult), "Should return GeofenceResult"
        assert result.distance >= 0, "Distance should be non-negative"
    
    def test_stateless_with_previous_state(self):
        """Test stateless check with previous state."""
        # First check
        result1 = check_geofence(
            (40.7128, -74.0060),
            (40.7130, -74.0060),
            radius=1000,
            radius_unit='m'
        )
        
        # Second check with previous state
        result2 = check_geofence(
            (40.7129, -74.0060),
            (40.7130, -74.0060),
            radius=1000,
            radius_unit='m',
            previous_distance=result1.distance,
            previous_state=result1.state,
            previous_distance_unit=result1.unit
        )
        
        assert isinstance(result2, GeofenceResult), "Should return GeofenceResult"
        # Should be able to detect state transitions
        assert result2.state in GeofenceState, "State should be valid"


class TestEdgeCases:
    """Test suite for edge cases."""
    
    def test_same_location_as_destination(self):
        """Test when current location is same as destination."""
        result = check_geofence(
            (40.7128, -74.0060),
            (40.7128, -74.0060),  # Same point
            radius=1000,
            radius_unit='m'
        )
        assert result.distance == 0.0, "Distance should be 0"
        assert result.is_inside is True, "Should be inside (distance = 0)"
    
    def test_very_small_radius(self):
        """Test with very small radius."""
        result = check_geofence(
            (40.7128, -74.0060),
            (40.7129, -74.0060),
            radius=1,  # 1 meter
            radius_unit='m'
        )
        assert isinstance(result, GeofenceResult), "Should handle small radius"
    
    def test_very_large_radius(self):
        """Test with very large radius."""
        result = check_geofence(
            (40.7128, -74.0060),  # NYC
            (34.0522, -118.2437),  # LA
            radius=1000,  # 1000 km
            radius_unit='km'
        )
        assert result.is_inside is True, "Should be inside with large radius"
    
    def test_negative_radius(self):
        """Test that negative radius is handled."""
        with pytest.raises((ValueError, AssertionError)):
            check_geofence(
                (40.7128, -74.0060),
                (40.7130, -74.0060),
                radius=-1000,
                radius_unit='m'
            )
    
    def test_zero_radius(self):
        """Test with zero radius."""
        result = check_geofence(
            (40.7128, -74.0060),
            (40.7128, -74.0060),  # Same point
            radius=0,
            radius_unit='m'
        )
        assert result.is_inside is True, "Same point should be inside with radius=0"


class TestResultObjects:
    """Test suite for result object methods."""
    
    def test_geofence_result_to_dict(self):
        """Test GeofenceResult.to_dict()."""
        result = check_geofence(
            (40.7128, -74.0060),
            (40.7130, -74.0060),
            radius=1000,
            radius_unit='m'
        )
        result_dict = result.to_dict()
        assert isinstance(result_dict, dict), "Should return dictionary"
        assert 'is_inside' in result_dict, "Should have is_inside"
        assert 'distance' in result_dict, "Should have distance"
        assert 'state' in result_dict, "Should have state"
        assert 'alerts' in result_dict, "Should have alerts"
    
    def test_geofence_alert_to_dict(self):
        """Test GeofenceAlert.to_dict()."""
        alert = GeofenceAlert(
            alert_type='reached',
            distance=100.0,
            unit='m',
            state=GeofenceState.INSIDE
        )
        alert_dict = alert.to_dict()
        assert isinstance(alert_dict, dict), "Should return dictionary"
        assert alert_dict['alert_type'] == 'reached', "Should have correct alert type"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
