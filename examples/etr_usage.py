#!/usr/bin/env python3
"""
ETR (Establish The Run) Usage Examples

This script demonstrates how to use the new ETR projection classes
that follow the same patterns as the NFL.com implementation.
"""

from nflprojections import ETRProjections
from nflprojections.fetch import ETRFetcher
from nflprojections.parse import ETRParser
from nflprojections.standardize import ProjectionStandardizer


def example_refactored_implementation():
    """Example using the current implementation with functional architecture"""
    print("=== ETR Current Implementation ===")
    
    # Create configured pipeline
    etr = ETRProjections(
        season=2024,
        week=1,
        position="qb",
        scoring="ppr"
    )
    
    # Get pipeline information
    info = etr.get_pipeline_info()
    print(f"Fetcher: {info['fetcher']}")
    print(f"Parser: {info['parser']}")
    print(f"Season: {info['season']}, Week: {info['week']}")
    print(f"Position: {info['position']}, Scoring: {info['scoring']}")
    
    # Note: Actual fetching would require a working ETR website
    # etr_projections = etr.fetch_projections()
    
    print("✓ Current implementation configured successfully")


def example_functional_components():
    """Example using individual functional components"""
    print("\n=== ETR Individual Functional Components ===")
    
    # Create pipeline components
    fetcher = ETRFetcher(position="rb", scoring="half-ppr", week=2)
    parser = ETRParser()
    standardizer = ProjectionStandardizer({
        'player': 'plyr',
        'position': 'pos',
        'team': 'team',
        'fantasy_points': 'proj',
        'season': 'season',
        'week': 'week'
    }, season=2024, week=2)
    
    print(f"Fetcher source: {fetcher.source_name}")
    print(f"Parser source: {parser.source_name}")
    print(f"URL would be: {fetcher.build_url(season=2024)}")
    
    # Execute pipeline (would work with real data)
    # raw_data = fetcher.fetch_raw_data()
    # parsed_df = parser.parse_raw_data(raw_data)
    # final_df = standardizer.standardize(parsed_df)
    
    print("✓ Individual components configured successfully")


def example_legacy_implementation():
    """Example using the legacy-style implementation"""
    print("\n=== ETR Legacy-Style Implementation ===")
    
    # Create ETR projections (backward compatible)
    etr = ETRProjections(
        season=2024,
        week=3,
        position="wr",
        scoring="standard"
    )
    
    print(f"Season: {etr.season}, Week: {etr.week}")
    print(f"Position: {etr.position}, Scoring: {etr.scoring}")
    print(f"URL would be: {etr._build_url()}")
    
    # Fetch projections (would work with real data)
    # projections = etr.fetch_projections()
    
    print("✓ Legacy implementation configured successfully")


def example_custom_column_mapping():
    """Example with custom column mapping"""
    print("\n=== ETR Custom Column Mapping ===")
    
    # Custom mapping for different ETR data format
    custom_mapping = {
        'player_name': 'plyr',
        'pos': 'pos',
        'team_abbr': 'team',
        'projected_points': 'proj',
        'season': 'season',
        'week': 'week'
    }
    
    etr = ETRProjections(
        season=2024,
        position="te",
        column_mapping=custom_mapping
    )
    
    print(f"Custom column mapping: {etr.standardizer.column_mapping}")
    print("✓ Custom column mapping configured successfully")


def example_different_positions_and_scoring():
    """Example with different positions and scoring formats"""
    print("\n=== ETR Different Positions and Scoring ===")
    
    configurations = [
        {"position": "qb", "scoring": "ppr"},
        {"position": "rb", "scoring": "half-ppr"}, 
        {"position": "wr", "scoring": "standard"},
        {"position": "te", "scoring": "ppr"},
        {"position": "k", "scoring": "standard"},
        {"position": "dst", "scoring": "standard"},
        {"position": "all", "scoring": "ppr"}
    ]
    
    for config in configurations:
        etr = ETRProjections(
            season=2024,
            week=1,
            **config
        )
        print(f"✓ {config['position'].upper()} with {config['scoring']} scoring configured")


if __name__ == "__main__":
    try:
        example_refactored_implementation()
        example_functional_components()
        example_legacy_implementation()
        example_custom_column_mapping()
        example_different_positions_and_scoring()
        
        print("\n🎉 All ETR examples completed successfully!")
        print("\nNote: To fetch actual data, you would need:")
        print("1. A working ETR website URL")
        print("2. Correct HTML structure understanding")
        print("3. Proper error handling for network requests")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise