# Functional Architecture

The NFLProjections package uses a functional architecture with clear separation of concerns. This page provides detailed implementation guidance for each component.

## Component Details

### 1. Data Source Fetch

**Purpose**: Handles retrieving raw data from different sources (web APIs, files, databases)

**Base Classes**:
- `DataSourceFetcher`: Abstract base class for all fetchers
- `WebDataFetcher`: Base for web-based data sources  
- `FileDataFetcher`: Base for file-based data sources

**Key Methods**:
- `fetch_raw_data(**params)`: Retrieve raw data
- `validate_connection()`: Check if data source is accessible

**Example Usage**:
```python
from nflprojections.fetch import NFLComFetcher

fetcher = NFLComFetcher(position="1")  # QB only
raw_html = fetcher.fetch_raw_data(season=2025)
```

### 2. Data Source Parse

**Purpose**: Handles parsing raw data into structured DataFrames

**Base Classes**:
- `DataSourceParser`: Abstract base class for all parsers
- `HTMLTableParser`: Base for HTML table parsing
- `CSVParser`: For CSV data parsing
- `JSONParser`: For JSON data parsing

**Key Methods**:
- `parse_raw_data(raw_data)`: Convert raw data to DataFrame
- `validate_parsed_data(df)`: Validate parsed structure

**Example Usage**:
```python
from nflprojections.parse import NFLComParser

parser = NFLComParser()
df = parser.parse_raw_data(raw_html)
```

### 3. Standardization

**Purpose**: Handles converting parsed data to common format across all sources

**Base Classes**:
- `DataStandardizer`: Abstract base for all standardizers
- `ProjectionStandardizer`: For NFL projection data
- `StatStandardizer`: For NFL statistical data

**Key Methods**:
- `standardize(df)`: Convert to standard format
- `remap_columns(df)`: Apply column mappings
- `standardize_players/positions/teams()`: Apply name standardization

**Example Usage**:
```python
from nflprojections.standardize import ProjectionStandardizer

column_mapping = {
    'player': 'plyr',
    'position': 'pos', 
    'team': 'team',
    'fantasy_points': 'proj',
    'season': 'season',
    'week': 'week'
}

standardizer = ProjectionStandardizer(column_mapping, season=2025, week=1)
standardized_df = standardizer.standardize(parsed_df)
```

### 4. Scoring

**Purpose**: Handles applying fantasy scoring rules to statistical data

**Classes**:
- `Scorer`: Converts statistics to fantasy points
- Various `ScoringFormat` classes for different league types

**Example Usage**:
```python
from nflprojections.scoring import StandardScoring, PPRScoring

# Standard scoring
standard = StandardScoring()
points = standard.calculate_points({
    'passing_yards': 300,
    'passing_tds': 2,
    'rushing_yards': 50,
    'rushing_tds': 1
})

# PPR scoring
ppr = PPRScoring()
ppr_points = ppr.calculate_points({
    'receptions': 8,
    'receiving_yards': 120,
    'receiving_tds': 1
})
```

### 5. Combining

**Purpose**: Handles aggregating projections using various algorithms

**Classes**:
- `ProjectionCombiner`: Main combination engine
- `CombinationMethod`: Enum of available methods

**Example Usage**:
```python
from nflprojections.combine import ProjectionCombiner, CombinationMethod

combiner = ProjectionCombiner()

# Average multiple projections
combined = combiner.combine(
    projections_list=[proj1, proj2, proj3],
    method=CombinationMethod.AVERAGE
)

# Weighted average with custom weights
weighted = combiner.combine(
    projections_list=[proj1, proj2, proj3],
    method=CombinationMethod.WEIGHTED_AVERAGE,
    weights=[0.5, 0.3, 0.2]
)
```

## Usage Options

### Option 1: Individual Components

Use components separately for maximum control:

```python
from nflprojections.fetch import NFLComFetcher
from nflprojections.parse import NFLComParser  
from nflprojections.standardize import ProjectionStandardizer

# Step 1: Fetch
fetcher = NFLComFetcher(position="1", stat_category="projectedStats")
raw_data = fetcher.fetch_raw_data(season=2025, week=1)

# Step 2: Parse
parser = NFLComParser(source_name="NFL.com")
parsed_df = parser.parse_raw_data(raw_data)

# Step 3: Standardize
column_mapping = {
    'player': 'plyr',
    'position': 'pos',
    'team': 'team', 
    'fantasy_points': 'proj'
}
standardizer = ProjectionStandardizer(column_mapping, season=2025, week=1)
final_df = standardizer.standardize(parsed_df)
```

### Option 2: Refactored Implementation

Use the pre-configured refactored class:

```python
from nflprojections import NFLComProjectionsRefactored

nfl_refactored = NFLComProjectionsRefactored(
    season=2025,
    week=1, 
    position="1",
    use_names=False
)

# Get projections
projections = nfl_refactored.fetch_projections()

# Pipeline information
pipeline_info = nfl_refactored.get_pipeline_info()
print("Pipeline components:", pipeline_info)

# Validation
validation_results = nfl_refactored.validate_data_pipeline()
print("Validation:", validation_results)
```

### Option 3: Combine Multiple Sources

Aggregate projections from different sources:

```python
from nflprojections import ProjectionCombiner, CombinationMethod

# Get projections from multiple sources (example)
nfl_projections = get_nfl_projections()
espn_projections = get_espn_projections()
fp_projections = get_fantasypros_projections()

# Combine using average
combiner = ProjectionCombiner()
combined_projections = combiner.combine([
    nfl_projections,
    espn_projections, 
    fp_projections
], method=CombinationMethod.AVERAGE)

print(f"Combined {len(combined_projections)} player projections")
```

### Option 4: Composed ProjectionSource

Use the flexible ProjectionSource for custom pipelines:

```python
from nflprojections import ProjectionSource
from nflprojections.fetch import NFLComFetcher
from nflprojections.parse import NFLComParser
from nflprojections.standardize import ProjectionStandardizer

# Create composed projection source
proj_source = ProjectionSource(
    fetcher=NFLComFetcher(position="1"),
    parser=NFLComParser(),
    standardizer=ProjectionStandardizer({
        'player': 'plyr',
        'position': 'pos',
        'fantasy_points': 'proj'
    }),
    season=2025,
    week=1
)

# Use like any other projection source
projections = proj_source.fetch_projections()

# Get pipeline information and validation
pipeline_info = proj_source.get_pipeline_info()
validation_results = proj_source.validate_data_pipeline()
print("Pipeline validation:", validation_results)
```

## Adding New Data Sources

To add a new data source, implement a Fetcher + Parser pair:

```python
# Step 1: Create custom fetcher
class CustomFetcher(DataSourceFetcher):
    def __init__(self, **kwargs):
        super().__init__("custom_source")
        # Initialize source-specific parameters
    
    def fetch_raw_data(self, **params):
        # Implement data fetching logic
        return raw_data
    
    def validate_connection(self):
        # Test if source is accessible
        return True

# Step 2: Create custom parser  
class CustomParser(DataSourceParser):
    def __init__(self):
        super().__init__("custom_source")
    
    def parse_raw_data(self, raw_data):
        # Parse raw data into DataFrame
        return parsed_df
    
    def validate_parsed_data(self, df):
        # Validate structure
        return not df.empty

# Step 3: Use in pipeline
fetcher = CustomFetcher()
parser = CustomParser()
standardizer = ProjectionStandardizer(column_mapping)

# Build pipeline
raw_data = fetcher.fetch_raw_data()
parsed_df = parser.parse_raw_data(raw_data)
final_df = standardizer.standardize(parsed_df)
```

## Migration from Original Code

The original `ProjectionSource` and `NFLComProjections` classes are still available for backward compatibility:

### Old Way
```python
from nflprojections import NFLComProjections

nfl = NFLComProjections(season=2025, week=1)
df = nfl.fetch_projections()
```

### New Way
```python
from nflprojections import NFLComProjectionsRefactored

nfl = NFLComProjectionsRefactored(season=2025, week=1)
df = nfl.fetch_projections()

# Additional benefits: 
pipeline_info = nfl.get_pipeline_info()
validation = nfl.validate_data_pipeline()
```

## Legacy Compatibility

The ProjectionSource class maintains full backward compatibility:

```python
from nflprojections import ProjectionSource

# Legacy mode - works exactly as before
legacy_source = ProjectionSource(
    source_name="my_source",
    column_mapping=column_mapping,
    slate_name="main", 
    season=2025,
    week=1
)

# All existing methods work unchanged
standardized_names = legacy_source.standardize_players(player_names)
```