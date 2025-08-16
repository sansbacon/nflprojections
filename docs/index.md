# NFLProjections

A Python library for fetching and aggregating NFL projections with a functional architecture designed for extensibility and maintainability.

## Overview

NFLProjections provides a clean, modular approach to collecting NFL fantasy projections from various sources and combining them using different algorithms. The library is built with a functional architecture that separates concerns across five main areas:

1. **Data Source Fetch** - Retrieving data from different sources (web, files, APIs)
2. **Data Source Parse** - Converting raw data to structured DataFrames  
3. **Standardization** - Normalizing data formats across sources
4. **Scoring** - Applying fantasy scoring rules to statistical data
5. **Combining** - Aggregating projections using various algorithms

## Key Features

- **Modular Architecture**: Each component has a single responsibility
- **Extensible**: Easy to add new data sources and algorithms
- **Testable**: Components can be tested independently
- **Reusable**: Mix and match components as needed
- **Maintainable**: Changes isolated to specific components

## Package Organization

The package is organized into logical submodules:

- **`fetch/`** - Data fetching components
- **`parse/`** - Data parsing components  
- **`standardize/`** - Data standardization
- **`scoring/`** - Scoring systems
- **`combine/`** - Projection combination
- **`sources/`** - Complete projection sources

## Quick Example

```python
from nflprojections import NFLComProjectionsRefactored

# Create refactored NFL.com projections
nfl = NFLComProjectionsRefactored(season=2025, week=1)
projections = nfl.fetch_projections()

# Get pipeline information
pipeline_info = nfl.get_pipeline_info()
print("Pipeline:", pipeline_info)

# Validate pipeline
validation = nfl.validate_data_pipeline()
print("Validation:", validation)
```

## Installation

Get started quickly with pip:

```bash
pip install -e .
```

## Next Steps

- [Installation Guide](installation.md) - Detailed installation instructions
- [Quick Start](quickstart.md) - Get up and running quickly
- [Architecture Overview](architecture/overview.md) - Learn about the design
- [API Reference](api/sources.md) - Explore the full API