# ETR (Establish The Run) Integration

This document describes the ETR (Establish The Run) projection source integration that follows the same functional architecture patterns as other sources like NFL.com.

!!! note "Integration with Main API"
    ETR projections are fully integrated into the main API. See the [Sources API Reference](api/sources.md) for complete usage examples alongside other projection sources.

## ETR Components

### ETR Components

- **`ETRFetcher`** - Handles fetching data from ETR website
- **`ETRParser`** - Parses HTML data from ETR into structured format
- **`ETRProjections`** - ETR projection class using functional architecture

## Usage Examples

### Using ETR Projections

```python
from nflprojections import ETRProjections

# Create configured pipeline
etr = ETRProjections(
    season=2024, 
    week=1, 
    position="qb",
    scoring="ppr"
)

# Fetch projections
projections = etr.fetch_projections()

# Get pipeline information
pipeline_info = etr.get_pipeline_info()
print("Pipeline components:", pipeline_info)

# Validation
validation_results = etr.validate_data_pipeline()
print("Validation:", validation_results)
```

### Individual Functional Components

```python
from nflprojections.fetch import ETRFetcher
from nflprojections.parse import ETRParser
from nflprojections.standardize import ProjectionStandardizer

# Create pipeline components
fetcher = ETRFetcher(position="rb", scoring="half-ppr", week=2)
parser = ETRParser()
standardizer = ProjectionStandardizer({
    'player': 'plyr',
    'position': 'pos',
    'team': 'team',
    'fantasy_points': 'proj',
    'season': 'season',
    'week': 'week'
}, season=2024, week=2)

# Execute pipeline
raw_data = fetcher.fetch_raw_data()
parsed_data = parser.parse_raw_data(raw_data)
final_data = standardizer.standardize(parsed_data)
```

### Legacy Implementation

```python
from nflprojections import ETRProjections

# Backward compatible usage - same API, refactored implementation
etr = ETRProjections(season=2024, week=1, position="wr", scoring="ppr")
projections = etr.fetch_projections()
```

## Configuration Options

### Position Filters
- `"all"` - All positions
- `"qb"` - Quarterbacks
- `"rb"` - Running backs  
- `"wr"` - Wide receivers
- `"te"` - Tight ends
- `"k"` - Kickers
- `"dst"` - Defense/Special Teams

### Scoring Formats
- `"ppr"` - Point Per Reception
- `"half-ppr"` - Half Point Per Reception  
- `"standard"` - Standard scoring

### Time Periods
- `week=None` - Season totals (default)
- `week=1-18` - Specific week projections

## Column Mapping

The ETR implementation uses flexible column mapping to handle different data formats:

```python
# Default mapping
DEFAULT_COLUMN_MAPPING = {
    'player': 'plyr',
    'position': 'pos',
    'team': 'team', 
    'fantasy_points': 'proj',
    'season': 'season',
    'week': 'week'
}

# Custom mapping example
custom_mapping = {
    'player_name': 'plyr',
    'pos': 'pos',
    'team_abbr': 'team',
    'projected_points': 'proj',
    'season': 'season',
    'week': 'week'
}

etr = ETRProjectionsRefactored(column_mapping=custom_mapping)
```

## Architecture Integration

The ETR implementation follows the same functional architecture as NFL.com:

1. **Data Source Fetch** - `ETRFetcher` handles HTTP requests and URL building
2. **Data Source Parse** - `ETRParser` converts HTML to structured data
3. **Standardization** - `ProjectionStandardizer` normalizes column names and formats
4. **Pipeline Integration** - `ETRProjectionsRefactored` combines all components

## Import Structure

**Main high-level APIs:**
```python
from nflprojections import ETRProjections, ETRProjectionsRefactored
```

**Specific components:**
```python
from nflprojections.fetch import ETRFetcher
from nflprojections.parse import ETRParser
```

## Testing

Comprehensive tests are included in `tests/test_etr.py` covering:

- Fetcher URL building and configuration
- Parser HTML processing and data extraction
- Legacy and refactored class functionality
- Column mapping and standardization
- Integration pipeline testing

Run ETR tests:
```bash
python -m pytest tests/test_etr.py -v
```

## Migration from Original Code

If you have existing ETR code, you can migrate to the new architecture:

### Old Way (If you had custom ETR implementation)
```python
# Custom implementation needed
```

### New Way
```python
from nflprojections import ETRProjections

etr = ETRProjections(season=2024, week=1, position="rb")
projections = etr.fetch_projections()

# Additional benefits:
pipeline_info = etr.get_pipeline_info()
validation = etr.validate_data_pipeline()
```

## Notes

1. **URL Structure**: The implementation uses educated guesses about ETR's URL structure. You may need to adjust the `BASE_URL` and URL building logic in `ETRFetcher` based on the actual ETR website structure.

2. **HTML Parsing**: The `ETRParser` includes flexible HTML parsing logic that can handle various table structures. You may need to customize the parsing logic based on ETR's specific HTML format.

3. **Error Handling**: The implementation includes proper error handling for network requests and data validation.

4. **Extensibility**: The functional architecture makes it easy to swap out components or add new functionality without affecting other parts of the system.

For working examples, see `examples/etr_usage.py`.