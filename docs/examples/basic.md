# Basic Usage Examples

This page shows common usage patterns for NFLProjections.

## Getting Started

### Simple Projection Fetching

```python
from nflprojections import NFLComProjectionsRefactored

# Get week 1 projections for all positions
nfl = NFLComProjectionsRefactored(season=2025, week=1)
projections = nfl.fetch_projections()

print(f"Retrieved {len(projections)} player projections")

# Print first few projections
for proj in projections[:5]:
    print(f"{proj['plyr']} ({proj['pos']}): {proj['proj']} pts")
```

### Position-Specific Projections

```python
# Get only quarterback projections
qb_nfl = NFLComProjectionsRefactored(
    season=2025, 
    week=1, 
    position="1"  # QB position code
)

qb_projections = qb_nfl.fetch_projections()

# Sort by projection (highest first)
sorted_qbs = sorted(qb_projections, key=lambda x: x['proj'], reverse=True)

print("Top 5 QBs:")
for i, qb in enumerate(sorted_qbs[:5], 1):
    print(f"{i}. {qb['plyr']} ({qb['team']}): {qb['proj']:.1f} pts")
```

### Position Code Reference

```python
positions = {
    "0": "All positions",
    "1": "QB",
    "2": "RB", 
    "3": "WR",
    "4": "TE",
    "5": "K",
    "6": "DEF"
}

# Get RB projections
rb_nfl = NFLComProjectionsRefactored(season=2025, week=1, position="2")
rb_projections = rb_nfl.fetch_projections()
```

## Working with Projection Data

### Filtering and Sorting

```python
# Get all projections
nfl = NFLComProjectionsRefactored(season=2025, week=1)
all_projections = nfl.fetch_projections()

# Filter by position
qbs = [p for p in all_projections if p['pos'] == 'QB']
rbs = [p for p in all_projections if p['pos'] == 'RB']
wrs = [p for p in all_projections if p['pos'] == 'WR']

# Filter by team
chiefs_players = [p for p in all_projections if p['team'] == 'KC']

# Filter by projection threshold
high_projections = [p for p in all_projections if p['proj'] > 15.0]

print(f"QBs: {len(qbs)}, RBs: {len(rbs)}, WRs: {len(wrs)}")
print(f"Chiefs players: {len(chiefs_players)}")
print(f"High projections (>15): {len(high_projections)}")
```

### Data Analysis

```python
import statistics

# Calculate position averages
positions = ['QB', 'RB', 'WR', 'TE']
position_stats = {}

for pos in positions:
    pos_players = [p for p in all_projections if p['pos'] == pos]
    if pos_players:
        projections = [p['proj'] for p in pos_players]
        position_stats[pos] = {
            'count': len(pos_players),
            'avg': statistics.mean(projections),
            'median': statistics.median(projections),
            'max': max(projections),
            'min': min(projections)
        }

# Print position statistics
for pos, stats in position_stats.items():
    print(f"\n{pos} Statistics:")
    print(f"  Players: {stats['count']}")
    print(f"  Average: {stats['avg']:.1f}")
    print(f"  Median: {stats['median']:.1f}")
    print(f"  Range: {stats['min']:.1f} - {stats['max']:.1f}")
```

### Export to Different Formats

```python
import json
import csv

# Export to JSON
with open('projections.json', 'w') as f:
    json.dump(all_projections, f, indent=2)

# Export to CSV
with open('projections.csv', 'w', newline='') as f:
    if all_projections:
        writer = csv.DictWriter(f, fieldnames=all_projections[0].keys())
        writer.writeheader()
        writer.writerows(all_projections)

print("Exported projections to JSON and CSV files")
```

## Error Handling

### Basic Error Handling

```python
from nflprojections import NFLComProjectionsRefactored

try:
    nfl = NFLComProjectionsRefactored(season=2025, week=1)
    projections = nfl.fetch_projections()
    print(f"Successfully retrieved {len(projections)} projections")
    
except ConnectionError as e:
    print(f"Network error: {e}")
    print("Check your internet connection")
    
except ValueError as e:
    print(f"Invalid parameters: {e}")
    print("Check season/week values")
    
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Pipeline Validation

```python
# Validate pipeline before fetching
nfl = NFLComProjectionsRefactored(season=2025, week=1)

# Check pipeline components
validation = nfl.validate_data_pipeline()
print("Pipeline validation results:")

all_valid = True
for component, is_valid in validation.items():
    status = "✓" if is_valid else "✗"
    print(f"  {status} {component}")
    if not is_valid:
        all_valid = False

if all_valid:
    projections = nfl.fetch_projections()
    print(f"Successfully retrieved {len(projections)} projections")
else:
    print("Pipeline validation failed - cannot fetch projections")
```

### Debugging with Pipeline Info

```python
# Get detailed pipeline information
nfl = NFLComProjectionsRefactored(season=2025, week=1)
info = nfl.get_pipeline_info()

print("Pipeline Configuration:")
for key, value in info.items():
    print(f"  {key}: {value}")

# This helps debug configuration issues
```

## Performance Tips

### Caching Results

```python
import pickle
import os
from datetime import datetime, timedelta

def get_cached_projections(season, week, max_age_hours=6):
    """Get projections with caching"""
    
    cache_file = f"projections_{season}_week_{week}.pkl"
    
    # Check if cache exists and is recent
    if os.path.exists(cache_file):
        cache_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(cache_file))
        if cache_age < timedelta(hours=max_age_hours):
            print("Using cached projections")
            with open(cache_file, 'rb') as f:
                return pickle.load(f)
    
    # Fetch fresh data
    print("Fetching fresh projections")
    nfl = NFLComProjectionsRefactored(season=season, week=week)
    projections = nfl.fetch_projections()
    
    # Cache the results
    with open(cache_file, 'wb') as f:
        pickle.dump(projections, f)
    
    return projections

# Usage
projections = get_cached_projections(2025, 1)
```

### Batch Processing

```python
def get_multiple_weeks(season, weeks):
    """Get projections for multiple weeks"""
    
    all_projections = {}
    
    for week in weeks:
        print(f"Fetching week {week}...")
        try:
            nfl = NFLComProjectionsRefactored(season=season, week=week)
            projections = nfl.fetch_projections()
            all_projections[week] = projections
            print(f"  Retrieved {len(projections)} projections")
        except Exception as e:
            print(f"  Error fetching week {week}: {e}")
            all_projections[week] = []
    
    return all_projections

# Get projections for weeks 1-4
weeks_1_4 = get_multiple_weeks(2025, [1, 2, 3, 4])
```

## Integration Examples

### With Pandas

```python
import pandas as pd

# Convert to DataFrame
nfl = NFLComProjectionsRefactored(season=2025, week=1)
projections = nfl.fetch_projections()

df = pd.DataFrame(projections)
print("\nDataFrame Info:")
print(df.info())

print("\nTop projections by position:")
for pos in ['QB', 'RB', 'WR', 'TE']:
    pos_df = df[df['pos'] == pos].nlargest(3, 'proj')
    print(f"\n{pos}:")
    print(pos_df[['plyr', 'team', 'proj']].to_string(index=False))
```

### With Matplotlib

```python
import matplotlib.pyplot as plt

# Plot projection distribution by position
fig, axes = plt.subplots(2, 2, figsize=(12, 10))
positions = ['QB', 'RB', 'WR', 'TE']

for i, pos in enumerate(positions):
    ax = axes[i//2, i%2]
    pos_projections = [p['proj'] for p in all_projections if p['pos'] == pos]
    
    ax.hist(pos_projections, bins=15, alpha=0.7, edgecolor='black')
    ax.set_title(f'{pos} Projection Distribution')
    ax.set_xlabel('Fantasy Points')
    ax.set_ylabel('Count')

plt.tight_layout()
plt.savefig('projection_distributions.png')
plt.show()
```