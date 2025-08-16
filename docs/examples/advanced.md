# Advanced Usage Examples

This page demonstrates advanced patterns and custom implementations.

## Custom Pipeline Components

### Custom Fetcher Implementation

```python
from nflprojections.fetch.base_fetcher import DataSourceFetcher
import requests
import json

class ESPNAPIFetcher(DataSourceFetcher):
    """Custom fetcher for ESPN API"""
    
    def __init__(self, api_key=None, **kwargs):
        super().__init__("espn_api")
        self.api_key = api_key
        self.base_url = "https://api.espn.com/v1/sports/football/nfl"
    
    def fetch_raw_data(self, season=None, week=None, **params):
        """Fetch data from ESPN API"""
        url = f"{self.base_url}/projections"
        
        headers = {}
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        
        params = {
            'season': season,
            'week': week,
            **params
        }
        
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        return response.text
    
    def validate_connection(self):
        """Test API connection"""
        try:
            test_url = f"{self.base_url}/status"
            response = requests.head(test_url, timeout=10)
            return response.status_code == 200
        except:
            return False
```

### Custom Parser Implementation

```python
from nflprojections.parse.base_parser import DataSourceParser
import json
import pandas as pd

class ESPNAPIParser(DataSourceParser):
    """Parser for ESPN API responses"""
    
    def __init__(self):
        super().__init__("espn_api")
    
    def parse_raw_data(self, raw_data):
        """Parse ESPN API JSON response"""
        try:
            data = json.loads(raw_data)
            players = data.get('athletes', [])
            
            parsed_players = []
            for player in players:
                # Extract player info
                player_info = {
                    'player_name': player.get('fullName'),
                    'position': player.get('position', {}).get('abbreviation'),
                    'team': player.get('team', {}).get('abbreviation'),
                    'projected_points': player.get('projectedPoints', 0),
                    'player_id': player.get('id'),
                    'active': player.get('active', True)
                }
                
                # Add individual stat projections if available
                stats = player.get('projectedStats', {})
                for stat_name, value in stats.items():
                    player_info[f'proj_{stat_name}'] = value
                
                parsed_players.append(player_info)
            
            return pd.DataFrame(parsed_players)
            
        except (json.JSONDecodeError, KeyError) as e:
            raise ValueError(f"Failed to parse ESPN API response: {e}")
    
    def validate_parsed_data(self, df):
        """Validate parsed DataFrame structure"""
        required_columns = ['player_name', 'position', 'projected_points']
        return all(col in df.columns for col in required_columns) and not df.empty
```

### Custom Standardizer

```python
from nflprojections.standardize.base_standardizer import DataStandardizer
import re

class ESPNStandardizer(DataStandardizer):
    """Standardizer for ESPN data"""
    
    def __init__(self, **kwargs):
        super().__init__("espn")
        self.season = kwargs.get('season')
        self.week = kwargs.get('week')
        
        # ESPN-specific column mapping
        self.column_mapping = {
            'player_name': 'plyr',
            'position': 'pos',
            'team': 'team',
            'projected_points': 'proj'
        }
        
        # ESPN-specific team mappings
        self.team_mapping = {
            'WSH': 'WAS',  # ESPN uses WSH, we standardize to WAS
            'LV': 'LAS',   # ESPN uses LV, we standardize to LAS
        }
    
    def standardize(self, data):
        """Standardize ESPN data format"""
        if isinstance(data, pd.DataFrame):
            df = data.copy()
            
            # Apply column mapping
            df = df.rename(columns=self.column_mapping)
            
            # Standardize team names
            if 'team' in df.columns:
                df['team'] = df['team'].map(self.team_mapping).fillna(df['team'])
            
            # Clean player names
            if 'plyr' in df.columns:
                df['plyr'] = df['plyr'].apply(self._clean_player_name)
            
            # Add season/week
            df['season'] = self.season
            df['week'] = self.week
            
            # Filter active players only
            if 'active' in df.columns:
                df = df[df['active'] == True]
            
            # Convert to list of dicts
            return df[['plyr', 'pos', 'team', 'proj', 'season', 'week']].to_dict('records')
        
        return data
    
    def _clean_player_name(self, name):
        """Clean and standardize player names"""
        if not name:
            return name
            
        # Remove Jr., Sr., etc.
        name = re.sub(r'\s+(Jr\.?|Sr\.?|III?|IV)$', '', name, flags=re.IGNORECASE)
        
        # Handle apostrophes
        name = re.sub(r"[''`]", "'", name)
        
        # Title case
        name = name.title()
        
        return name.strip()
```

## Building Complete Custom Pipeline

```python
from nflprojections import ProjectionSource

# Create custom pipeline with ESPN components
espn_pipeline = ProjectionSource(
    fetcher=ESPNAPIFetcher(api_key="your-api-key"),
    parser=ESPNAPIParser(),
    standardizer=ESPNStandardizer(season=2025, week=1),
    season=2025,
    week=1
)

# Validate and use
validation = espn_pipeline.validate_data_pipeline()
if all(validation.values()):
    projections = espn_pipeline.fetch_projections()
    print(f"Retrieved {len(projections)} ESPN projections")
else:
    print("Pipeline validation failed:", validation)
```

## Multi-Source Aggregation

### Sophisticated Projection Combining

```python
from nflprojections.combine import ProjectionCombiner, CombinationMethod
from nflprojections import NFLComProjections
import numpy as np

class AdvancedProjectionCombiner:
    """Advanced projection combination with confidence scoring"""
    
    def __init__(self):
        self.base_combiner = ProjectionCombiner()
        self.source_reliability = {
            'nfl': {'weight': 0.35, 'variance': 0.8},
            'espn': {'weight': 0.30, 'variance': 1.0},
            'fp': {'weight': 0.35, 'variance': 0.6}
        }
    
    def combine_with_confidence(self, source_projections, position_adjustments=None):
        """Combine projections with confidence intervals"""
        
        position_adjustments = position_adjustments or {
            'QB': {'reliability_boost': 1.1, 'variance_reduction': 0.9},
            'RB': {'reliability_boost': 0.9, 'variance_reduction': 1.1},
            'WR': {'reliability_boost': 1.0, 'variance_reduction': 1.0},
            'TE': {'reliability_boost': 0.95, 'variance_reduction': 1.05}
        }
        
        # Get base combined projections
        combined = self.base_combiner.combine(
            list(source_projections.values()),
            method=CombinationMethod.WEIGHTED_AVERAGE,
            weights=[self.source_reliability[src]['weight'] for src in source_projections.keys()]
        )
        
        # Add confidence metrics
        enhanced_projections = []
        
        for player_proj in combined:
            player_name = player_proj['plyr']
            position = player_proj.get('pos', 'WR')  # Default to WR
            
            # Collect all projections for this player
            player_values = []
            source_weights = []
            
            for source_name, projections in source_projections.items():
                for proj in projections:
                    if proj['plyr'] == player_name:
                        # Apply position adjustments
                        pos_adj = position_adjustments.get(position, {})
                        reliability = (self.source_reliability[source_name]['weight'] * 
                                     pos_adj.get('reliability_boost', 1.0))
                        
                        player_values.append(proj['proj'])
                        source_weights.append(reliability)
            
            if len(player_values) >= 2:
                # Calculate confidence metrics
                weighted_mean = np.average(player_values, weights=source_weights)
                variance = np.var(player_values)
                
                # Adjust variance by position
                pos_adj = position_adjustments.get(position, {})
                adjusted_variance = variance * pos_adj.get('variance_reduction', 1.0)
                
                # Confidence based on agreement and source count
                agreement_score = 1.0 / (1.0 + adjusted_variance)
                source_score = min(len(player_values) / 3.0, 1.0)  # Max at 3 sources
                confidence = (agreement_score + source_score) / 2.0
                
                # Calculate confidence interval
                std_dev = np.sqrt(adjusted_variance)
                margin = 1.96 * std_dev  # 95% confidence interval
                
                enhanced_proj = {
                    **player_proj,
                    'proj': weighted_mean,
                    'confidence': confidence,
                    'proj_low': weighted_mean - margin,
                    'proj_high': weighted_mean + margin,
                    'variance': adjusted_variance,
                    'source_count': len(player_values)
                }
                
                enhanced_projections.append(enhanced_proj)
            else:
                # Single source - lower confidence
                enhanced_proj = {
                    **player_proj,
                    'confidence': 0.5,
                    'source_count': len(player_values)
                }
                enhanced_projections.append(enhanced_proj)
        
        return enhanced_projections

# Usage example
def get_multi_source_projections(season, week):
    """Get projections from multiple sources"""
    
    # NFL.com projections
    nfl_source = NFLComProjections(season=season, week=week)
    nfl_projections = nfl_source.fetch_projections()
    
    # ESPN projections (custom pipeline)
    espn_pipeline = ProjectionSource(
        fetcher=ESPNAPIFetcher(),
        parser=ESPNAPIParser(),
        standardizer=ESPNStandardizer(season=season, week=week),
        season=season, week=week
    )
    espn_projections = espn_pipeline.fetch_projections()
    
    # Combine with confidence
    combiner = AdvancedProjectionCombiner()
    combined = combiner.combine_with_confidence({
        'nfl': nfl_projections,
        'espn': espn_projections,
        # Add more sources as needed
    })
    
    return combined

# Get enhanced projections
enhanced_projections = get_multi_source_projections(2025, 1)

# Sort by confidence and projection
top_confident_picks = sorted(
    enhanced_projections, 
    key=lambda x: (x['confidence'] * x['proj']), 
    reverse=True
)

print("Most confident high-projection players:")
for i, proj in enumerate(top_confident_picks[:10], 1):
    print(f"{i:2d}. {proj['plyr']:20} ({proj['pos']}) - "
          f"{proj['proj']:.1f} pts (conf: {proj['confidence']:.2f}, "
          f"sources: {proj['source_count']})")
```

## Custom Scoring Systems

### League-Specific Scoring

```python
from nflprojections.scoring.scoring_formats import ScoringFormat

class SuperflexScoring(ScoringFormat):
    """Custom superflex league scoring"""
    
    def __init__(self):
        super().__init__()
        
        # Enhanced QB scoring
        self.scoring_rules.update({
            'passing_yards': 0.05,      # 1 pt per 20 yards (vs standard 25)
            'passing_tds': 6,           # 6 pts (vs standard 4)
            'passing_300_bonus': 3,     # Bonus for 300+ yards
            'passing_400_bonus': 6,     # Bonus for 400+ yards
            
            # Reception bonuses
            'receptions': 1,            # Full PPR
            'reception_bonus_10': 5,    # 10+ reception bonus
            
            # Yardage bonuses
            'rushing_100_bonus': 5,     # 100+ rushing yards
            'receiving_100_bonus': 5,   # 100+ receiving yards
        })
    
    def calculate_points(self, stats):
        """Calculate points with bonuses"""
        points = 0
        
        # Base scoring
        for stat, value in stats.items():
            if stat in self.scoring_rules:
                points += value * self.scoring_rules[stat]
        
        # Apply bonuses
        passing_yards = stats.get('passing_yards', 0)
        if passing_yards >= 400:
            points += self.scoring_rules['passing_400_bonus']
        elif passing_yards >= 300:
            points += self.scoring_rules['passing_300_bonus']
        
        receptions = stats.get('receptions', 0)
        if receptions >= 10:
            points += self.scoring_rules['reception_bonus_10']
        
        rushing_yards = stats.get('rushing_yards', 0)
        if rushing_yards >= 100:
            points += self.scoring_rules['rushing_100_bonus']
        
        receiving_yards = stats.get('receiving_yards', 0)
        if receiving_yards >= 100:
            points += self.scoring_rules['receiving_100_bonus']
        
        return points

# Usage with projection conversion
def convert_projections_to_custom_scoring(projections, scoring_system):
    """Convert standard projections to custom scoring"""
    
    converted = []
    for proj in projections:
        # This would need actual stat projections, not just fantasy points
        # For demonstration, we'll adjust the points by position
        
        position_multipliers = {
            'QB': 1.25,  # QBs get boost in superflex
            'RB': 1.0,
            'WR': 1.0, 
            'TE': 1.05   # Slight TE premium
        }
        
        multiplier = position_multipliers.get(proj['pos'], 1.0)
        adjusted_proj = proj.copy()
        adjusted_proj['proj'] = proj['proj'] * multiplier
        adjusted_proj['scoring_system'] = 'superflex'
        
        converted.append(adjusted_proj)
    
    return converted
```

## Real-Time Data Pipeline

### Automated Updates

```python
import schedule
import time
from datetime import datetime
import logging

class ProjectionUpdater:
    """Automated projection updates"""
    
    def __init__(self, output_file='current_projections.json'):
        self.output_file = output_file
        self.last_update = None
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def update_projections(self, season, week):
        """Update projections from all sources"""
        self.logger.info(f"Starting projection update for {season} Week {week}")
        
        try:
            # Get projections from multiple sources
            projections = get_multi_source_projections(season, week)
            
            # Add metadata
            update_info = {
                'last_updated': datetime.now().isoformat(),
                'season': season,
                'week': week,
                'projection_count': len(projections),
                'projections': projections
            }
            
            # Save to file
            with open(self.output_file, 'w') as f:
                json.dump(update_info, f, indent=2)
            
            self.last_update = datetime.now()
            self.logger.info(f"Updated {len(projections)} projections")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update projections: {e}")
            return False
    
    def start_scheduler(self, season, week):
        """Start automated updates"""
        # Update every 4 hours during the week
        schedule.every(4).hours.do(self.update_projections, season, week)
        
        # More frequent updates on game days (every hour)
        schedule.every().sunday.at("08:00").do(
            lambda: schedule.every(1).hours.until("23:00").do(
                self.update_projections, season, week
            )
        )
        
        # Initial update
        self.update_projections(season, week)
        
        self.logger.info("Started projection update scheduler")
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

# Usage
updater = ProjectionUpdater('week1_projections.json')
# updater.start_scheduler(2025, 1)  # Uncomment to run
```

## Integration with External Systems

### Database Integration

```python
import sqlite3
import pandas as pd

class ProjectionDatabase:
    """SQLite database for projection storage"""
    
    def __init__(self, db_path='projections.db'):
        self.db_path = db_path
        self.setup_database()
    
    def setup_database(self):
        """Create database tables"""
        conn = sqlite3.connect(self.db_path)
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS projections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_name TEXT NOT NULL,
                position TEXT NOT NULL,
                team TEXT NOT NULL,
                projection REAL NOT NULL,
                season INTEGER NOT NULL,
                week INTEGER NOT NULL,
                source TEXT NOT NULL,
                confidence REAL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(player_name, position, season, week, source)
            )
        ''')
        
        conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_player_season_week 
            ON projections(player_name, season, week)
        ''')
        
        conn.commit()
        conn.close()
    
    def store_projections(self, projections, source='unknown'):
        """Store projections in database"""
        conn = sqlite3.connect(self.db_path)
        
        for proj in projections:
            conn.execute('''
                INSERT OR REPLACE INTO projections 
                (player_name, position, team, projection, season, week, source, confidence)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                proj['plyr'],
                proj['pos'], 
                proj['team'],
                proj['proj'],
                proj['season'],
                proj['week'],
                source,
                proj.get('confidence', 0.5)
            ))
        
        conn.commit()
        conn.close()
        
        print(f"Stored {len(projections)} projections from {source}")
    
    def get_projections(self, season, week, position=None):
        """Retrieve projections from database"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT player_name, position, team, 
                   AVG(projection) as avg_proj,
                   AVG(confidence) as avg_confidence,
                   COUNT(*) as source_count
            FROM projections 
            WHERE season = ? AND week = ?
        '''
        params = [season, week]
        
        if position:
            query += ' AND position = ?'
            params.append(position)
        
        query += '''
            GROUP BY player_name, position, team
            ORDER BY avg_proj DESC
        '''
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        return df.to_dict('records')

# Usage
db = ProjectionDatabase()

# Store projections
nfl = NFLComProjections(season=2025, week=1)
projections = nfl.fetch_projections()
db.store_projections(projections, source='nfl')

# Retrieve and analyze
stored_projections = db.get_projections(2025, 1, position='QB')
print(f"Retrieved {len(stored_projections)} QB projections from database")
```