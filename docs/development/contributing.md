# Contributing

Thank you for your interest in contributing to NFLProjections! This guide will help you get started.

## Development Setup

### Prerequisites

- Python 3.7+
- Git
- pip

### Getting Started

1. **Fork and clone the repository**:
   ```bash
   git clone https://github.com/yourusername/nflprojections.git
   cd nflprojections
   ```

2. **Install in development mode**:
   ```bash
   pip install -e .
   ```

3. **Install development dependencies**:
   ```bash
   pip install pytest pytest-cov mkdocs mkdocs-material
   ```

4. **Run the tests**:
   ```bash
   pytest tests/ -v
   ```

5. **Build the documentation**:
   ```bash
   mkdocs serve
   ```

## Code Organization

The project follows a functional architecture with clear separation of concerns:

```
nflprojections/
├── fetch/           # Data fetching components
├── parse/           # Data parsing components
├── standardize/     # Data standardization  
├── scoring/         # Fantasy scoring systems
├── combine/         # Projection combination
├── sources/         # Complete projection sources
└── __init__.py      # Main package exports
```

## Contributing Guidelines

### Code Style

- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Include docstrings for all public methods
- Keep functions focused and small
- Use meaningful variable and function names

### Example of good code style:

```python
from typing import List, Dict, Any
from abc import ABC, abstractmethod

class DataSourceFetcher(ABC):
    """Abstract base class for data source fetchers.
    
    Args:
        source_name: Human-readable name of the data source
        
    Attributes:
        source_name: The name of this data source
    """
    
    def __init__(self, source_name: str) -> None:
        self.source_name = source_name
    
    @abstractmethod
    def fetch_raw_data(self, **params: Any) -> Any:
        """Fetch raw data from the source.
        
        Args:
            **params: Parameters specific to the data source
            
        Returns:
            Raw data from the source
            
        Raises:
            ConnectionError: If unable to connect to data source
        """
        pass
    
    def validate_connection(self) -> bool:
        """Validate connection to the data source.
        
        Returns:
            True if connection is valid, False otherwise
        """
        try:
            # Test connection logic here
            return True
        except Exception:
            return False
```

### Testing

We use pytest for testing. Please write tests for new functionality:

```python
import pytest
from nflprojections.fetch import NFLComFetcher

class TestNFLComFetcher:
    """Test cases for NFLComFetcher"""
    
    def test_init(self):
        """Test fetcher initialization"""
        fetcher = NFLComFetcher(position="1")
        assert fetcher.source_name == "NFL.com"
        assert fetcher.position == "1"
    
    def test_validate_connection(self):
        """Test connection validation"""
        fetcher = NFLComFetcher()
        # This should not raise an exception
        is_valid = fetcher.validate_connection()
        assert isinstance(is_valid, bool)
    
    @pytest.mark.slow
    def test_fetch_raw_data(self):
        """Test data fetching (slow test)"""
        fetcher = NFLComFetcher(position="1")
        raw_data = fetcher.fetch_raw_data(season=2025, week=1)
        assert raw_data is not None
        assert len(raw_data) > 0
```

Run tests with:
```bash
# All tests
pytest tests/ -v

# Fast tests only (skip slow network tests)
pytest tests/ -v -m "not slow"

# With coverage
pytest tests/ -v --cov=nflprojections --cov-report=html
```

### Documentation

- Update docstrings for any modified methods
- Add examples to documentation for new features
- Update the changelog for significant changes

Documentation is built with MkDocs Material:

```bash
# Serve locally for development
mkdocs serve

# Build static site
mkdocs build
```

## Adding New Features

### Adding a New Data Source

To add a new data source, implement both a Fetcher and Parser:

1. **Create the fetcher** in `nflprojections/fetch/`:
   ```python
   from .base_fetcher import DataSourceFetcher
   
   class NewSourceFetcher(DataSourceFetcher):
       def __init__(self, **kwargs):
           super().__init__("NewSource")
           # Initialize source-specific parameters
       
       def fetch_raw_data(self, **params):
           # Implement fetching logic
           pass
       
       def validate_connection(self):
           # Test connection
           pass
   ```

2. **Create the parser** in `nflprojections/parse/`:
   ```python
   from .base_parser import DataSourceParser
   
   class NewSourceParser(DataSourceParser):
       def __init__(self):
           super().__init__("NewSource")
       
       def parse_raw_data(self, raw_data):
           # Implement parsing logic
           pass
       
       def validate_parsed_data(self, df):
           # Validate structure
           pass
   ```

3. **Update package exports** in `__init__.py` files:
   ```python
   from .new_source_fetcher import NewSourceFetcher
   from .new_source_parser import NewSourceParser
   ```

4. **Write tests** for both components:
   ```python
   def test_new_source_fetcher():
       # Test fetcher functionality
       pass
   
   def test_new_source_parser():
       # Test parser functionality  
       pass
   ```

5. **Add documentation** in `docs/api/`:
   - Document the new classes
   - Provide usage examples
   - Update relevant guides

### Adding New Combination Methods

To add a new combination method to `ProjectionCombiner`:

1. **Add the method to the enum** in `projectioncombiner.py`:
   ```python
   class CombinationMethod(Enum):
       # ... existing methods
       NEW_METHOD = "new_method"
   ```

2. **Implement the logic** in the `combine` method:
   ```python
   elif method == CombinationMethod.NEW_METHOD:
       # Implement new combination logic
       result = self._combine_new_method(projections_list, **kwargs)
   ```

3. **Add the private method**:
   ```python
   def _combine_new_method(self, projections_list, **kwargs):
       """Implement new combination algorithm"""
       # Your algorithm here
       pass
   ```

### Adding New Scoring Formats

To add a new scoring format:

1. **Create the scoring class** in `nflprojections/scoring/`:
   ```python
   from .scoring_formats import ScoringFormat
   
   class CustomScoring(ScoringFormat):
       def __init__(self):
           super().__init__()
           # Define scoring rules
           self.scoring_rules.update({
               'custom_stat': 2.0,  # Custom scoring rule
           })
       
       def calculate_points(self, stats):
           # Custom calculation logic if needed
           return super().calculate_points(stats)
   ```

## Pull Request Process

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the guidelines above

3. **Run the test suite**:
   ```bash
   pytest tests/ -v
   ```

4. **Update documentation** if needed:
   ```bash
   mkdocs serve  # Test documentation locally
   ```

5. **Commit your changes** with clear messages:
   ```bash
   git commit -m "Add NewSource data fetcher and parser"
   ```

6. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a pull request** on GitHub with:
   - Clear description of changes
   - Reference to any related issues
   - Screenshots if UI changes
   - Test results

### PR Checklist

- [ ] Code follows project style guidelines
- [ ] Tests pass (`pytest tests/ -v`)
- [ ] New functionality has tests
- [ ] Documentation updated if needed
- [ ] Commit messages are clear and descriptive
- [ ] PR description explains the changes

## Reporting Issues

When reporting bugs or requesting features:

1. **Check existing issues** first to avoid duplicates

2. **Use the issue templates** if available

3. **Provide detailed information**:
   - Python version
   - Package version
   - Steps to reproduce
   - Expected vs actual behavior
   - Error messages/tracebacks
   - Code samples

4. **Label appropriately**:
   - `bug` for bugs
   - `enhancement` for new features
   - `documentation` for doc issues
   - `help wanted` if you need assistance

## Development Tips

### Debugging

Use the pipeline validation features to debug issues:

```python
from nflprojections import NFLComProjectionsRefactored

nfl = NFLComProjectionsRefactored(season=2025, week=1)

# Get detailed pipeline info
info = nfl.get_pipeline_info()
print("Pipeline config:", info)

# Validate each component
validation = nfl.validate_data_pipeline()
for component, is_valid in validation.items():
    if not is_valid:
        print(f"Issue with {component}")
```

### Testing with Real Data

Be mindful when testing with real data sources:

- Use `@pytest.mark.slow` for tests that make network requests
- Consider mocking external services for faster tests
- Cache responses during development to avoid excessive API calls

### Documentation Writing

- Use clear, concise language
- Include code examples for all features
- Update API documentation when changing interfaces
- Test documentation examples to ensure they work

## Community

- **GitHub Discussions**: For general questions and ideas
- **Issues**: For bugs and feature requests  
- **Pull Requests**: For code contributions

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).