# nflprojections
python library for fetching and aggregating NFL projections

## Installation

```bash
pip install -e .
```

## Package Organization

This package is organized into logical submodules for better code organization and maintainability:

- **`fetch/`** - Data fetching components (base_fetcher.py, nflcom_fetcher.py)
- **`parse/`** - Data parsing components (base_parser.py, nflcom_parser.py)  
- **`standardize/`** - Data standardization (base_standardizer.py)
- **`scoring/`** - Scoring systems (scoring.py, scoring_formats.py)
- **`combine/`** - Projection combination (projectioncombiner.py)
- **`sources/`** - Complete projection sources (nflcom.py, nflcom_refactored.py, projectionsource.py)

### Import Options

You can import components in two ways:

**Traditional imports** (backward compatible):
```python
from nflprojections import NFLComProjections, ProjectionCombiner, NFLComFetcher
```

**Organized submodule imports**:
```python
from nflprojections.sources import NFLComProjections
from nflprojections.combine import ProjectionCombiner  
from nflprojections.fetch import NFLComFetcher
```

## Architecture

This package uses a functional architecture with clear separation of concerns across five main areas:

1. **Data Source Fetch** - Retrieving data from different sources (web, files, APIs)
2. **Data Source Parse** - Converting raw data to structured DataFrames  
3. **Standardization** - Normalizing data formats across sources
4. **Scoring** - Applying fantasy scoring rules to statistical data
5. **Combining** - Aggregating projections using various algorithms

See [FUNCTIONAL_ARCHITECTURE.md](FUNCTIONAL_ARCHITECTURE.md) for detailed documentation.

## Quick Start

### Using the Refactored Implementation

```python
from nflprojections import NFLComProjectionsRefactored

# Create configured pipeline
nfl = NFLComProjectionsRefactored(season=2025, week=1, position="1")  # QB only

# Fetch projections
df = nfl.fetch_projections()
print(df.head())
```

### Using Individual Functional Components

```python
from nflprojections import NFLComFetcher, NFLComParser, ProjectionStandardizer

# Create pipeline components
fetcher = NFLComFetcher(position="1")  # QB only
parser = NFLComParser()
standardizer = ProjectionStandardizer({
    'player': 'plyr',
    'position': 'pos',
    'team': 'team',
    'fantasy_points': 'proj',
    'season': 'season',
    'week': 'week'
}, season=2025, week=1)

# Execute pipeline
raw_data = fetcher.fetch_raw_data()
parsed_df = parser.parse_raw_data(raw_data)
final_df = standardizer.standardize(parsed_df)
```

### Combining Projections from Multiple Sources

```python
from nflprojections import ProjectionCombiner, CombinationMethod

# Assume you have projections from multiple sources
combiner = ProjectionCombiner()

# Simple average
combined = combiner.combine_projections(
    [source1_df, source2_df, source3_df],
    method=CombinationMethod.AVERAGE
)

# Weighted average with custom weights
combined = combiner.combine_projections(
    [source1_df, source2_df, source3_df],
    method=CombinationMethod.WEIGHTED_AVERAGE,
    weights={'source_0': 0.5, 'source_1': 0.3, 'source_2': 0.2}
)

# Other methods available: MEDIAN, DROP_HIGH_LOW, CONFIDENCE_BANDS
```

## Usage

### NFL.com Projections (Original Interface)

```python
from nflprojections import NFLComProjections

# Create parser for 2025 season projections
nfl = NFLComProjections(season=2025, week=1)

# Fetch all position projections
df = nfl.fetch_projections()

# Fetch quarterback projections only
qb_nfl = NFLComProjections(season=2025, position="1")  # 1 = QB
qb_df = qb_nfl.fetch_projections()
```

#### Position Filters
- `"0"` - All positions (default)
- `"1"` - Quarterbacks (QB)
- `"2"` - Running backs (RB)
- `"3"` - Wide receivers (WR) 
- `"4"` - Tight ends (TE)
- `"5"` - Kickers (K)
- `"6"` - Defense/Special Teams (DST)

### Fantasy Scoring

```python
from nflprojections.scoring import Scorer
from nflprojections.scoring_formats import StandardScoring, PPRScoring

# Create scorer with standard scoring
scorer = Scorer(StandardScoring())

# Calculate fantasy points from stats
stats = {
    'pass_yd': 300,
    'pass_td': 2, 
    'rush_yd': 50,
    'rec': 6,
    'rec_yd': 80
}

fantasy_points = scorer.calculate_fantasy_points(stats)
print(f"Fantasy Points: {fantasy_points}")

# Convert entire DataFrame
stat_columns = {
    'pass_yd': 'passing_yards',
    'pass_td': 'passing_tds',
    'rush_yd': 'rushing_yards'
}

df_with_points = scorer.convert_dataframe(stats_df, stat_columns)
```

### Combination Methods

The `ProjectionCombiner` supports multiple algorithms:

- **AVERAGE**: Simple average across all sources
- **WEIGHTED_AVERAGE**: Weighted average with custom source weights  
- **MEDIAN**: Median value across sources
- **DROP_HIGH_LOW**: Average after removing highest and lowest values
- **CONFIDENCE_BANDS**: Average with confidence interval calculations

```python
from nflprojections import ProjectionCombiner, CombinationMethod

combiner = ProjectionCombiner()

# Drop high and low outliers before averaging
result = combiner.combine_projections(
    projections_list,
    method=CombinationMethod.DROP_HIGH_LOW
)

# Generate confidence bands
result = combiner.combine_projections(
    projections_list, 
    method=CombinationMethod.CONFIDENCE_BANDS,
    confidence_level=0.95
)
```

## Data Format

The returned DataFrame uses standardized column names:
- `plyr` - Player name
- `pos` - Position
- `team` - Team abbreviation  
- `proj` - Fantasy points projection
- `season` - Season year
- `week` - Week number

## Benefits of Functional Architecture

1. **Modularity**: Each component has a single responsibility
2. **Extensibility**: Easy to add new data sources and algorithms
3. **Testability**: Components can be tested independently
4. **Reusability**: Components can be mixed and matched
5. **Maintainability**: Changes isolated to specific components

## Running the Demo

```bash
python demo_functional_architecture.py
```

This demonstrates the new architecture with examples of each functional component.

## Testing

```bash
# Test new functional components
python -m pytest tests/test_functional_components.py -v

# Test all components  
python -m pytest tests/ -v
```
