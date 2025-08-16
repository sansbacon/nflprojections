# Standardize API Reference

The standardize module normalizes data formats across different sources.

## Classes

::: nflprojections.standardize.base_standardizer.ProjectionStandardizer
    options:
      show_root_heading: true
      show_source: false

## Usage Examples

### Basic Standardization

```python
from nflprojections.standardize import ProjectionStandardizer

# Define column mapping
column_mapping = {
    'player_name': 'plyr',
    'pos': 'pos',
    'team_abbr': 'team', 
    'projected_points': 'proj',
    'year': 'season',
    'week_num': 'week'
}

# Create standardizer
standardizer = ProjectionStandardizer(
    column_mapping=column_mapping,
    season=2025,
    week=1
)

# Standardize parsed data
standardized_data = standardizer.standardize(parsed_df)
print(f"Standardized {len(standardized_data)} players")
```

### Player Name Standardization

```python
from nflprojections.standardize import ProjectionStandardizer

standardizer = ProjectionStandardizer(column_mapping)

# Standardize individual player names
names = ["Josh Allen", "J. Allen", "Joshua Allen"]
standardized_names = standardizer.standardize_players(names)
print("Standardized names:", standardized_names)

# Use name lookup
lookup = standardizer.get_name_lookup()
print("Name mappings:", lookup)
```

### Team Name Standardization

```python
# Standardize team names/abbreviations
teams = ["Buffalo Bills", "BUF", "buffalo"]
standardized_teams = standardizer.standardize_teams(teams)
print("Standardized teams:", standardized_teams)  # ['BUF', 'BUF', 'BUF']
```

### Position Standardization

```python
# Standardize position names
positions = ["Quarterback", "QB", "qb", "Q"]
standardized_pos = standardizer.standardize_positions(positions)
print("Standardized positions:", standardized_pos)  # ['QB', 'QB', 'QB', 'QB']
```

### Custom Standardizer

```python
from nflprojections.standardize.base_standardizer import DataStandardizer

class CustomStandardizer(DataStandardizer):
    def __init__(self, column_mapping, **kwargs):
        super().__init__(source_name="custom")
        self.column_mapping = column_mapping
        self.season = kwargs.get('season')
        self.week = kwargs.get('week')
    
    def standardize(self, data):
        """Custom standardization logic"""
        if isinstance(data, pd.DataFrame):
            # Apply column mapping
            data = data.rename(columns=self.column_mapping)
            
            # Add season/week if missing
            if 'season' not in data.columns:
                data['season'] = self.season
            if 'week' not in data.columns:
                data['week'] = self.week
            
            # Custom data cleaning
            data['plyr'] = data['plyr'].str.title()
            data['pos'] = data['pos'].str.upper()
            
            return data.to_dict('records')
        
        return data
```

## Standard Output Format

All standardizers output data in this format:

```python
{
    'plyr': 'Josh Allen',     # Standardized player name
    'pos': 'QB',              # Standardized position
    'team': 'BUF',           # Standardized team abbreviation  
    'proj': 23.4,            # Fantasy projection (float)
    'season': 2025,          # Season year (int)
    'week': 1                # Week number (int)
}
```

## Configuration Options

### Column Mapping

Map source columns to standard format:

```python
# ESPN example
espn_mapping = {
    'name': 'plyr',
    'position': 'pos',
    'team': 'team',
    'fantasy_points_ppr': 'proj'
}

# FantasyPros example  
fp_mapping = {
    'player_name': 'plyr',
    'pos': 'pos',
    'tm': 'team',
    'fpts': 'proj'
}
```

### Name Standardization

Control how player names are standardized:

```python
standardizer = ProjectionStandardizer(
    column_mapping=mapping,
    use_names=True,      # Enable name standardization
    name_source="file"   # Use name file for lookups
)
```