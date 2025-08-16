# Quick Start

Get up and running with NFLProjections in just a few minutes.

## Basic Usage

### Using the Functional Architecture

The recommended approach is to use the functional architecture with improved modularity:

```python
from nflprojections import NFLComProjections

# Create NFL.com projections instance
nfl = NFLComProjections(
    season=2025, 
    week=1,
    position="1"  # QB only
)

# Fetch projections
projections = nfl.fetch_projections()
print(f"Retrieved {len(projections)} projections")

# Get pipeline information
pipeline_info = nfl.get_pipeline_info()
for key, value in pipeline_info.items():
    print(f"{key}: {value}")

# Validate the data pipeline
validation = nfl.validate_data_pipeline()
print("Pipeline validation:", validation)
```

### Using Individual Functional Components

For more control, you can use individual components:

```python
from nflprojections.fetch import NFLComFetcher
from nflprojections.parse import NFLComParser
from nflprojections.standardize import ProjectionStandardizer

# Step 1: Fetch raw data
fetcher = NFLComFetcher(position="1")  # QB only
raw_data = fetcher.fetch_raw_data(season=2025, week=1)

# Step 2: Parse raw data
parser = NFLComParser()
parsed_df = parser.parse_raw_data(raw_data)

# Step 3: Standardize the data
standardizer = ProjectionStandardizer({
    'player': 'plyr',
    'position': 'pos',
    'team': 'team',
    'fantasy_points': 'proj',
    'season': 'season',
    'week': 'week'
}, season=2025, week=1)
standardized_data = standardizer.standardize(parsed_df)

print(f"Processed {len(standardized_data)} players")
```

### Combining Projections from Multiple Sources

```python
from nflprojections import ProjectionCombiner, CombinationMethod

# Sample projection data (normally from different sources)
projections_list = [
    [{'plyr': 'Player1', 'proj': 20.5}, {'plyr': 'Player2', 'proj': 15.3}],
    [{'plyr': 'Player1', 'proj': 22.1}, {'plyr': 'Player2', 'proj': 14.8}]
]

# Combine using different methods
combiner = ProjectionCombiner()

# Average method
avg_projections = combiner.combine(
    projections_list, 
    method=CombinationMethod.AVERAGE
)

print("Combined projections:", avg_projections)
```

## Data Format

All standardized data uses consistent column names:

- `plyr` - Player name
- `pos` - Position (QB, RB, WR, TE, etc.)
- `team` - Team abbreviation
- `proj` - Fantasy points projection
- `season` - Season year
- `week` - Week number

## Fantasy Scoring

Apply different scoring systems to statistical projections:

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

print(f"Standard: {points}, PPR: {ppr_points}")
```

## Error Handling

The library includes validation and error handling:

```python
from nflprojections import NFLComProjections

try:
    nfl = NFLComProjections(season=2025, week=1)
    
    # Validate pipeline before fetching
    validation = nfl.validate_data_pipeline()
    if not all(validation.values()):
        print("Pipeline validation failed:", validation)
    else:
        projections = nfl.fetch_projections()
        print(f"Successfully retrieved {len(projections)} projections")
        
except Exception as e:
    print(f"Error: {e}")
```

## Next Steps

- Learn more about the [architecture](architecture/overview.md)
- Explore the [API reference](api/sources.md)
- See [advanced examples](examples/advanced.md)