# Architecture Documentation

## Internal Architecture

### Overview

`geo_intel_offline` uses a **hybrid three-stage resolution pipeline** optimized for speed, accuracy, and memory efficiency.

```
Input: (lat, lon)
    ↓
[1] Geohash Encoding
    ↓
[2] Geohash Index Lookup → Candidate Countries
    ↓
[3] Point-in-Polygon Verification
    ↓
[4] Confidence Scoring
    ↓
Output: Country + Metadata + Confidence
```

### Stage 1: Geohash Encoding

**Purpose**: Fast spatial indexing to reduce candidate set from ~200 countries to 1-3 candidates.

**Implementation**: `geohash.py`
- Encodes lat/lon to base32 string (precision level 6 = ~1.2km)
- Deterministic encoding (same input → same output)
- O(1) lookup complexity

**Design Decisions**:
- **Precision 6**: Balance between index size and spatial resolution
  - Too low (4): Too many false positives → more PIP tests
  - Too high (8): Index too large → memory bloat
  - 6 is optimal: ~1.2km precision, manageable index size

### Stage 2: Geohash Index Lookup

**Purpose**: Map geohash → candidate country IDs.

**Data Structure**: `geohash_index.json`
- Key: geohash string (6 chars)
- Value: list of country IDs

**Construction**:
- For each country polygon, sample points and validate with point-in-polygon
- Only index geohashes where country actually exists (eliminates false positives)
- Encode validated sample point → geohash
- Build reverse index: geohash → country IDs

**Edge Cases**:
- Geohash on border: Multiple countries in list (handled in Stage 3)
- No match: Try neighbor geohashes (geohash boundary cases)

### Stage 3: Point-in-Polygon (PIP)

**Purpose**: Accurate geometric verification.

**Algorithm**: Ray Casting
- Cast horizontal ray East from point
- Count intersections with polygon edges
- Odd count = inside, even = outside

**Why Ray Casting?**
- More accurate than bounding boxes
- Handles complex polygons (holes, multiple rings)
- Deterministic results
- Fast enough for production (< 0.5ms typical)

**Implementation**: `pip.py`
- `point_in_polygon()`: Basic PIP for single ring
- `point_in_polygon_with_holes()`: PIP with exclusion rings (lakes, etc.)

### Stage 4: Confidence Scoring

**Purpose**: Provide actionable uncertainty metrics.

**Strategy**: Distance-based scoring
- Calculate distance to nearest polygon edge
- Map distance → confidence score (0.0-1.0)
- Apply ambiguity penalty (multiple candidates)

**Thresholds**:
- > 0.1° (~11km): 0.98-1.0 confidence (high)
- 0.01°-0.1° (~1-11km): 0.85-0.98 (medium)
- < 0.01° (~1km): 0.70-0.85 (low)

**Design Rationale**: Users need to know when results are uncertain (borders, disputed areas).

## Data Model

### Binary Format Design

**Format**: JSON with automatic gzip compression

**Files**:
1. `geohash_index.json(.gz)`: `{geohash: [country_ids]}`
2. `polygons.json(.gz)`: `{country_id: {exterior: [[lat,lon]], holes: [...]}}`
3. `metadata.json(.gz)`: `{country_id: {name, iso2, iso3, continent, timezone}}`

**Compression**:
- All files are automatically compressed during build using gzip (level 9)
- ~66% size reduction (12 MB → 4 MB uncompressed → compressed)
- 100% lossless - data integrity verified
- Data loaders automatically detect and use compressed files (`.json.gz`)
- Automatic fallback to uncompressed files for compatibility

**Optimizations**:
- Coordinate simplification (Douglas-Peucker, tolerance 0.005°)
- Sparse geohash representation (only non-empty geohashes stored)
- JSON minification (no whitespace)
- Gzip compression (automatic, integrated into build pipeline)

**Alternative Formats** (future optimization):
- MessagePack: 30-50% smaller, faster parsing
- Protocol Buffers: Type-safe, efficient
- Custom binary format: Maximum efficiency

### Memory Footprint

**Target**: < 15 MB total

**Breakdown** (with compression):
- Geohash index: ~0.07 MB compressed (0.35 MB uncompressed)
- Polygons: ~4.0 MB compressed (11.6 MB uncompressed)
- Metadata: ~0.004 MB compressed (0.02 MB uncompressed)
- Code + overhead: ~1-2 MB
- **Total**: ~5-7 MB compressed files, ~13-15 MB in memory (meets < 15 MB target)

**Note**: Data files are stored compressed (~4 MB), but decompress to ~12 MB in memory during runtime. The compression reduces distribution size by ~66% while maintaining fast load times.

### Data Preparation

**Source**: Natural Earth (admin_0_countries.geojson) or similar

**Processing Pipeline** (`data_builder.py`):
1. Load GeoJSON
2. Simplify polygons (Douglas-Peucker, tolerance 0.005°)
3. Extract metadata (ISO codes, continent, timezone)
4. Build geohash index with PIP validation (only index points inside polygons)
5. Export to JSON (both uncompressed and compressed)
6. **Automatically compress files** using gzip (level 9)

### Compression Pipeline

During the build process, the data builder:
- Saves uncompressed `.json` files (for compatibility)
- Automatically creates compressed `.json.gz` files (for distribution)
- Verifies file sizes and compression ratios
- Ensures data integrity through verification

The compressed files are ~66% smaller and are automatically preferred by the data loaders.

## Performance Characteristics

### Lookup Time

**Target**: < 1 ms per lookup

**Breakdown**:
- Geohash encoding: ~0.01 ms
- Index lookup: ~0.05 ms (dict lookup)
- PIP test (1-3 candidates): ~0.2-0.6 ms
- Confidence calculation: ~0.1 ms
- **Total**: ~0.4-0.8 ms (well under 1 ms target)

### Scalability

- **Countries**: Supports 200+ countries
- **Lookups/sec**: ~1,000-2,000 (single-threaded Python)
- **Concurrent**: Thread-safe (read-only data structures)

### Trade-offs

**Accuracy vs Performance**:
- Polygon simplification reduces vertices → faster PIP
- Trade-off: Border accuracy ~100-1000m (acceptable for country-level)

**Memory vs Speed**:
- Full polygons → higher memory, same speed
- Simplified polygons → lower memory, same speed (preferred)
- **Compression**: Reduces file size by ~66% (12 MB → 4 MB), transparent to runtime (auto-decompression)

## Edge Cases

### 1. Border Points

**Problem**: Point on country border may match multiple countries.

**Solution**:
- Return country with highest confidence (distance to edge)
- If tied, return first match (deterministic)
- Low confidence score warns user of uncertainty

### 2. Geohash Boundaries

**Problem**: Point near geohash cell boundary may miss matches.

**Solution**:
- If primary geohash has no candidates, try 8 neighbors
- Increases lookup time slightly but handles edge cases

### 3. Oceans / No Match

**Problem**: Point in ocean has no country.

**Solution**:
- Return empty result (country=None)
- Confidence = 0.0
- User can check `result.country is None` to detect

### 4. Disputed Territories

**Problem**: Multiple countries claim same territory.

**Solution**:
- Return highest confidence match based on polygon data
- Document known disputes in metadata (future enhancement)
- Confidence score indicates uncertainty

### 5. Countries with Holes

**Problem**: Countries with lakes (e.g., Italy with Lake Como).

**Solution**:
- `point_in_polygon_with_holes()` handles exclusion rings
- Interior rings (holes) exclude points from result

## Security

**No Dynamic Code Execution**:
- No `eval()`, `exec()`, `compile()`
- All data is JSON (safe deserialization)
- Pure Python implementation (no native extensions)

**Input Validation**:
- Lat/lon bounds checking (-90 to 90, -180 to 180)
- Geohash character validation
- Polygon coordinate validation

## Extensibility

### Future Enhancements

1. **State/Province Resolution**:
   - Add state-level polygons
   - Hierarchical lookup: country → state
   - Larger memory footprint (~50-100 MB)

2. **City Resolution**:
   - Add city polygons
   - Requires significant data preparation
   - Memory footprint: ~200-500 MB

3. **Performance Optimization**:
   - Cython/C bindings for PIP algorithm
   - Parallel lookup for batch operations
   - Caching for repeated coordinates

4. **Data Formats**:
   - MessagePack/Protocol Buffers
   - Incremental loading (load countries on-demand)
   - ~~Compression (gzip/brotli)~~ ✅ **Implemented**: Automatic gzip compression (66% size reduction)

5. **Additional Metadata**:
   - Currency
   - Language
   - Phone country code
   - Regional subdivisions

## Testing Strategy

1. **Unit Tests**: Each module (geohash, PIP, confidence)
2. **Integration Tests**: End-to-end resolution pipeline
3. **Performance Tests**: Benchmark lookup time
4. **Accuracy Tests**: Validate against known coordinates
5. **Edge Case Tests**: Borders, oceans, holes

## Deployment Considerations

### AWS Lambda

- **Cold Start**: Data loading on first invocation
- **Optimization**: Pre-load data in global scope
- **Memory**: Fits in 128 MB Lambda (with margin)

### Edge / CDN

- **Format**: Pre-compiled binary data files
- **Loading**: Lazy load on first use
- **Caching**: In-memory cache after first load

### Offline / Air-Gapped

- **No Network**: All data bundled in package
- **Updates**: Manual data file replacement
- **Validation**: Checksum verification for data integrity
