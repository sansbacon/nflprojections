# Player Matching API Reference

The matching module provides fuzzy player matching functionality to handle variations in player names and team abbreviations across different projection sources.

## Classes

### PlayerMatcher

Matches players across different projection sources using fuzzy string matching with Python's standard library `difflib.SequenceMatcher`.

#### Constructor

```python
PlayerMatcher(
    name_threshold: float = 0.7,
    position_threshold: float = 0.8, 
    team_threshold: float = 0.5,
    overall_threshold: float = 0.65
)
```

**Parameters:**
- `name_threshold`: Minimum similarity for player names (0.0-1.0)
- `position_threshold`: Minimum similarity for positions (0.0-1.0)  
- `team_threshold`: Minimum similarity for team names (0.0-1.0)
- `overall_threshold`: Minimum overall similarity score (0.0-1.0)

#### Methods

##### match_players()

```python
match_players(
    source1: Union[List[Dict[str, Any]], pd.DataFrame],
    source2: Union[List[Dict[str, Any]], pd.DataFrame]
) -> List[MatchResult]
```

Find all potential matches between two data sources that meet the similarity thresholds.

##### get_best_matches()

```python
get_best_matches(
    source1: Union[List[Dict[str, Any]], pd.DataFrame],
    source2: Union[List[Dict[str, Any]], pd.DataFrame],
    allow_duplicates: bool = False
) -> List[MatchResult]
```

Get the best match for each player in source1. If `allow_duplicates=False`, each player from source2 can only match once.

##### create_merged_data()

```python
create_merged_data(
    matches: List[MatchResult],
    merge_strategy: str = 'prefer_source1'
) -> List[Dict[str, Any]]
```

Create merged player data from match results.

**Merge strategies:**
- `'prefer_source1'`: Use source1 player info, add source2 projections
- `'prefer_source2'`: Use source2 player info, add source1 projections  
- `'combine'`: Combine all fields, separate projection columns

### MatchResult

Data class containing the result of a player matching operation.

**Attributes:**
- `source1_index`: Index in first data source
- `source2_index`: Index in second data source
- `source1_player`: Player record from first source
- `source2_player`: Player record from second source
- `similarity`: Overall similarity score (0.0-1.0)
- `match_fields`: Dictionary of field-specific similarity scores

## Enhanced ProjectionCombiner

The existing `ProjectionCombiner` has been enhanced to optionally use fuzzy matching.

### Constructor Enhancement

```python
ProjectionCombiner(
    method: CombinationMethod = CombinationMethod.AVERAGE,
    use_fuzzy_matching: bool = False,
    matcher_config: Optional[Dict[str, float]] = None
)
```

**New parameters:**
- `use_fuzzy_matching`: Enable fuzzy player matching (default: False)
- `matcher_config`: Configuration dictionary for PlayerMatcher thresholds

## Usage Examples

### Basic Player Matching

```python
from nflprojections.matching import PlayerMatcher

# Sample data with name variations
source1 = [
    {"plyr": "Josh Allen", "pos": "QB", "team": "BUF", "proj": 25.4},
    {"plyr": "Jonathan Taylor", "pos": "RB", "team": "IND", "proj": 18.2},
]

source2 = [
    {"plyr": "J. Allen", "pos": "QB", "team": "Buffalo", "proj": 24.1},
    {"plyr": "Jon Taylor", "pos": "RB", "team": "Indianapolis", "proj": 17.9},
]

# Create matcher with custom thresholds
matcher = PlayerMatcher(
    name_threshold=0.6,
    team_threshold=0.4,
    overall_threshold=0.5
)

# Find matches
matches = matcher.match_players(source1, source2)

for match in matches:
    print(f"Match (similarity: {match.similarity:.3f}):")
    print(f"  {match.source1_player['plyr']} -> {match.source2_player['plyr']}")
    print(f"  Projections: {match.source1_player['proj']} vs {match.source2_player['proj']}")
```

### Enhanced Projection Combination

```python
from nflprojections.combine import ProjectionCombiner
import pandas as pd

# Sample projection DataFrames
source1_df = pd.DataFrame([
    {"plyr": "Josh Allen", "pos": "QB", "team": "BUF", "proj": 25.4},
    {"plyr": "Jonathan Taylor", "pos": "RB", "team": "IND", "proj": 18.2},
])

source2_df = pd.DataFrame([
    {"plyr": "J. Allen", "pos": "QB", "team": "Buffalo", "proj": 24.1}, 
    {"plyr": "Jon Taylor", "pos": "RB", "team": "Indianapolis", "proj": 17.9},
])

# Traditional exact matching (may miss matches due to name variations)
exact_combiner = ProjectionCombiner(use_fuzzy_matching=False)
exact_result = exact_combiner.combine_projections([source1_df, source2_df])

# Enhanced fuzzy matching (handles name variations)
fuzzy_combiner = ProjectionCombiner(
    use_fuzzy_matching=True,
    matcher_config={
        'name_threshold': 0.6,
        'team_threshold': 0.4, 
        'overall_threshold': 0.5
    }
)
fuzzy_result = fuzzy_combiner.combine_projections([source1_df, source2_df])

print(f"Exact matching found {len(exact_result)} total entries")
print(f"Fuzzy matching found {len(fuzzy_result)} total entries")
```

### Custom Merge Strategies

```python
# Get best matches
matches = matcher.get_best_matches(source1, source2)

# Different merge strategies
source1_preferred = matcher.create_merged_data(matches, 'prefer_source1')
source2_preferred = matcher.create_merged_data(matches, 'prefer_source2')
combined_data = matcher.create_merged_data(matches, 'combine')
```

## Similarity Calculation

The PlayerMatcher uses a weighted approach to calculate overall similarity:

- **Player name**: 60% weight (most important)
- **Position**: 20% weight  
- **Team**: 20% weight

Field-specific similarities are calculated using `difflib.SequenceMatcher.ratio()` after normalizing strings to lowercase and removing extra whitespace.

For team matching, a minimum threshold of 0.4 is enforced regardless of the configured `team_threshold` to handle common abbreviation variations (e.g., "BUF" vs "Buffalo").

## Performance Considerations

- Time complexity is O(n*m) where n and m are the sizes of the two data sources
- For large datasets, consider preprocessing to reduce the number of comparisons
- The fuzzy matching adds computational overhead but significantly improves match accuracy

## Backward Compatibility

The enhanced `ProjectionCombiner` is fully backward compatible. Existing code will continue to work unchanged, and fuzzy matching is only enabled when explicitly requested via `use_fuzzy_matching=True`.