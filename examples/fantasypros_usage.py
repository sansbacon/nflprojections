#!/usr/bin/env python3
"""
FantasyPros Usage Examples

This script demonstrates how to use the new FantasyPros projection class
that follows the same patterns as the other projection implementations.
"""

from nflprojections import FantasyProsProjections
from nflprojections.fetch import FantasyProsFetcher
from nflprojections.parse import FantasyProsParser
from nflprojections.standardize import ProjectionStandardizer


def example_fantasypros_implementation():
    """Example using the FantasyPros implementation with functional architecture"""
    print("=== FantasyPros Implementation (Functional Architecture) ===")
    
    # Initialize with different positions and scoring
    configurations = [
        {"position": "qb", "scoring": "ppr", "week": "draft"},
        {"position": "rb", "scoring": "ppr", "week": "1"},
        {"position": "wr", "scoring": "half", "week": "8"},
        {"position": "te", "scoring": "standard", "week": "draft"},
    ]
    
    for config in configurations:
        fp = FantasyProsProjections(**config)
        print(f"✓ {config['position'].upper()} with {config['scoring']} scoring, week {config['week']} configured")
        
        # Show pipeline info
        info = fp.get_pipeline_info()
        print(f"  - Fetcher: {info['fetcher']}")
        print(f"  - Parser: {info['parser']}")
        print(f"  - URL would be: {fp.fetcher.build_url()}")
        print()


def example_functional_components():
    """Example using individual functional components"""
    print("=== FantasyPros Functional Components ===")
    
    # Create individual components
    fetcher = FantasyProsFetcher(position="qb", scoring="ppr", week="draft")
    parser = FantasyProsParser(position="qb")
    standardizer = ProjectionStandardizer(
        column_mapping={
            'player': 'plyr',
            'position': 'pos',
            'team': 'team',
            'fantasy_points': 'proj',
            'season': 'season',
            'week': 'week'
        }
    )
    
    print(f"✓ Fetcher configured: {fetcher.source_name}")
    print(f"✓ Parser configured: {parser.source_name}")
    print(f"✓ Standardizer configured")
    print(f"  - URL: {fetcher.build_url()}")
    print()


def example_url_variations():
    """Example showing different URL variations"""
    print("=== FantasyPros URL Variations ===")
    
    test_cases = [
        {"position": "qb", "scoring": "ppr", "week": "draft"},
        {"position": "rb", "scoring": "ppr", "week": "1"},  
        {"position": "wr", "scoring": "half", "week": "8"},
        {"position": "te", "scoring": "standard", "week": "draft"},
        {"position": "k", "scoring": "ppr", "week": "1"},
        {"position": "dst", "scoring": "ppr", "week": "1"},
    ]
    
    for case in test_cases:
        fetcher = FantasyProsFetcher(**case)
        url = fetcher.build_url()
        print(f"{case['position'].upper():3} | {case['scoring']:8} | Week {case['week']:5} | {url}")
    
    print()


def example_custom_column_mapping():
    """Example with custom column mapping"""
    print("=== FantasyPros Custom Column Mapping ===")
    
    # Custom mapping for different FantasyPros data format
    custom_mapping = {
        'player': 'plyr',  # FantasyPros column -> standard column
        'position': 'pos',
        'team': 'team', 
        'fantasy_points': 'proj',
        'att': 'pass_att',
        'cmp': 'pass_cmp',
        'season': 'season',
        'week': 'week'
    }
    
    fp = FantasyProsProjections(
        position="qb",
        scoring="ppr",
        week="draft",
        column_mapping=custom_mapping
    )
    
    print(f"Custom column mapping configured")
    print("✓ Custom column mapping configured successfully")
    print()


def example_validation():
    """Example showing pipeline validation"""
    print("=== FantasyPros Pipeline Validation ===")
    
    fp = FantasyProsProjections(position="qb", scoring="ppr", week="draft")
    
    print("Pipeline components:")
    info = fp.get_pipeline_info()
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    print()
    print("Note: Full validation requires actual HTTP requests to FantasyPros")
    print("✓ Pipeline structure validation complete")


if __name__ == "__main__":
    try:
        example_fantasypros_implementation()
        example_functional_components()
        example_url_variations()
        example_custom_column_mapping()
        example_validation()
        
        print("🎉 All FantasyPros examples completed successfully!")
        
    except Exception as e:
        print(f"❌ Error in FantasyPros examples: {e}")
        import traceback
        traceback.print_exc()