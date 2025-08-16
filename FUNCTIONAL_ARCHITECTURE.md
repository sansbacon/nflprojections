# Functional Architecture Guide

## Overview

The NFLProjections package has been refactored into a functional architecture with clear separation of concerns. This document explains the new architecture and how to use it.

## Architecture Components

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

## Using the Refactored Architecture

### Option 1: Use Individual Components

```python
from nflprojections import NFLComFetcher, NFLComParser, ProjectionStandardizer

# Create pipeline components
fetcher = NFLComFetcher(position="1")  # QB only
parser = NFLComParser()
standardizer = ProjectionStandardizer(column_mapping, season=2025)

# Execute pipeline
raw_data = fetcher.fetch_raw_data()
parsed_df = parser.parse_raw_data(raw_data)
final_df = standardizer.standardize(parsed_df)
```

### Option 2: Use Refactored Implementation

```python
from nflprojections import NFLComProjectionsRefactored

# Create configured pipeline
nfl = NFLComProjectionsRefactored(season=2025, week=1, position="1")

# Execute full pipeline
projections_df = nfl.fetch_projections()

# Validate pipeline
validation = nfl.validate_data_pipeline()
```

### Option 3: Combine Multiple Sources

```python
from nflprojections import NFLComProjectionsRefactored, ProjectionCombiner, CombinationMethod

# Get projections from multiple sources
source1 = NFLComProjectionsRefactored(season=2025, position="1")
# source2 = AnotherSourceProjections(...)  # Add other sources
# source3 = YetAnotherSourceProjections(...)

proj1 = source1.fetch_projections()
# proj2 = source2.fetch_projections()
# proj3 = source3.fetch_projections()

# Combine using different methods
combiner = ProjectionCombiner()
combined = combiner.combine_projections(
    [proj1],  # Add [proj1, proj2, proj3] when you have multiple sources
    method=CombinationMethod.WEIGHTED_AVERAGE,
    weights={'source_0': 1.0}  # Adjust weights as needed
)
```

## Benefits of Functional Architecture

### 1. Separation of Concerns
- Each component has a single, well-defined responsibility
- Changes to fetching don't affect parsing or standardization
- Easy to understand what each component does

### 2. Extensibility
- Add new data sources by implementing Fetcher + Parser
- Add new combination algorithms to ProjectionCombiner
- Add new standardization rules without changing existing code

### 3. Testability
- Each component can be tested independently
- Mock components can be easily substituted
- Pipeline validation at each step

### 4. Reusability
- Fetchers can be reused across different parsers
- Standardizers can be reused across different sources
- Combiners work with any standardized projection data

### 5. Maintainability
- Clear interfaces make relationships explicit
- Configuration is centralized and explicit
- Easier to debug problems in isolated components

## Migration from Original Code

The original `ProjectionSource` and `NFLComProjections` classes are still available for backward compatibility. However, new development should use the functional components or the refactored implementations.

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

## Adding New Data Sources

To add a new data source, create two classes:

1. **Fetcher** (inherits from appropriate base)
2. **Parser** (inherits from appropriate base)

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