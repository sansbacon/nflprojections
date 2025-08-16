# Sources API Reference

The sources module provides complete projection sources that combine fetching, parsing, and standardization into easy-to-use interfaces.

## Main Classes

::: nflprojections.sources.projectionsource.ProjectionSource
    options:
      show_root_heading: true
      show_source: false

::: nflprojections.sources.nflcom.NFLComProjections
    options:
      show_root_heading: true
      show_source: false

::: nflprojections.sources.nflcom_refactored.NFLComProjectionsRefactored
    options:
      show_root_heading: true
      show_source: false

## Usage Examples

### NFLComProjections (Original)

The original NFL.com projections interface:

```python
from nflprojections import NFLComProjections

# Basic usage
nfl = NFLComProjections(season=2025, week=1)
projections = nfl.fetch_projections()

# Position-specific
qb_nfl = NFLComProjections(season=2025, week=1, position="QB")
qb_projections = qb_nfl.fetch_projections()
```

### NFLComProjectionsRefactored (Recommended)

The improved refactored implementation with additional features:

```python
from nflprojections import NFLComProjectionsRefactored

# Create instance
nfl = NFLComProjectionsRefactored(
    season=2025, 
    week=1,
    position="1",  # QB
    use_names=False
)

# Fetch projections
projections = nfl.fetch_projections()

# Get pipeline information
info = nfl.get_pipeline_info()
print("Fetcher:", info['fetcher'])
print("Parser:", info['parser'])
print("Standardizer:", info['standardizer'])

# Validate pipeline
validation = nfl.validate_data_pipeline()
for component, is_valid in validation.items():
    print(f"{component}: {'✓' if is_valid else '✗'}")
```

### ProjectionSource (Flexible)

The most flexible interface supporting both legacy and composed modes:

```python
from nflprojections import ProjectionSource
from nflprojections.fetch import NFLComFetcher
from nflprojections.parse import NFLComParser
from nflprojections.standardize import ProjectionStandardizer

# Composed mode - combine your own components
source = ProjectionSource(
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

# Use the composed pipeline
projections = source.fetch_projections()
validation = source.validate_data_pipeline()

# Legacy mode - traditional usage
legacy_source = ProjectionSource(
    source_name="my_source",
    column_mapping={'player': 'plyr'},
    season=2025,
    week=1
)
```

## Return Format

All projection sources return data in a standardized format:

```python
[
    {
        'plyr': 'Josh Allen',        # Player name
        'pos': 'QB',                 # Position
        'team': 'BUF',              # Team abbreviation
        'proj': 23.4,               # Fantasy projection
        'season': 2025,             # Season
        'week': 1                   # Week number
    },
    # ... more players
]
```

## Error Handling

```python
try:
    nfl = NFLComProjectionsRefactored(season=2025, week=1)
    
    # Validate before fetching
    validation = nfl.validate_data_pipeline()
    if not all(validation.values()):
        print("Pipeline validation failed:", validation)
        return
    
    projections = nfl.fetch_projections()
    print(f"Retrieved {len(projections)} projections")
    
except ConnectionError:
    print("Could not connect to data source")
except ValueError as e:
    print(f"Invalid parameters: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Configuration Options

### Position Filtering

```python
# NFL.com position codes
positions = {
    "0": "All positions", 
    "1": "QB",
    "2": "RB", 
    "3": "WR",
    "4": "TE",
    "5": "K",
    "6": "DEF"
}

nfl = NFLComProjectionsRefactored(position="2")  # RB only
```

### Season and Week

```python
# Current season, specific week
nfl = NFLComProjectionsRefactored(season=2025, week=5)

# Season projections (week=None)
nfl = NFLComProjectionsRefactored(season=2025, week=None)
```

### Custom Column Mapping

```python
custom_mapping = {
    'player_name': 'plyr',
    'pos': 'pos', 
    'team_abbr': 'team',
    'projected_points': 'proj'
}

nfl = NFLComProjectionsRefactored(
    column_mapping=custom_mapping,
    season=2025,
    week=1
)
```