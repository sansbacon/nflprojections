# Architecture Overview

NFLProjections uses a functional architecture with clear separation of concerns. This design makes the system modular, testable, and easy to extend.

## Design Principles

### 1. Separation of Concerns
Each component has a single, well-defined responsibility:
- Fetching doesn't affect parsing or standardization
- Changes to one component don't impact others
- Easy to understand what each component does

### 2. Functional Composition
Components can be combined in different ways:
- Mix and match fetchers, parsers, and standardizers
- Compose complete pipelines from individual components
- Reuse components across different data sources

### 3. Interface-Driven Design
Clear interfaces define component interactions:
- Predictable input/output contracts
- Easy to mock for testing
- Simple to swap implementations

## Architecture Components

```mermaid
graph TD
    A[Data Source] --> B[Fetcher]
    B --> C[Parser] 
    C --> D[Standardizer]
    D --> E[Scorer]
    E --> F[Combiner]
    F --> G[Final Projections]
    
    style B fill:#e1f5fe
    style C fill:#f3e5f5
    style D fill:#e8f5e8
    style E fill:#fff3e0
    style F fill:#fce4ec
```

### 1. Data Source Fetch
**Purpose**: Retrieve raw data from different sources

- **Web sources**: NFL.com, ESPN, FantasyPros
- **File sources**: CSV, JSON, Excel files
- **API sources**: REST APIs, GraphQL endpoints

**Key Interface**: `fetch_raw_data(**params) -> RawData`

### 2. Data Source Parse
**Purpose**: Convert raw data to structured format

- **HTML parsers**: BeautifulSoup-based table extraction
- **JSON parsers**: API response processing
- **CSV parsers**: File-based data loading

**Key Interface**: `parse_raw_data(raw_data) -> DataFrame`

### 3. Standardization
**Purpose**: Normalize data formats across sources

- **Column mapping**: Different sources use different field names
- **Data cleaning**: Handle missing values, format inconsistencies
- **Player name standardization**: Consistent player identification

**Key Interface**: `standardize(data) -> StandardizedData`

### 4. Scoring
**Purpose**: Apply fantasy scoring rules

- **Standard scoring**: Traditional fantasy points
- **PPR scoring**: Points per reception
- **Custom scoring**: User-defined rules

**Key Interface**: `calculate_points(stats) -> FantasyPoints`

### 5. Combining
**Purpose**: Aggregate projections from multiple sources

- **Average**: Simple mean across sources
- **Weighted average**: Different weights per source
- **Median**: Robust to outliers
- **Custom algorithms**: User-defined combination logic

**Key Interface**: `combine(projections_list, method) -> CombinedProjections`

## Package Structure

The package is organized into logical submodules for clear separation of concerns:

```
nflprojections/
├── __init__.py           # Main high-level APIs only
├── fetch/                # Data fetching components
│   ├── __init__.py
│   ├── base_fetcher.py   # Abstract fetcher classes
│   └── nflcom_fetcher.py # NFL.com specific fetcher
├── parse/                # Data parsing components
│   ├── __init__.py
│   ├── base_parser.py    # Abstract parser classes
│   └── nflcom_parser.py  # NFL.com specific parser
├── standardize/          # Data standardization
│   ├── __init__.py
│   └── base_standardizer.py # Standardization logic
├── scoring/              # Scoring systems
│   ├── __init__.py
│   ├── scoring.py        # Base scoring functionality
│   └── scoring_formats.py # Specific scoring formats
├── combine/              # Projection combination
│   ├── __init__.py
│   └── projectioncombiner.py # Combination algorithms
└── sources/              # Complete projection sources
    ├── __init__.py
    ├── projectionsource.py    # Abstract base
    ├── nflcom.py              # NFL.com implementation
    └── nflcom_refactored.py   # Refactored NFL.com
```

### Package Installation

The package is pip-installable with proper setup.py:

```bash
pip install -e .              # Development install
pip install nflprojections    # From PyPI (when published)
```

All submodules are included automatically via `find_packages()`, providing:
- ✅ Main high-level APIs available from root package
- ✅ Organized into 6 logical submodules for better code organization
- ✅ Clear separation of concerns (fetch, parse, standardize, score, combine, sources)
- ✅ Pip-installable Python module
- ✅ Explicit submodule imports for better code organization

## Usage Patterns

### Pattern 1: High-Level API
For most users, the high-level APIs provide everything needed:

```python
from nflprojections import NFLComProjectionsRefactored

nfl = NFLComProjectionsRefactored(season=2025, week=1)
projections = nfl.fetch_projections()
```

### Pattern 2: Individual Components
For advanced users who need custom pipelines:

```python
from nflprojections.fetch import NFLComFetcher
from nflprojections.parse import NFLComParser
from nflprojections.standardize import ProjectionStandardizer

# Build custom pipeline
fetcher = NFLComFetcher()
parser = NFLComParser()
standardizer = ProjectionStandardizer(custom_mapping)
```

### Pattern 3: Composed Pipeline
Use the ProjectionSource for flexible composition:

```python
from nflprojections import ProjectionSource
from nflprojections.fetch import CustomFetcher
from nflprojections.parse import CustomParser

source = ProjectionSource(
    fetcher=CustomFetcher(),
    parser=CustomParser(),
    standardizer=standardizer
)
```

## Benefits

### Modularity
- Each component has a single responsibility
- Easy to understand and maintain
- Clear boundaries between concerns

### Extensibility
- Add new data sources by implementing Fetcher + Parser
- Add new combination algorithms to ProjectionCombiner
- Add new standardization rules without changing existing code

### Testability
- Each component can be tested independently
- Mock components can be easily substituted
- Pipeline validation at each step

### Reusability
- Fetchers can be reused across different parsers
- Standardizers can be reused across different sources
- Combiners work with any standardized projection data

## Next Steps

- [Functional Architecture Details](functional.md) - Deep dive into implementation
- [API Reference](../api/sources.md) - Explore the full API
- [Examples](../examples/advanced.md) - See advanced usage patterns