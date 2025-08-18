### Copilot Instructions for `nflprojections`

#### Repository Summary
The `nflprojections` repository is a Python library for fetching, parsing, standardizing, scoring, and combining NFL player projections from different sources such as NFL.com, ESPN, Establish The Run (ETR), and FantasyPros. It uses a modular and functional architecture to facilitate data processing pipelines for fantasy football projections.

#### High-Level Repository Information
- **Type of Project**: Python library for data processing and aggregation.
- **Languages Used**: Python (primary language).
- **Frameworks/Tools**: BeautifulSoup, Pandas, NumPy, Requests.
- **Target Runtime**: Python 3.7 or higher (validated up to Python 3.12).
- **Repository Size**: Medium-sized with detailed documentation and examples.

#### Build Instructions
1. **Bootstrap**
   - Install dependencies:
     ```bash
     pip install -r requirements.txt
     ```
   - For development:
     ```bash
     pip install -r requirements-dev.txt
     ```

2. **Build**
   - The library does not require explicit build steps but can be installed locally:
     ```bash
     pip install -e .
     ```

3. **Test**
   - Run the tests using `pytest`:
     ```bash
     pytest
     ```

4. **Lint**
   - Linting tools are not explicitly mentioned; use Python linters like `flake8` or `pylint` if required.

5. **Run**
   - The library can be imported and used in Python scripts directly:
     ```python
     from nflprojections import NFLComProjections
     nfl = NFLComProjections(season=2025, week=1)
     projections = nfl.fetch_projections()
     print(projections)
     ```

6. **Documentation**
   - Build and deploy documentation using MkDocs:
     ```bash
     mkdocs build
     ```

#### Project Layout
- **Source Code**:
  - Main modules:
    - `fetch/`: Data fetching components.
    - `parse/`: Data parsing components.
    - `standardize/`: Data standardization components.
    - `scoring/`: Scoring systems.
    - `combine/`: Projection combination algorithms.
    - `sources/`: Integrated projection sources.
  - Entry point: `nflprojections/__init__.py`.

- **Configuration Files**:
  - `requirements.txt`: Core dependencies.
  - `requirements-dev.txt`: Development dependencies.
  - `.github/workflows/docs.yml`: GitHub Actions for building and deploying documentation.
  - `pyproject.toml`: Project metadata and build system configuration.

- **Checks Prior to Commit**:
  - Run tests using `pytest`.
  - Validate dependencies using `validate_requirements.py` (located in the root directory).

#### Validation Steps
- Always install dependencies using `pip install -r requirements.txt` before running tests or scripts.
- Verify imports and functionality using `validate_requirements.py` to ensure all dependencies are correctly installed.
- Use the provided GitHub Actions workflow (`docs.yml`) to ensure documentation builds properly.

#### Key Facts
- **Entry Points**:
  - High-level APIs (`NFLComProjections`, `ETRProjections`, `ESPNProjections`) are imported from the root package.
  - Modular components such as fetchers, parsers, and standardizers are imported from submodules.
- **Documentation**:
  - Comprehensive documentation is available in Markdown files, including architecture overview, API references, and examples.
- **Dependencies**:
  - Core: `requests`, `beautifulsoup4`, `pandas`, `numpy`.
  - Development: `pytest`, `mkdocs`, `mkdocs-material`.

#### Instructions for the Copilot Coding Agent
- Trust the provided instructions for building, testing, and validating changes.
- Use the modular architecture to locate components easily:
  - Fetching logic is in `fetch/`.
  - Parsing logic is in `parse/`.
  - Scoring logic is in `scoring/`.
  - Combination logic is in `combine/`.
- Refer to the documentation in the `docs/` folder for in-depth details about API usage and architecture.
- Perform a search only if the instructions are incomplete or found to be in error.