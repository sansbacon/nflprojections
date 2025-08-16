# nflprojections
python library for fetching and aggregating NFL projections

## Installation

```bash
pip install -e .
```

## Usage

### NFL.com Projections

The `nflcom` module provides parsing of NFL.com fantasy football projections:

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

The returned DataFrame uses standardized column names:
- `plyr` - Player name
- `pos` - Position
- `team` - Team abbreviation
- `proj` - Fantasy points projection
- `season` - Season year
- `week` - Week number
