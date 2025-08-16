# Parse API Reference

The parse module converts raw data into structured DataFrames.

## Base Classes

::: nflprojections.parse.base_parser.DataSourceParser
    options:
      show_root_heading: true
      show_source: false

## Implementations

::: nflprojections.parse.nflcom_parser.NFLComParser
    options:
      show_root_heading: true
      show_source: false

::: nflprojections.parse.etr_parser.ETRParser
    options:
      show_root_heading: true
      show_source: false

::: nflprojections.parse.espn_parser.ESPNParser
    options:
      show_root_heading: true
      show_source: false

::: nflprojections.parse.rotogrinders_parser.RotogrindersJSONParser
    options:
      show_root_heading: true
      show_source: false

## Usage Examples

### Basic Parsing

```python
from nflprojections.parse import NFLComParser
from nflprojections.fetch import NFLComFetcher

# Get raw data
fetcher = NFLComFetcher(position="1")
raw_html = fetcher.fetch_raw_data(season=2025, week=1)

# Parse it
parser = NFLComParser()
df = parser.parse_raw_data(raw_html)

print(f"Parsed {len(df)} rows")
print("Columns:", df.columns.tolist())
```

### ETR Parser

```python
from nflprojections.parse import ETRParser
from nflprojections.fetch import ETRFetcher

# Get ETR raw data
fetcher = ETRFetcher(position="rb")
raw_html = fetcher.fetch_raw_data()

# Parse it
parser = ETRParser()
df = parser.parse_raw_data(raw_html)

print(f"Parsed {len(df)} ETR projections")
```

### ESPN Parser

```python
from nflprojections.parse import ESPNParser
from nflprojections.fetch import ESPNFetcher

# Get ESPN raw data
fetcher = ESPNFetcher()
raw_data = fetcher.fetch_raw_data(season=2025, week=1)

# Parse it
parser = ESPNParser()
df = parser.parse_raw_data(raw_data)

print(f"Parsed {len(df)} ESPN projections")
```

### Rotogrinders Parser

```python
from nflprojections.parse import RotogrindersJSONParser
from nflprojections.fetch import RotogrindersWebFetcher

# Get Rotogrinders raw data
fetcher = RotogrindersWebFetcher(position="QB")
raw_html = fetcher.fetch_raw_data(params={'week': 1})

# Parse it
parser = RotogrindersJSONParser()
df = parser.parse_raw_data(raw_html)

print(f"Parsed {len(df)} Rotogrinders projections")
```

### Custom Parser Implementation

```python
from nflprojections.parse.base_parser import DataSourceParser
import pandas as pd
import json

class JSONAPIParser(DataSourceParser):
    def __init__(self):
        super().__init__("json_api")
    
    def parse_raw_data(self, raw_data):
        """Parse JSON API response"""
        data = json.loads(raw_data)
        players = data.get('players', [])
        
        # Convert to DataFrame
        df = pd.DataFrame(players)
        return df
    
    def validate_parsed_data(self, df):
        """Validate the parsed DataFrame"""
        required_columns = ['player', 'position', 'team']
        return all(col in df.columns for col in required_columns)
```

### HTML Table Parsing

```python
from nflprojections.parse.base_parser import HTMLTableParser

class CustomHTMLParser(HTMLTableParser):
    def __init__(self):
        super().__init__("custom_site")
    
    def parse_raw_data(self, raw_html):
        """Parse HTML table data"""
        soup = self.get_soup(raw_html)
        
        # Find the projections table
        table = soup.find('table', {'class': 'projections-table'})
        
        # Extract data
        rows = []
        for row in table.find_all('tr')[1:]:  # Skip header
            cells = row.find_all('td')
            if len(cells) >= 4:
                rows.append({
                    'player': cells[0].text.strip(),
                    'position': cells[1].text.strip(),
                    'team': cells[2].text.strip(),
                    'points': float(cells[3].text.strip())
                })
        
        return pd.DataFrame(rows)
```