# Release Notes - geo-intel-offline v1.5.0 (Python)

## 🎉 Major New Features

This release introduces **four powerful new features** that extend the library's capabilities beyond geocoding:

### 1. 📏 Distance Calculation
Calculate distances between any two locations with automatic unit detection and multiple algorithms.

**Features:**
- **Multiple Algorithms**: Haversine (fast), Vincenty (most accurate), Spherical Law of Cosines
- **Smart Unit Detection**: Automatically detects km/miles based on country preferences (US, GB, LR, MM use miles)
- **Flexible Inputs**: Accepts coordinates, country names, ISO codes, or continent names
- **Automatic Method Selection**: Chooses optimal algorithm based on distance

**Example:**
```python
from geo_intel_offline import calculate_distance

# Distance between coordinates (auto-detects unit)
result = calculate_distance([40.7128, -74.0060], [34.0522, -118.2437])
print(f"{result.distance:.2f} {result.unit}")  # "2448.50 mile"

# Distance between countries
result = calculate_distance("United States", "Canada")

# Force unit or method
result = calculate_distance("US", "CA", unit='km', method='vincenty')
```

### 2. 🎯 Geo-fencing
Monitor location proximity with state tracking and configurable alerts.

**Features:**
- **State Tracking**: OUTSIDE, APPROACHING, INSIDE, LEAVING
- **Configurable Alerts**: Reached, Entered, Exited, Approaching, Leaving
- **Stateless & Stateful APIs**: `check_geofence()` for one-off checks, `GeofenceMonitor` for tracking
- **Multiple Units**: Supports meters, kilometers, and miles

**Example:**
```python
from geo_intel_offline import check_geofence, GeofenceMonitor, GeofenceConfig

# Stateless check
result = check_geofence(
    current_location=(40.7128, -74.0060),
    destination=(40.7130, -74.0060),
    radius=1000,
    radius_unit='m'
)
print(f"Inside: {result.is_inside}, State: {result.state}")

# Stateful monitoring with alerts
config = GeofenceConfig(
    radius=1000,
    radius_unit='m',
    approaching_threshold_percent=10.0
)
monitor = GeofenceMonitor(config)
result = monitor.check((40.7128, -74.0060), (40.7130, -74.0060))
```

### 3. 🎲 Random Coordinates by Region
Generate random coordinates within countries or continents with point-in-polygon validation.

**Features:**
- **Region Support**: Countries and continents
- **Point-in-Polygon Validation**: Ensures all generated coordinates are actually within the region
- **Reproducible**: Seed support for deterministic generation
- **Efficient**: Rejection sampling with bounding box optimization

**Example:**
```python
from geo_intel_offline import generate_random_coordinates_by_region

# Generate random coordinates in a country
result = generate_random_coordinates_by_region("United States", count=10, seed=42)
for lat, lon in result.coordinates:
    print(f"({lat:.4f}, {lon:.4f})")

# Generate in a continent
result = generate_random_coordinates_by_region("Europe", count=5, seed=42)
```

### 4. 🎲 Random Coordinates by Area
Generate random coordinates within a circular area with uniform distribution.

**Features:**
- **Circular Areas**: Define center and radius
- **Uniform Distribution**: Properly distributed points within the circle
- **Multiple Units**: Meters, kilometers, miles, or degrees
- **Reproducible**: Seed support

**Example:**
```python
from geo_intel_offline import generate_random_coordinates_by_area

result = generate_random_coordinates_by_area(
    center=(40.7128, -74.0060),  # NYC
    radius=10,                    # 10 km
    count=5,
    radius_unit='km',
    seed=42
)
```

## 📊 Test Results

### Comprehensive Testing
- ✅ **95/95 new feature tests passing** (100% pass rate)
- ✅ **All backward compatibility tests passing** (no breaking changes)
- ✅ **100% accuracy** maintained for all 258 countries
- ✅ **Integration tests** verify all features work together seamlessly

### Test Coverage
- **Distance Calculation**: 36 tests (positive, negative, edge cases)
- **Geo-fencing**: 16 tests (state transitions, alerts, various units)
- **Random Coordinates**: 23 tests (region and area generation, reproducibility)
- **Backward Compatibility**: 20 tests (all original features verified)

## 🔄 Backward Compatibility

✅ **100% backward compatible** - All existing code continues to work without changes.

The new features are additive and do not modify any existing APIs or behavior.

## 📚 Documentation

- ✅ Comprehensive README updates with examples for all new features
- ✅ API reference documentation for all new functions and classes
- ✅ Comparison table with other geo libraries
- ✅ Use cases and limitations documented
- ✅ Integration examples showing all features working together

## 🚀 Performance

- **Distance Calculation**: < 0.1ms per calculation
- **Geo-fencing Check**: < 0.5ms per check
- **Random Coordinate Generation**: ~1-5ms per coordinate (depends on region complexity)
- **Memory Footprint**: No significant increase (~15MB total)

## 🔧 Technical Details

### New Modules
- `geo_intel_offline.distance`: Distance calculation algorithms and utilities
- `geo_intel_offline.geofence`: Geo-fencing with state tracking
- `geo_intel_offline.random_coords`: Random coordinate generation

### New Classes
- `DistanceResult`: Distance calculation results
- `GeofenceState`: Enum for geofence states
- `GeofenceConfig`: Configuration for geo-fencing
- `GeofenceMonitor`: Stateful geo-fencing monitor
- `GeofenceAlert`: Alert information
- `GeofenceResult`: Geo-fencing check results
- `RandomCoordinateResult`: Random coordinate generation results

### New Functions
- `calculate_distance()`: Main distance calculation function
- `haversine_distance()`: Haversine algorithm
- `vincenty_distance()`: Vincenty algorithm
- `spherical_law_of_cosines()`: Spherical Law of Cosines
- `check_geofence()`: Stateless geo-fencing check
- `generate_random_coordinates_by_region()`: Generate coordinates in regions
- `generate_random_coordinates_by_area()`: Generate coordinates in circular areas

## 📦 Installation

```bash
pip install geo-intel-offline==1.5.0
```

## 🔗 Links

- **PyPI**: https://pypi.org/project/geo-intel-offline/
- **GitHub**: https://github.com/RRJena/geo-intel-offline
- **Documentation**: See README.md for comprehensive examples

## 🙏 Acknowledgments

- Distance algorithms: Haversine, Vincenty, Spherical Law of Cosines
- Point-in-Polygon: Ray casting algorithm
- Data source: Natural Earth

---

**Made with ❤️ by Rakesh Ranjan Jena**
