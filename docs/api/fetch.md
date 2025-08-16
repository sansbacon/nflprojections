# Fetch API Reference

The fetch module handles data retrieval from various sources.

## Base Classes

::: nflprojections.fetch.base_fetcher.DataSourceFetcher
    options:
      show_root_heading: true
      show_source: false

## Implementations

::: nflprojections.fetch.nflcom_fetcher.NFLComFetcher
    options:
      show_root_heading: true
      show_source: false

## Usage Examples

### Basic Fetching

```python
from nflprojections.fetch import NFLComFetcher

# Create fetcher for quarterbacks
fetcher = NFLComFetcher(position="1")  # QB

# Fetch raw data
raw_data = fetcher.fetch_raw_data(season=2025, week=1)
print(f"Fetched {len(raw_data)} bytes of data")

# Validate connection
is_valid = fetcher.validate_connection()
print(f"Connection valid: {is_valid}")
```

### Custom Fetcher Implementation

```python
from nflprojections.fetch.base_fetcher import DataSourceFetcher

class CustomAPIFetcher(DataSourceFetcher):
    def __init__(self, api_key, **kwargs):
        super().__init__("custom_api")
        self.api_key = api_key
    
    def fetch_raw_data(self, **params):
        # Implement API call
        response = requests.get(
            self.api_url,
            headers={'Authorization': f'Bearer {self.api_key}'},
            params=params
        )
        return response.text
    
    def validate_connection(self):
        try:
            # Test API connection
            response = requests.head(self.api_url)
            return response.status_code == 200
        except:
            return False
```

### Position Codes

NFL.com uses numeric position codes:

```python
positions = {
    "0": "All positions",
    "1": "QB",  # Quarterback
    "2": "RB",  # Running Back
    "3": "WR",  # Wide Receiver
    "4": "TE",  # Tight End
    "5": "K",   # Kicker
    "6": "DEF"  # Defense
}

fetcher = NFLComFetcher(position=positions["2"])  # RB
```