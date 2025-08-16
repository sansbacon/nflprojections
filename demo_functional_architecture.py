#!/usr/bin/env python3
# demo_functional_architecture.py
# -*- coding: utf-8 -*-
# Copyright (C) 2025 Eric Truett
# Licensed under the MIT License

"""
Demonstration of the new functional architecture for NFL projections
"""

import pandas as pd
from nflprojections import (
    # Functional components
    NFLComFetcher, NFLComParser, ProjectionStandardizer,
    ProjectionCombiner, CombinationMethod,
    
    # Refactored implementation 
    NFLComProjectionsRefactored,
    
    # Original implementation for comparison
    NFLComProjections
)


def demo_individual_components():
    """Demonstrate using individual functional components"""
    print("=== Demonstrating Individual Functional Components ===")
    
    # Step 1: Create a fetcher
    print("\n1. Creating NFL.com fetcher...")
    fetcher = NFLComFetcher(position="1")  # QB only
    print(f"   Fetcher: {fetcher.source_name}")
    print(f"   Connection valid: {fetcher.validate_connection()}")
    
    # Step 2: Create a parser
    print("\n2. Creating NFL.com parser...")
    parser = NFLComParser()
    print(f"   Parser: {parser.source_name}")
    
    # Step 3: Create a standardizer
    print("\n3. Creating projection standardizer...")
    column_mapping = {
        'player': 'plyr',
        'position': 'pos',
        'team': 'team', 
        'fantasy_points': 'proj',
        'season': 'season',
        'week': 'week'
    }
    standardizer = ProjectionStandardizer(column_mapping, season=2025, week=1, use_names=False)
    print(f"   Standardizer configured with {len(column_mapping)} column mappings")
    
    # Step 4: Demonstrate pipeline (with mock data since we can't guarantee NFL.com access)
    print("\n4. Demonstrating data pipeline with mock data...")
    mock_data = [
        {'player': 'Josh Allen', 'position': 'QB', 'team': 'BUF', 'fantasy_points': 24.5},
        {'player': 'Patrick Mahomes', 'position': 'QB', 'team': 'KC', 'fantasy_points': 23.2},
        {'player': 'Lamar Jackson', 'position': 'QB', 'team': 'BAL', 'fantasy_points': 22.8}
    ]
    mock_df = pd.DataFrame(mock_data)
    print(f"   Mock data shape: {mock_df.shape}")
    
    # Standardize the mock data
    standardized_df = standardizer.standardize(mock_df)
    print(f"   Standardized columns: {list(standardized_df.columns)}")
    print(f"   Sample row: {standardized_df.iloc[0].to_dict()}")


def demo_refactored_implementation():
    """Demonstrate the refactored implementation"""
    print("\n\n=== Demonstrating Refactored Implementation ===")
    
    # Create refactored NFL.com projections
    nfl_refactored = NFLComProjectionsRefactored(season=2025, week=1, position="1", use_names=False)
    
    # Show pipeline info
    pipeline_info = nfl_refactored.get_pipeline_info()
    print("\nPipeline Information:")
    for key, value in pipeline_info.items():
        print(f"   {key}: {value}")
    
    # Validate pipeline components
    validation_results = nfl_refactored.validate_data_pipeline()
    print(f"\nPipeline Validation Results:")
    for component, is_valid in validation_results.items():
        status = "✓" if is_valid else "✗"
        print(f"   {status} {component}: {'Valid' if is_valid else 'Invalid'}")


def demo_projection_combiner():
    """Demonstrate the projection combiner"""
    print("\n\n=== Demonstrating Projection Combiner ===")
    
    # Create sample projections from different sources
    source1_projections = pd.DataFrame([
        {'plyr': 'Josh Allen', 'proj': 24.5},
        {'plyr': 'Patrick Mahomes', 'proj': 23.2},
        {'plyr': 'Lamar Jackson', 'proj': 22.8}
    ])
    
    source2_projections = pd.DataFrame([
        {'plyr': 'Josh Allen', 'proj': 25.1},
        {'plyr': 'Patrick Mahomes', 'proj': 22.8},
        {'plyr': 'Lamar Jackson', 'proj': 23.5}
    ])
    
    source3_projections = pd.DataFrame([
        {'plyr': 'Josh Allen', 'proj': 24.0},
        {'plyr': 'Patrick Mahomes', 'proj': 23.8},
        {'plyr': 'Lamar Jackson', 'proj': 22.2}
    ])
    
    print("Sample projections from 3 sources:")
    print("   Source 1:", source1_projections['proj'].tolist())
    print("   Source 2:", source2_projections['proj'].tolist()) 
    print("   Source 3:", source3_projections['proj'].tolist())
    
    # Test different combination methods
    combiner = ProjectionCombiner()
    projections = [source1_projections, source2_projections, source3_projections]
    
    # Simple average
    avg_result = combiner.combine_projections(projections, method=CombinationMethod.AVERAGE)
    print(f"\nSimple Average Results:")
    for _, row in avg_result.iterrows():
        print(f"   {row['plyr']}: {row['combined_proj']:.2f}")
    
    # Weighted average (give more weight to source 1)
    weights = {'source_0': 0.5, 'source_1': 0.3, 'source_2': 0.2}
    weighted_result = combiner.combine_projections(
        projections, 
        method=CombinationMethod.WEIGHTED_AVERAGE,
        weights=weights
    )
    print(f"\nWeighted Average Results (50%/30%/20%):")
    for _, row in weighted_result.iterrows():
        print(f"   {row['plyr']}: {row['combined_proj']:.2f}")
    
    # Median
    median_result = combiner.combine_projections(projections, method=CombinationMethod.MEDIAN)
    print(f"\nMedian Results:")
    for _, row in median_result.iterrows():
        print(f"   {row['plyr']}: {row['combined_proj']:.2f}")
    
    # Drop high/low
    drop_result = combiner.combine_projections(projections, method=CombinationMethod.DROP_HIGH_LOW)
    print(f"\nDrop High/Low Results:")
    for _, row in drop_result.iterrows():
        print(f"   {row['plyr']}: {row['combined_proj']:.2f}")


def demo_architecture_benefits():
    """Demonstrate the benefits of the functional architecture"""
    print("\n\n=== Architecture Benefits ===")
    
    print("\n1. Separation of Concerns:")
    print("   • Fetching: Handles data source connections and retrieval")
    print("   • Parsing: Handles data structure interpretation") 
    print("   • Standardizing: Handles format normalization")
    print("   • Combining: Handles projection aggregation algorithms")
    
    print("\n2. Extensibility:")
    print("   • Easy to add new data sources (just implement Fetcher + Parser)")
    print("   • Easy to add new combination algorithms")
    print("   • Easy to customize standardization rules")
    
    print("\n3. Testability:")
    print("   • Each component can be tested independently")
    print("   • Mock components can be easily substituted")
    print("   • Pipeline validation at each step")
    
    print("\n4. Reusability:")
    print("   • Fetchers can be reused across different parsers")
    print("   • Standardizers can be reused across different sources")
    print("   • Combiners can work with any standardized projection data")
    
    print("\n5. Maintainability:")
    print("   • Changes to one component don't affect others")
    print("   • Clear interfaces make it easy to understand relationships")
    print("   • Configuration is centralized and explicit")


if __name__ == "__main__":
    print("NFL Projections - Functional Architecture Demo")
    print("=" * 50)
    
    try:
        demo_individual_components()
        demo_refactored_implementation()
        demo_projection_combiner()
        demo_architecture_benefits()
        
        print("\n" + "=" * 50)
        print("Demo completed successfully!")
        print("The functional architecture provides clear separation of concerns")
        print("and makes the system more maintainable and extensible.")
        
    except Exception as e:
        print(f"\nDemo encountered an error: {e}")
        print("This might be expected if external dependencies are not available.")