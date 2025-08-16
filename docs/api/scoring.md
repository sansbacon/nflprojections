# Scoring API Reference

The scoring module applies fantasy scoring rules to statistical data.

## Classes

::: nflprojections.scoring.scoring.Scorer
    options:
      show_root_heading: true
      show_source: false

::: nflprojections.scoring.scoring_formats.ScoringFormat
    options:
      show_root_heading: true
      show_source: false

::: nflprojections.scoring.scoring_formats.StandardScoring
    options:
      show_root_heading: true
      show_source: false

::: nflprojections.scoring.scoring_formats.PPRScoring
    options:
      show_root_heading: true
      show_source: false

## Usage Examples

### Standard Scoring

```python
from nflprojections.scoring.scoring_formats import StandardScoring
from nflprojections.scoring.scoring import Scorer

scoring_format = StandardScoring()
scorer = Scorer(scoring_format)

# QB stats
qb_stats = {
    'pass_yd': 300,
    'pass_td': 2,
    'pass_int': 1,
    'rush_yd': 25,
    'rush_td': 1,
    'fumble_lost': 0
}

points = scorer.calculate_fantasy_points(qb_stats)
print(f"QB Points: {points}")  # Standard scoring
```

### PPR Scoring

```python
from nflprojections.scoring.scoring_formats import PPRScoring
from nflprojections.scoring.scoring import Scorer

ppr_format = PPRScoring()
ppr_scorer = Scorer(ppr_format)

# WR stats
wr_stats = {
    'rec': 8,
    'rec_yd': 120,
    'rec_td': 1,
    'fumble_lost': 0
}

ppr_points = ppr_scorer.calculate_fantasy_points(wr_stats)
print(f"WR Points (PPR): {ppr_points}")
```

### Custom Scoring System

```python
from nflprojections.scoring.scoring_formats import ScoringFormat

class SuperflexScoring(ScoringFormat):
    """Custom scoring with bonuses"""
    
    def __init__(self):
        # Start with standard scoring
        super().__init__()
        
        # Add custom rules
        self.scoring_rules.update({
            # Passing bonuses
            'passing_yards_bonus_300': 3,  # Bonus for 300+ yards
            'passing_yards_bonus_400': 2,  # Additional for 400+
            
            # Rushing bonuses  
            'rushing_yards_bonus_100': 3,  # Bonus for 100+ yards
            
            # Reception bonuses
            'receptions_bonus_10': 2,      # Bonus for 10+ catches
        })
    
    def calculate_points(self, stats):
        # Get base points
        points = super().calculate_points(stats)
        
        # Apply bonuses
        if stats.get('passing_yards', 0) >= 400:
            points += self.scoring_rules['passing_yards_bonus_400']
        elif stats.get('passing_yards', 0) >= 300:
            points += self.scoring_rules['passing_yards_bonus_300']
            
        if stats.get('rushing_yards', 0) >= 100:
            points += self.scoring_rules['rushing_yards_bonus_100']
            
        if stats.get('receptions', 0) >= 10:
            points += self.scoring_rules['receptions_bonus_10']
        
        return points
```

### Scoring Different Positions

```python
from nflprojections.scoring import StandardScoring

scorer = StandardScoring()

# Quarterback
qb_points = scorer.calculate_points({
    'passing_yards': 275,
    'passing_tds': 2,
    'rushing_yards': 40,
    'rushing_tds': 1
})

# Running Back
rb_points = scorer.calculate_points({
    'rushing_yards': 85,
    'rushing_tds': 1,
    'receptions': 4,
    'receiving_yards': 35
})

# Wide Receiver
wr_points = scorer.calculate_points({
    'receptions': 6,
    'receiving_yards': 95,
    'receiving_tds': 1
})

print(f"QB: {qb_points}, RB: {rb_points}, WR: {wr_points}")
```

## Scoring Rules

### Standard Scoring Rules

```python
standard_rules = {
    # Passing
    'passing_yards': 0.04,      # 1 pt per 25 yards (0.04 per yard)
    'passing_tds': 4,           # 4 pts per TD
    'interceptions': -2,        # -2 pts per INT
    
    # Rushing  
    'rushing_yards': 0.1,       # 1 pt per 10 yards
    'rushing_tds': 6,           # 6 pts per TD
    
    # Receiving
    'receiving_yards': 0.1,     # 1 pt per 10 yards  
    'receiving_tds': 6,         # 6 pts per TD
    
    # Negative plays
    'fumbles_lost': -2,         # -2 pts per fumble
    
    # Kicking
    'field_goals': 3,           # 3 pts per FG
    'extra_points': 1,          # 1 pt per XP
    
    # Defense
    'defensive_tds': 6,         # 6 pts per TD
    'interceptions_defense': 2,  # 2 pts per INT
    'fumbles_recovered': 2,     # 2 pts per fumble recovery
    'sacks': 1,                 # 1 pt per sack
}
```

### PPR Scoring Rules

PPR adds reception points to standard scoring:

```python
ppr_addition = {
    'receptions': 1,            # 1 pt per reception
}
```

### Half-PPR Scoring

```python
from nflprojections.scoring.scoring_formats import ScoringFormat

class HalfPPRScoring(ScoringFormat):
    def __init__(self):
        super().__init__()
        self.scoring_rules['receptions'] = 0.5  # 0.5 pts per reception
```

## Position-Specific Considerations

```python
def get_position_stats(position, stats):
    """Get relevant stats for a position"""
    
    if position == 'QB':
        return {k: v for k, v in stats.items() 
                if k.startswith(('passing_', 'rushing_', 'fumbles_'))}
    
    elif position in ['RB', 'WR', 'TE']:
        return {k: v for k, v in stats.items()
                if k.startswith(('rushing_', 'receiving_', 'fumbles_'))}
    
    elif position == 'K':
        return {k: v for k, v in stats.items()
                if k.startswith(('field_', 'extra_'))}
    
    elif position == 'DEF':
        return {k: v for k, v in stats.items()
                if k.startswith(('defensive_', 'sacks', 'interceptions_defense'))}
    
    return stats
```