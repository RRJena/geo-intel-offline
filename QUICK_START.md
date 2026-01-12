# Quick Start Guide

A 5-minute guide to get started with `geo-intel-offline`.

## Installation

```bash
pip install geo-intel-offline
```

## Basic Usage

```python
from geo_intel_offline import resolve

# Resolve coordinates
result = resolve(40.7128, -74.0060)  # New York

# Access results
print(result.country)      # "United States of America"
print(result.iso2)         # "US"
print(result.iso3)         # "USA"
print(result.continent)    # "North America"
print(result.timezone)     # "America/New_York"
print(result.confidence)   # 0.98
```

## Common Use Cases

### 1. Single Location

```python
from geo_intel_offline import resolve

result = resolve(51.5074, -0.1278)  # London
print(f"{result.country} ({result.iso2})")
```

### 2. Multiple Locations

```python
from geo_intel_offline import resolve

locations = [
    (40.7128, -74.0060),  # NYC
    (35.6762, 139.6503),  # Tokyo
    (-33.8688, 151.2093), # Sydney
]

for lat, lon in locations:
    result = resolve(lat, lon)
    print(f"{result.country} ({result.iso2})")
```

### 3. With Error Handling

```python
from geo_intel_offline import resolve

def safe_resolve(lat, lon):
    result = resolve(lat, lon)
    if result.country is None:
        return "No country found (ocean or invalid)"
    return f"{result.country} ({result.iso2})"

print(safe_resolve(40.7128, -74.0060))
```

## Next Steps

- See [README.md](README.md) for full documentation
- Check [ARCHITECTURE.md](ARCHITECTURE.md) for technical details
- View [TEST_RESULTS.md](TEST_RESULTS.md) for accuracy reports
