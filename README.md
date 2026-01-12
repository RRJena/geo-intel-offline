# geo-intel-offline

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Development Status](https://img.shields.io/badge/status-production--ready-brightgreen.svg)](https://pypi.org/project/geo-intel-offline/)

**Production-ready, offline geo-intelligence library** for resolving latitude/longitude coordinates to country, ISO codes, continent, timezone, and confidence scores. No API keys, no network requests, 100% deterministic.

## 🌟 Why This Library Exists

Every developer working with geolocation has faced the same frustration: you need to know what country a set of coordinates belongs to, but all the solutions either cost money, require API keys, need constant internet connectivity, or have restrictive rate limits. What if you're building an offline application? What if you're processing millions of records and API costs become prohibitive? What if you need deterministic results without external dependencies?

**We built `geo-intel-offline` to solve these real-world problems.**

This library was born from the need for a **reliable, fast, and completely free** solution that works everywhere—from edge devices in remote locations to high-throughput data processing pipelines. No subscriptions, no rate limits, no vendor lock-in. Just pure Python that does one thing exceptionally well: **tell you where in the world a coordinate belongs.**

Whether you're building a mobile app that works offline, processing billions of GPS logs, enriching datasets without external APIs, or creating applications for regions with unreliable internet—this library empowers you to add geo-intelligence to your projects without compromise.

## ✨ Features

- 🚀 **Fast**: < 1ms per lookup, < 15MB memory footprint
- 📦 **Offline**: Zero network dependencies, works completely offline
- 🎯 **Accurate**: 99.92% accuracy across 258 countries
- 🔒 **Deterministic**: Same input always produces same output
- 🗜️ **Optimized**: 66% size reduction with automatic compression
- 🌍 **Comprehensive**: Supports all countries, continents, and territories
- 🎨 **Clean API**: Simple, intuitive interface
- 🔧 **No Dependencies**: Pure Python, no native extensions
- 💰 **Free Forever**: No API costs, no rate limits, no hidden fees

## 🎯 Where Can You Use This Library?

### Mobile Applications
**Offline-first apps** that need to identify user location even without internet connectivity. Perfect for travel apps, fitness trackers, or field data collection tools that work in remote areas.

```python
# Works offline - no internet needed!
from geo_intel_offline import resolve

def identify_user_country(lat, lon):
    result = resolve(lat, lon)
    return result.country  # Works even in airplane mode
```

### Data Processing & Analytics
**Batch processing** of GPS logs, location data, or transaction records. Process millions of coordinates without API rate limits or costs.

```python
# Process millions of records - no rate limits!
import pandas as pd
from geo_intel_offline import resolve

df = pd.read_csv('location_data.csv')
df['country'] = df.apply(
    lambda row: resolve(row['lat'], row['lon']).country,
    axis=1
)
```

### IoT & Edge Devices
**Edge computing** applications where devices need geo-intelligence without cloud connectivity. Perfect for sensors, trackers, or embedded systems.

```python
# Runs on Raspberry Pi, microcontrollers, edge devices
# No cloud dependency, minimal resources
result = resolve(sensor_lat, sensor_lon)
if result.country != 'US':
    trigger_alert()
```

### API Alternatives & Rate Limit Avoidance
**Replace expensive APIs** or bypass rate limits. Perfect for applications that need high throughput or want to reduce infrastructure costs. See the [Use Cases](#-use-cases) section below for detailed implementation examples.

```python
# Instead of: external_api.geocode(lat, lon)  # $0.005 per request
# Use: resolve(lat, lon)  # FREE, unlimited, instant
```

### Geographic Data Enrichment
**Enrich datasets** with country information for analysis, visualization, or machine learning. No need to maintain external API connections or handle failures. See the [Use Cases](#-use-cases) section below for pandas DataFrame examples.

```python
# Enrich logs, events, transactions with country data
events = load_events_from_database()
for event in events:
    event['country'] = resolve(event['lat'], event['lon']).iso2
    save_event(event)
```

### Location-Based Features
**Add geo-context** to your applications: content localization, compliance checks, regional restrictions, or timezone-aware scheduling.

```python
# Content localization based on location
result = resolve(user_lat, user_lon)
if result.continent == 'Europe':
    show_gdpr_banner()
elif result.country == 'US':
    show_us_specific_content()
```

### Development & Testing
**Local development** and testing without needing API keys or internet connectivity. Great for CI/CD pipelines and automated testing.

```python
# Test with real data - no mocks needed
def test_geocoding():
    result = resolve(40.7128, -74.0060)
    assert result.country == 'United States of America'
    assert result.iso2 == 'US'
```

### Research & Academic Projects
**Academic research** that requires reproducible results without external API dependencies or costs that might limit research scope.

```python
# Reproducible research - same results every time
# No API costs to worry about in grant proposals
results = [resolve(lat, lon) for lat, lon in research_coordinates]
```

## 💡 Benefits

### For Developers

#### **Simplicity & Speed**
- **One-line integration**: `from geo_intel_offline import resolve`
- **No configuration**: Works out of the box with pre-built data
- **Lightning fast**: < 1ms per lookup means no performance bottlenecks
- **Predictable**: Same coordinates always return same results

#### **Development Experience**
- **No API keys needed**: Start coding immediately
- **Works offline**: Develop and test without internet
- **No rate limits**: Test with unlimited requests
- **Pure Python**: Easy to debug, inspect, and modify
- **Well documented**: Comprehensive examples and API reference

#### **Flexibility & Control**
- **Modular loading**: Load only countries you need (reduce memory)
- **Custom data**: Build datasets from your own GeoJSON sources
- **No vendor lock-in**: Your code, your data, your control
- **Deterministic**: Perfect for testing and reproducible builds

### For Businesses & Organizations

#### **Cost Savings**
- **Zero API costs**: Save thousands on external geocoding services
- **No infrastructure**: Runs locally, no cloud services needed
- **No scaling costs**: Handle millions of requests without per-request fees
- **Predictable expenses**: One-time setup, no ongoing subscription

**Example Cost Comparison:**
- External API: $0.005 per request × 1M requests = **$5,000/month**
- This library: **$0/month** (one-time setup time)

#### **Reliability & Performance**
- **100% uptime**: No external service dependencies to fail
- **Consistent latency**: < 1ms every time (no network delays)
- **No rate limits**: Process data at your own pace
- **Data privacy**: Location data never leaves your infrastructure

#### **Scalability**
- **Handle any volume**: Process billions of coordinates
- **Edge deployment**: Deploy to edge devices and IoT
- **Batch processing**: Process large datasets efficiently
- **Memory efficient**: < 15MB footprint even with all countries

#### **Compliance & Security**
- **GDPR friendly**: No data sent to external services
- **Offline capable**: Meets requirements for air-gapped systems
- **Auditable**: You can inspect the exact logic and data
- **No data sharing**: Complete data sovereignty

### For End Users

#### **Privacy**
- **Data stays local**: Coordinates never sent to external servers
- **No tracking**: No analytics, no usage monitoring
- **Transparent**: Open source, you can verify everything

#### **Performance**
- **Instant results**: No network latency
- **Works offline**: No internet required
- **Low resource usage**: Runs on modest hardware

## 📦 Installation

### From PyPI (Recommended)

```bash
pip install geo-intel-offline
```

### From uv

```bash
uv pip install geo-intel-offline
```

### From Source

```bash
git clone https://github.com/yourusername/geo-intel-offline.git
cd geo-intel-offline
pip install .
```

## 🚀 Quick Start

### Basic Usage

```python
from geo_intel_offline import resolve

# Resolve coordinates to country information
result = resolve(40.7128, -74.0060)  # New York City

print(result.country)      # "United States of America"
print(result.iso2)         # "US"
print(result.iso3)         # "USA"
print(result.continent)    # "North America"
print(result.timezone)     # "America/New_York"
print(result.confidence)   # 0.98
```

### Step-by-Step Guide

#### Step 1: Install the Package

```bash
pip install geo-intel-offline
```

#### Step 2: Import and Use

```python
from geo_intel_offline import resolve

# Resolve a coordinate
result = resolve(51.5074, -0.1278)  # London, UK

# Access results as attributes
print(f"Country: {result.country}")
print(f"ISO2 Code: {result.iso2}")
print(f"ISO3 Code: {result.iso3}")
print(f"Continent: {result.continent}")
print(f"Timezone: {result.timezone}")
print(f"Confidence: {result.confidence:.2f}")
```

#### Step 3: Handle Edge Cases

```python
from geo_intel_offline import resolve

# Ocean locations (no country)
result = resolve(0.0, 0.0)  # Gulf of Guinea (ocean)
if result.country is None:
    print("No country found (likely ocean)")
    print(f"Confidence: {result.confidence}")  # Will be 0.0

# Border regions (may have lower confidence)
result = resolve(49.0, 8.2)  # Near France-Germany border
if result.confidence < 0.7:
    print(f"Low confidence: {result.confidence:.2f} (near border)")
```

## 📖 Detailed Examples

### Example 1: Resolve Multiple Locations

```python
from geo_intel_offline import resolve

locations = [
    (40.7128, -74.0060, "New York"),
    (51.5074, -0.1278, "London"),
    (35.6762, 139.6503, "Tokyo"),
    (-33.8688, 151.2093, "Sydney"),
    (55.7558, 37.6173, "Moscow"),
]

for lat, lon, name in locations:
    result = resolve(lat, lon)
    print(f"{name}: {result.country} ({result.iso2}) - Confidence: {result.confidence:.2f}")
```

**Output:**
```
New York: United States of America (US) - Confidence: 0.98
London: United Kingdom (GB) - Confidence: 0.93
Tokyo: Japan (JP) - Confidence: 0.93
Sydney: Australia (AU) - Confidence: 0.80
Moscow: Russia (RU) - Confidence: 0.93
```

### Example 2: Batch Processing

```python
from geo_intel_offline import resolve
import time

coordinates = [
    (40.7128, -74.0060),
    (51.5074, -0.1278),
    (35.6762, 139.6503),
    # ... more coordinates
]

start = time.perf_counter()
results = [resolve(lat, lon) for lat, lon in coordinates]
end = time.perf_counter()

print(f"Processed {len(coordinates)} coordinates in {(end - start)*1000:.2f}ms")
print(f"Average: {(end - start)*1000/len(coordinates):.3f}ms per lookup")
```

### Example 3: Dictionary Access

```python
from geo_intel_offline import resolve

result = resolve(37.7749, -122.4194)  # San Francisco

# Access as dictionary
result_dict = result.to_dict()
print(result_dict)
# {
#     'country': 'United States of America',
#     'iso2': 'US',
#     'iso3': 'USA',
#     'continent': 'North America',
#     'timezone': 'America/Los_Angeles',
#     'confidence': 0.95
# }

# Or access as attributes
print(result.country)  # "United States of America"
print(result.iso2)     # "US"
```

### Example 4: Filter by Confidence

```python
from geo_intel_offline import resolve

def resolve_with_threshold(lat, lon, min_confidence=0.7):
    """Resolve coordinates with confidence threshold."""
    result = resolve(lat, lon)
    if result.confidence < min_confidence:
        return None, f"Low confidence: {result.confidence:.2f}"
    return result, None

result, error = resolve_with_threshold(40.7128, -74.0060, min_confidence=0.9)
if result:
    print(f"High confidence result: {result.country}")
else:
    print(f"Rejected: {error}")
```

### Example 5: Error Handling

```python
from geo_intel_offline import resolve

def safe_resolve(lat, lon):
    """Safely resolve coordinates with error handling."""
    try:
        result = resolve(lat, lon)
        if result.country is None:
            return {"error": "No country found", "confidence": result.confidence}
        return {
            "country": result.country,
            "iso2": result.iso2,
            "iso3": result.iso3,
            "continent": result.continent,
            "timezone": result.timezone,
            "confidence": result.confidence,
        }
    except ValueError as e:
        return {"error": f"Invalid coordinates: {e}"}
    except FileNotFoundError as e:
        return {"error": f"Data files not found: {e}"}

# Usage
result = safe_resolve(40.7128, -74.0060)
print(result)
```

## 📚 API Reference

### `resolve(lat, lon, data_dir=None, countries=None, continents=None, exclude_countries=None)`

Main function to resolve coordinates to geo-intelligence.

**Parameters:**

- `lat` (float): Latitude (-90.0 to 90.0)
- `lon` (float): Longitude (-180.0 to 180.0)
- `data_dir` (str, optional): Custom data directory path
- `countries` (list[str], optional): List of ISO2 codes to load (modular format only)
- `continents` (list[str], optional): List of continent names to load (modular format only)
- `exclude_countries` (list[str], optional): List of ISO2 codes to exclude (modular format only)

**Returns:**

`GeoIntelResult` object with the following properties:

- `country` (str | None): Country name
- `iso2` (str | None): ISO 3166-1 alpha-2 code
- `iso3` (str | None): ISO 3166-1 alpha-3 code
- `continent` (str | None): Continent name
- `timezone` (str | None): IANA timezone identifier
- `confidence` (float): Confidence score (0.0 to 1.0)

**Methods:**

- `to_dict()`: Convert result to dictionary

**Raises:**

- `ValueError`: If lat/lon are out of valid range
- `FileNotFoundError`: If data files are missing

### `GeoIntelResult`

Result object returned by `resolve()`.

**Properties:**

```python
result.country      # Country name (str | None)
result.iso2         # ISO2 code (str | None)
result.iso3         # ISO3 code (str | None)
result.continent    # Continent name (str | None)
result.timezone     # Timezone (str | None)
result.confidence   # Confidence score (float, 0.0-1.0)
```

**Methods:**

```python
result.to_dict()    # Convert to dictionary
```

## 🎯 Use Cases

### 1. Geocoding Service

```python
from geo_intel_offline import resolve

def geocode_location(lat, lon):
    """Geocode a location without external API."""
    result = resolve(lat, lon)
    return {
        "country": result.country,
        "country_code": result.iso2,
        "continent": result.continent,
        "timezone": result.timezone,
    }

# Use in your application
location_info = geocode_location(40.7128, -74.0060)
```

### 2. User Location Analysis

```python
from geo_intel_offline import resolve

def analyze_user_locations(locations):
    """Analyze user locations for geographic distribution."""
    countries = {}
    for lat, lon in locations:
        result = resolve(lat, lon)
        if result.country:
            countries[result.country] = countries.get(result.country, 0) + 1
    return countries
```

### 3. Data Enrichment

```python
from geo_intel_offline import resolve
import pandas as pd

# Enrich DataFrame with country information
df = pd.DataFrame({
    'lat': [40.7128, 51.5074, 35.6762],
    'lon': [-74.0060, -0.1278, 139.6503],
})

df['country'] = df.apply(
    lambda row: resolve(row['lat'], row['lon']).country,
    axis=1
)
df['iso2'] = df.apply(
    lambda row: resolve(row['lat'], row['lon']).iso2,
    axis=1
)

print(df)
```

### 4. API Rate Limiting Alternative

```python
from geo_intel_offline import resolve

# Instead of calling external API
# result = external_api.geocode(lat, lon)  # Rate limited!

# Use offline resolution
result = resolve(lat, lon)  # No rate limits, always available
```

## 🔧 Advanced Usage

### Modular Data Loading

For applications that only need specific regions, you can use modular data loading to reduce memory footprint:

```python
from geo_intel_offline import resolve

# Load only specific countries (requires modular data format)
result = resolve(40.7128, -74.0060, countries=["US", "CA", "MX"])

# Load by continent
result = resolve(51.5074, -0.1278, continents=["Europe"])

# Exclude specific countries
result = resolve(35.6762, 139.6503, exclude_countries=["RU", "CN"])
```

**Note:** Modular data loading requires building data in modular format. See [Building Custom Data](#building-custom-data) below.

## 🏗️ Building Custom Data (Advanced)

### Prerequisites

1. Download Natural Earth Admin 0 Countries GeoJSON:
   ```bash
   wget https://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-admin-0-countries/
   # Or use the provided script:
   bash scripts/download_natural_earth.sh
   ```

### Build Full Dataset

```bash
# Build complete dataset with compression
python3 -m geo_intel_offline.data_builder \
    data_sources/ne_10m_admin_0_countries.geojson \
    geo_intel_offline/data

# Or use automated script
python3 scripts/prepare_full_data.py
```

**Note:** The build process automatically compresses data files, reducing size by ~66%.

### Build Modular Dataset

```bash
# Build modular format (country-wise files)
python3 -m geo_intel_offline.data_builder_modular \
    data_sources/ne_10m_admin_0_countries.geojson \
    output_directory

# Build specific countries only
python3 -m geo_intel_offline.data_builder_modular \
    --countries US,CA,MX \
    data_sources/ne_10m_admin_0_countries.geojson \
    output_directory

# Build by continent
python3 -m geo_intel_offline.data_builder_modular \
    --continents "North America,Europe" \
    data_sources/ne_10m_admin_0_countries.geojson \
    output_directory
```

## ⚡ Performance

### Benchmarks

- **Lookup Speed**: < 1ms per resolution
- **Memory Footprint**: < 15 MB (all data in memory)
- **Cold Start**: ~100ms (initial data load)
- **Accuracy**: 99.92% across 258 countries
- **Data Size**: ~4 MB compressed (66% reduction)

### Performance Test

```python
from geo_intel_offline import resolve
import time

test_points = [
    (40.7128, -74.0060),   # NYC
    (51.5074, -0.1278),    # London
    (35.6762, 139.6503),   # Tokyo
    # ... more points
]

start = time.perf_counter()
for _ in range(100):
    for lat, lon in test_points:
        resolve(lat, lon)
end = time.perf_counter()

avg_time = ((end - start) / (100 * len(test_points))) * 1000
print(f"Average lookup time: {avg_time:.3f}ms")
```

## 🔍 Understanding Confidence Scores

Confidence scores range from 0.0 to 1.0:

- **0.9 - 1.0**: High confidence (well within country boundaries)
- **0.7 - 0.9**: Good confidence (inside country, may be near border)
- **0.5 - 0.7**: Moderate confidence (near border or ambiguous region)
- **0.0 - 0.5**: Low confidence (likely ocean or disputed territory)

```python
from geo_intel_offline import resolve

result = resolve(40.7128, -74.0060)  # NYC (center of country)
print(f"Confidence: {result.confidence:.2f}")  # ~0.98

result = resolve(49.0, 8.2)  # Near France-Germany border
print(f"Confidence: {result.confidence:.2f}")  # ~0.65-0.75

result = resolve(0.0, 0.0)  # Ocean
print(f"Confidence: {result.confidence:.2f}")  # 0.0
```

## ❓ Troubleshooting

### Issue: "Data file not found"

**Solution:** Ensure data files are present in the package installation directory, or build custom data:

```bash
# Check if data files exist
ls geo_intel_offline/data/*.json.gz

# If missing, rebuild data
python3 -m geo_intel_offline.data_builder \
    path/to/geojson \
    geo_intel_offline/data
```

### Issue: Low accuracy for specific locations

**Possible causes:**
- Location is in ocean (no country)
- Location is on border (ambiguous)
- Location is in disputed territory

**Solution:** Check confidence score and handle edge cases:

```python
result = resolve(lat, lon)
if result.confidence < 0.5:
    print("Low confidence - may be ocean or border region")
```

### Issue: Memory usage higher than expected

**Solution:** Use modular data loading to load only needed countries:

```python
# Instead of loading all countries
result = resolve(lat, lon)

# Load only needed countries
result = resolve(lat, lon, countries=["US", "CA"])
```

## 📊 Test Results

Comprehensive testing across 258 countries:

- **Overall Accuracy**: 99.92%
- **Countries Tested**: 258
- **Total Test Points**: 2,513
- **Countries with 100% Accuracy**: 256 (99.2%)
- **Countries with 90%+ Accuracy**: 257 (99.6%)

See [TEST_RESULTS.md](TEST_RESULTS.md) for detailed country-wise results.

## 🏗️ Architecture

The library uses a hybrid three-stage resolution pipeline:

1. **Geohash Indexing**: Fast spatial filtering to candidate countries
2. **Point-in-Polygon**: Accurate geometric verification using ray casting
3. **Confidence Scoring**: Distance-to-border calculation for certainty assessment

For detailed architecture documentation, see [ARCHITECTURE.md](ARCHITECTURE.md).

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## 📚 Additional Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Internal design and architecture details
- **[TEST_RESULTS.md](TEST_RESULTS.md)** - Comprehensive test results and benchmarks
- **[QUICK_START.md](QUICK_START.md)** - Quick start guide for new users

## 🔗 Links

- **PyPI**: https://pypi.org/project/geo-intel-offline/
- **GitHub**: https://github.com/yourusername/geo-intel-offline
- **Issues**: https://github.com/yourusername/geo-intel-offline/issues

## 🙏 Acknowledgments

- Data source: [Natural Earth](https://www.naturalearthdata.com/)
- Geohash implementation: Based on standard geohash algorithm
- Point-in-Polygon: Ray casting algorithm

---

## 👨‍💻 Author

**Rakesh Ranjan Jena**

- 🌐 **Blog**: [https://www.rrjprince.com/](https://www.rrjprince.com/)
- 💼 **LinkedIn**: [https://www.linkedin.com/in/rrjprince/](https://www.linkedin.com/in/rrjprince/)

---

**Made with ❤️ for the Python community**
