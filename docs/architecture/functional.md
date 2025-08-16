# Functional Architecture

The NFLProjections package uses a functional architecture with clear separation of concerns. This design provides modularity, testability, and extensibility through well-defined component interfaces.

## Component Details

### 1. Data Source Fetch (`base_fetcher.py`)

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
from nflprojections import NFLComFetcher

fetcher = NFLComFetcher(position="1")  # QB only
raw_html = fetcher.fetch_raw_data(season=2025)
```

### 2. Data Source Parse (`base_parser.py`)

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
from nflprojections import NFLComParser

parser = NFLComParser()
df = parser.parse_raw_data(raw_html)
```

### 3. Standardization (`base_standardizer.py`)

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
from nflprojections import ProjectionStandardizer

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

### 4. Scoring (`scoring.py`)

**Purpose**: Handles applying fantasy scoring rules to statistical data

**Classes**:
- `Scorer`: Converts statistics to fantasy points
- Various `ScoringFormat` classes for different league types

**Example Usage**:
```python
from nflprojections.scoring import Scorer
from nflprojections.scoring_formats import StandardScoring

scorer = Scorer(StandardScoring())
fantasy_points = scorer.calculate_fantasy_points({
    'pass_yd': 300,
    'pass_td': 2,
    'rush_yd': 50
})
```

### 5. Combining (`projectioncombiner.py`)

**Purpose**: Handles combining projections from multiple sources using various algorithms

**Classes**:
- `ProjectionCombiner`: Main combiner class
- `CombinationMethod`: Enum of available methods

**Available Methods**:
- `AVERAGE`: Simple average of all sources
- `WEIGHTED_AVERAGE`: Weighted average with custom weights
- `MEDIAN`: Median value across sources
- `DROP_HIGH_LOW`: Average after removing highest and lowest
- `CONFIDENCE_BANDS`: Average with confidence intervals

**Example Usage**:
```python
from nflprojections import ProjectionCombiner, CombinationMethod

combiner = ProjectionCombiner()

# Simple average
combined = combiner.combine_projections(
    [source1_df, source2_df, source3_df], 
    method=CombinationMethod.AVERAGE
)

# Weighted average  
weights = {'source_0': 0.5, 'source_1': 0.3, 'source_2': 0.2}
combined = combiner.combine_projections(
    [source1_df, source2_df, source3_df],
    method=CombinationMethod.WEIGHTED_AVERAGE,
    weights=weights
)
```

## Usage Options

### Option 1: Individual Components

Use components separately for maximum control:

```python
from nflprojections import NFLComFetcher, NFLComParser, ProjectionStandardizer

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

### Option 2: Configured Pipeline

Use the pre-configured class:

```python
from nflprojections import NFLComProjections

nfl = NFLComProjections(
    season=2025,
    week=1, 
    position="1",
    use_names=False
)

# Get projections
projections = nfl.fetch_projections()

# Pipeline information
pipeline_info = nfl.get_pipeline_info()
print("Pipeline components:", pipeline_info)

# Validation
validation_results = nfl.validate_data_pipeline()
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

The `ProjectionSource` class now supports composition of functional components, providing a unified interface for the entire pipeline:

```python
from nflprojections import ProjectionSource
from nflprojections import NFLComFetcher, NFLComParser, ProjectionStandardizer

# Create functional components
fetcher = NFLComFetcher(position="1")  # QB only
parser = NFLComParser()

column_mapping = {
    'player': 'plyr',
    'position': 'pos',
    'team': 'team',
    'fantasy_points': 'proj',
    'season': 'season',
    'week': 'week'
}
standardizer = ProjectionStandardizer(column_mapping, season=2025, week=1)

# Create composed ProjectionSource
proj_source = ProjectionSource(
    fetcher=fetcher,
    parser=parser,
    standardizer=standardizer,
    season=2025,
    week=1
)

# Execute full pipeline with single method call
projections_df = proj_source.fetch_projections()

# Get pipeline information
pipeline_info = proj_source.get_pipeline_info()
print("Pipeline components:", pipeline_info)

# Validate pipeline functionality  
validation_results = proj_source.validate_data_pipeline()
print("Pipeline validation:", validation_results)
```

## Benefits of Functional Architecture

### 1. Separation of Concerns
- **Fetching**: Handles data source connections and retrieval
- **Parsing**: Handles data structure interpretation 
- **Standardizing**: Handles format normalization
- **Combining**: Handles projection aggregation algorithms
- Each component has a single, well-defined responsibility
- Changes to one component don't affect others

### 2. Extensibility
- Add new data sources by implementing Fetcher + Parser
- Easy to add new combination algorithms to ProjectionCombiner
- Easy to customize standardization rules
- Reuse existing components across different sources

### 3. Testability
- Each component can be tested independently
- Mock components can be easily substituted
- Pipeline validation at each step
- Clear interfaces make it easy to understand relationships

### 4. Reusability
- Fetchers can be reused across different parsers
- Standardizers can be reused across different sources
- Combiners work with any standardized projection data
- Components compose together flexibly

### 5. Maintainability
- Clear interfaces make relationships explicit
- Configuration is centralized and explicit
- Easier to debug problems in isolated components
- Changes to one component don't affect others

### 6. Backward Compatibility
- Existing code continues to work without changes
- Migration path available for new functionality
- No breaking changes to existing APIs
- Legacy ProjectionSource class maintains full compatibility

## Adding New Data Sources

To add a new data source, implement a Fetcher + Parser pair:

```python
from nflprojections import WebDataFetcher, HTMLTableParser

class MySourceFetcher(WebDataFetcher):
    def __init__(self):
        super().__init__("my_source", "https://my-api.com/data")
    
    def fetch_raw_data(self, **params):
        # Custom fetching logic
        return super().fetch_raw_data(**params)

class MySourceParser(HTMLTableParser):
    def parse_raw_data(self, raw_data):
        # Custom parsing logic
        return super().parse_raw_data(raw_data)
    
    def validate_parsed_data(self, df):
        # Custom validation logic
        return not df.empty
```

Then use with the standard pipeline:

```python
fetcher = MySourceFetcher()
parser = MySourceParser()
standardizer = ProjectionStandardizer(my_column_mapping, season=2025)

# Execute pipeline
raw_data = fetcher.fetch_raw_data()
parsed_df = parser.parse_raw_data(raw_data)
final_df = standardizer.standardize(parsed_df)
```

## Migration from Original Code

The original `ProjectionSource` class is still available for backward compatibility, but the main projection classes now use the refactored functional architecture:

### Current Implementation
```python
from nflprojections import NFLComProjections

nfl = NFLComProjections(season=2025, week=1)
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