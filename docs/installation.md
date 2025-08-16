# Installation

## Requirements

- Python 3.7+
- pip

## Install from Source

Since this library is currently available from source, install it in development mode:

```bash
git clone https://github.com/sansbacon/nflprojections.git
cd nflprojections
pip install -e .
```

This installs the package in "editable" mode, meaning changes to the source code will be immediately available without reinstalling.

## Verify Installation

You can verify the installation worked by importing the main components:

```python
# Test basic imports
from nflprojections import NFLComProjections, NFLComProjectionsRefactored
from nflprojections import ProjectionCombiner, ProjectionSource

# Test submodule imports
from nflprojections.fetch import NFLComFetcher
from nflprojections.parse import NFLComParser
from nflprojections.scoring import StandardScoring
from nflprojections.standardize import ProjectionStandardizer

print("✓ All imports successful")
```

## Dependencies

The package has minimal external dependencies and uses mostly standard library modules. Key dependencies include:

- **requests** - For HTTP requests to fetch data
- **pandas** - For data manipulation (if available)
- **beautifulsoup4** - For HTML parsing (if available)

## Development Dependencies

If you plan to contribute or modify the code, you may also want to install development dependencies:

```bash
pip install pytest  # For running tests
```

## Troubleshooting

### Import Errors

If you encounter import errors, ensure you're importing from the correct submodules:

```python
# ✓ Correct - main APIs from root
from nflprojections import NFLComProjections

# ✓ Correct - specific components from submodules
from nflprojections.fetch import NFLComFetcher

# ✗ Incorrect - specific components from root
from nflprojections import NFLComFetcher  # This won't work
```

### Network Issues

The library fetches data from external sources. If you encounter network-related errors:

1. Check your internet connection
2. Verify the data source is accessible
3. Check if you're behind a firewall or proxy

### Missing Dependencies

If you get import errors for specific features, you may need to install additional dependencies:

```bash
pip install pandas beautifulsoup4 requests
```