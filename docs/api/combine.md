# Combine API Reference

The combine module aggregates projections from multiple sources using various algorithms.

## Classes

::: nflprojections.combine.projectioncombiner.ProjectionCombiner
    options:
      show_root_heading: true
      show_source: false

::: nflprojections.combine.projectioncombiner.CombinationMethod
    options:
      show_root_heading: true
      show_source: false

## Usage Examples

### Basic Combination

```python
from nflprojections.combine import ProjectionCombiner, CombinationMethod

# Sample projections from different sources
nfl_projections = [
    {'plyr': 'Josh Allen', 'proj': 23.4},
    {'plyr': 'Lamar Jackson', 'proj': 21.8}
]

espn_projections = [
    {'plyr': 'Josh Allen', 'proj': 25.1},
    {'plyr': 'Lamar Jackson', 'proj': 20.5}
]

fp_projections = [
    {'plyr': 'Josh Allen', 'proj': 24.2},
    {'plyr': 'Lamar Jackson', 'proj': 22.1}
]

# Combine using average
combiner = ProjectionCombiner()
combined = combiner.combine(
    [nfl_projections, espn_projections, fp_projections],
    method=CombinationMethod.AVERAGE
)

print("Combined projections:", combined)
```

### Weighted Average

```python
# Give different weights to sources
combined = combiner.combine(
    [nfl_projections, espn_projections, fp_projections],
    method=CombinationMethod.WEIGHTED_AVERAGE,
    weights=[0.4, 0.3, 0.3]  # NFL.com gets 40% weight
)
```

### Median Combination

```python
# Use median (robust to outliers)
combined = combiner.combine(
    [nfl_projections, espn_projections, fp_projections],
    method=CombinationMethod.MEDIAN
)
```

### Custom Combination Algorithm

```python
from nflprojections.combine.projectioncombiner import ProjectionCombiner

class CustomCombiner(ProjectionCombiner):
    def combine_custom(self, projections_list, **kwargs):
        """Custom combination algorithm"""
        combined = {}
        
        # Get all unique players
        all_players = set()
        for projections in projections_list:
            for proj in projections:
                all_players.add(proj['plyr'])
        
        result = []
        for player in all_players:
            # Get projections for this player
            player_projections = []
            for projections in projections_list:
                for proj in projections:
                    if proj['plyr'] == player:
                        player_projections.append(proj['proj'])
            
            if player_projections:
                # Custom algorithm: weighted by recency
                weights = [i+1 for i in range(len(player_projections))]
                weighted_sum = sum(p*w for p, w in zip(player_projections, weights))
                weight_sum = sum(weights)
                
                result.append({
                    'plyr': player,
                    'proj': weighted_sum / weight_sum,
                    'source_count': len(player_projections)
                })
        
        return result

# Use custom combiner
custom_combiner = CustomCombiner()
custom_combined = custom_combiner.combine_custom(
    [nfl_projections, espn_projections, fp_projections]
)
```

## Combination Methods

### Available Methods

```python
class CombinationMethod(Enum):
    AVERAGE = "average"                    # Simple arithmetic mean
    WEIGHTED_AVERAGE = "weighted_average" # Weighted arithmetic mean
    MEDIAN = "median"                     # Median value
    CONSERVATIVE = "conservative"         # Lower bound estimate
    AGGRESSIVE = "aggressive"            # Upper bound estimate
```

### Method Details

#### Average
Simple arithmetic mean of all projections:
```python
combined_projection = sum(projections) / len(projections)
```

#### Weighted Average
Weighted mean with custom weights:
```python
combined_projection = sum(proj * weight for proj, weight in zip(projections, weights)) / sum(weights)
```

#### Median
Middle value (robust to outliers):
```python
combined_projection = median(projections)
```

#### Conservative
Takes lower estimates:
```python
combined_projection = min(projections) * 1.1  # 10% above minimum
```

#### Aggressive  
Takes higher estimates:
```python
combined_projection = max(projections) * 0.9  # 10% below maximum
```

## Advanced Usage

### Position-Specific Combination

```python
def combine_by_position(projections_list, position_weights=None):
    """Combine projections with position-specific weights"""
    
    default_weights = {
        'QB': [0.4, 0.3, 0.3],    # Conservative for QB
        'RB': [0.3, 0.4, 0.3],    # Favor middle source for RB
        'WR': [0.35, 0.35, 0.3],  # Balanced for WR
        'TE': [0.3, 0.3, 0.4],    # Favor last source for TE
    }
    
    combiner = ProjectionCombiner()
    combined_by_pos = {}
    
    # Group by position
    for pos in ['QB', 'RB', 'WR', 'TE']:
        pos_projections = []
        for projections in projections_list:
            pos_proj = [p for p in projections if p.get('pos') == pos]
            pos_projections.append(pos_proj)
        
        weights = (position_weights or {}).get(pos, default_weights.get(pos))
        
        combined = combiner.combine(
            pos_projections,
            method=CombinationMethod.WEIGHTED_AVERAGE,
            weights=weights
        )
        
        combined_by_pos[pos] = combined
    
    return combined_by_pos
```

### Source Reliability Weighting

```python
def combine_with_reliability(projections_list, source_reliability=None):
    """Weight sources by historical accuracy"""
    
    reliability_scores = source_reliability or {
        'nfl': 0.85,      # NFL.com reliability
        'espn': 0.80,     # ESPN reliability  
        'fp': 0.90        # FantasyPros reliability
    }
    
    # Convert reliability to weights
    total_reliability = sum(reliability_scores.values())
    weights = [score/total_reliability for score in reliability_scores.values()]
    
    combiner = ProjectionCombiner()
    return combiner.combine(
        projections_list,
        method=CombinationMethod.WEIGHTED_AVERAGE,
        weights=weights
    )
```

### Confidence Intervals

```python
def combine_with_confidence(projections_list, confidence_level=0.95):
    """Combine with confidence intervals"""
    import numpy as np
    from scipy import stats
    
    combiner = ProjectionCombiner()
    combined = combiner.combine(projections_list, method=CombinationMethod.AVERAGE)
    
    # Add confidence intervals
    for player_proj in combined:
        player_name = player_proj['plyr']
        
        # Get all projections for this player
        all_projections = []
        for projections in projections_list:
            for proj in projections:
                if proj['plyr'] == player_name:
                    all_projections.append(proj['proj'])
        
        if len(all_projections) > 1:
            # Calculate confidence interval
            mean_proj = np.mean(all_projections)
            std_proj = np.std(all_projections)
            n = len(all_projections)
            
            # t-distribution for small samples
            t_val = stats.t.ppf((1 + confidence_level) / 2, n-1)
            margin_error = t_val * (std_proj / np.sqrt(n))
            
            player_proj.update({
                'proj_lower': mean_proj - margin_error,
                'proj_upper': mean_proj + margin_error,
                'confidence': confidence_level,
                'std_dev': std_proj
            })
    
    return combined
```