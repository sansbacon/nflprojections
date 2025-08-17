# examples/player_matching_example.py
# -*- coding: utf-8 -*-
# Copyright (C) 2025 Eric Truett
# Licensed under the MIT License

"""
Example demonstrating player matching functionality across projection sources.
This example shows how to use the PlayerMatcher and enhanced ProjectionCombiner
to handle variations in player names and team abbreviations.
"""

import pandas as pd
from nflprojections.matching import PlayerMatcher
from nflprojections.combine import ProjectionCombiner


def demonstrate_basic_matching():
    """Demonstrate basic player matching between two sources"""
    print("=== Basic Player Matching Example ===\n")
    
    # Sample data from two projection sources with name variations
    source1 = [
        {"plyr": "Josh Allen", "pos": "QB", "team": "BUF", "proj": 25.4},
        {"plyr": "Jonathan Taylor", "pos": "RB", "team": "IND", "proj": 18.2},
        {"plyr": "Davante Adams", "pos": "WR", "team": "LV", "proj": 16.8},
        {"plyr": "Travis Kelce", "pos": "TE", "team": "KC", "proj": 14.5},
        {"plyr": "Tyreek Hill", "pos": "WR", "team": "MIA", "proj": 15.9},
    ]
    
    source2 = [
        {"plyr": "J. Allen", "pos": "QB", "team": "Buffalo", "proj": 24.1},
        {"plyr": "Jon Taylor", "pos": "RB", "team": "Indianapolis", "proj": 17.9},
        {"plyr": "D. Adams", "pos": "WR", "team": "Las Vegas", "proj": 16.2},
        {"plyr": "T. Kelce", "pos": "TE", "team": "Kansas City", "proj": 15.1},
        {"plyr": "Patrick Mahomes", "pos": "QB", "team": "KC", "proj": 23.8},
        {"plyr": "Tyreek Hill", "pos": "WR", "team": "Miami", "proj": 16.3},
    ]
    
    # Create matcher with reasonable thresholds
    matcher = PlayerMatcher(
        name_threshold=0.6,       # Allow some name variations
        position_threshold=0.8,   # Positions should be pretty similar
        team_threshold=0.4,       # Team names vary a lot (abbreviations vs full names)
        overall_threshold=0.55    # Overall similarity threshold
    )
    
    # Find all matches
    print("Finding all potential matches...")
    matches = matcher.match_players(source1, source2)
    
    print(f"Found {len(matches)} potential matches:\n")
    for match in matches:
        s1_player = match.source1_player
        s2_player = match.source2_player
        print(f"Match (similarity: {match.similarity:.3f}):")
        print(f"  Source 1: {s1_player['plyr']} ({s1_player['pos']}, {s1_player['team']}) - {s1_player['proj']}")
        print(f"  Source 2: {s2_player['plyr']} ({s2_player['pos']}, {s2_player['team']}) - {s2_player['proj']}")
        print(f"  Field similarities: {match.match_fields}")
        print()
    
    # Get best matches (no duplicates)
    print("Finding best matches (no duplicates)...")
    best_matches = matcher.get_best_matches(source1, source2, allow_duplicates=False)
    
    print(f"Found {len(best_matches)} best matches:\n")
    for match in best_matches:
        s1_player = match.source1_player
        s2_player = match.source2_player
        print(f"Best match (similarity: {match.similarity:.3f}):")
        print(f"  {s1_player['plyr']} -> {s2_player['plyr']}")
        print(f"  Projections: {s1_player['proj']} vs {s2_player['proj']}")
        print()


def demonstrate_projection_combination():
    """Demonstrate enhanced projection combination with fuzzy matching"""
    print("=== Enhanced Projection Combination Example ===\n")
    
    # Sample projection data as DataFrames
    source1_data = pd.DataFrame([
        {"plyr": "Josh Allen", "pos": "QB", "team": "BUF", "proj": 25.4, "season": 2025, "week": 1},
        {"plyr": "Jonathan Taylor", "pos": "RB", "team": "IND", "proj": 18.2, "season": 2025, "week": 1},
        {"plyr": "Davante Adams", "pos": "WR", "team": "LV", "proj": 16.8, "season": 2025, "week": 1},
        {"plyr": "Travis Kelce", "pos": "TE", "team": "KC", "proj": 14.5, "season": 2025, "week": 1},
    ])
    
    source2_data = pd.DataFrame([
        {"plyr": "J. Allen", "pos": "QB", "team": "Buffalo", "proj": 24.1, "season": 2025, "week": 1},
        {"plyr": "Jon Taylor", "pos": "RB", "team": "Indianapolis", "proj": 17.9, "season": 2025, "week": 1},
        {"plyr": "D. Adams", "pos": "WR", "team": "Las Vegas", "proj": 16.2, "season": 2025, "week": 1},
        {"plyr": "T. Kelce", "pos": "TE", "team": "Kansas City", "proj": 15.1, "season": 2025, "week": 1},
        {"plyr": "Patrick Mahomes", "pos": "QB", "team": "KC", "proj": 23.8, "season": 2025, "week": 1},
    ])
    
    print("Source 1 projections:")
    print(source1_data[['plyr', 'pos', 'team', 'proj']])
    print("\nSource 2 projections:")
    print(source2_data[['plyr', 'pos', 'team', 'proj']])
    
    # Test without fuzzy matching (traditional exact matching)
    print("\n--- Without Fuzzy Matching (Exact String Matching) ---")
    exact_combiner = ProjectionCombiner(use_fuzzy_matching=False)
    exact_result = exact_combiner.combine_projections([source1_data, source2_data])
    
    print("Combined projections (exact matching):")
    available_cols = ['plyr']
    if 'proj_0' in exact_result.columns:
        available_cols.append('proj_0')
    if 'proj_1' in exact_result.columns:
        available_cols.append('proj_1')
    if 'combined_proj' in exact_result.columns:
        available_cols.append('combined_proj')
    print(exact_result[available_cols])
    
    # Count successful matches
    exact_matches = exact_result[['proj_0', 'proj_1']].dropna().shape[0]
    print(f"\nExact matching found {exact_matches} player matches")
    
    # Test with fuzzy matching
    print("\n--- With Fuzzy Matching ---")
    fuzzy_combiner = ProjectionCombiner(
        use_fuzzy_matching=True,
        matcher_config={
            'name_threshold': 0.6,
            'team_threshold': 0.4,
            'overall_threshold': 0.5
        }
    )
    
    fuzzy_result = fuzzy_combiner.combine_projections([source1_data, source2_data])
    
    print("Combined projections (fuzzy matching):")
    display_cols = ['plyr', 'pos', 'team', 'proj_0', 'proj_1', 'combined_proj']
    if 'match_similarity' in fuzzy_result.columns:
        display_cols.append('match_similarity')
    
    print(fuzzy_result[display_cols])
    
    # Count successful matches
    fuzzy_matches = fuzzy_result[['proj_0', 'proj_1']].dropna().shape[0]
    print(f"\nFuzzy matching found {fuzzy_matches} player matches")
    
    if fuzzy_matches > exact_matches:
        print(f"Fuzzy matching improved matching by {fuzzy_matches - exact_matches} players!")


def demonstrate_merge_strategies():
    """Demonstrate different merge strategies"""
    print("=== Merge Strategies Example ===\n")
    
    source1 = [
        {"plyr": "Josh Allen", "pos": "QB", "team": "BUF", "proj": 25.4},
        {"plyr": "Jonathan Taylor", "pos": "RB", "team": "IND", "proj": 18.2},
    ]
    
    source2 = [
        {"plyr": "J. Allen", "pos": "QB", "team": "Buffalo", "proj": 24.1},
        {"plyr": "Jon Taylor", "pos": "RB", "team": "Indianapolis", "proj": 17.9},
    ]
    
    matcher = PlayerMatcher()
    matches = matcher.get_best_matches(source1, source2)
    
    print("Original matches:")
    for i, match in enumerate(matches):
        print(f"Match {i+1}: {match.source1_player['plyr']} -> {match.source2_player['plyr']}")
        print(f"  Projections: {match.source1_player['proj']} vs {match.source2_player['proj']}")
    
    # Test different merge strategies
    strategies = ['prefer_source1', 'prefer_source2', 'combine']
    
    for strategy in strategies:
        print(f"\n--- Merge Strategy: {strategy} ---")
        merged = matcher.create_merged_data(matches, merge_strategy=strategy)
        
        for i, player in enumerate(merged):
            print(f"Player {i+1}: {player['plyr']} ({player['pos']}, {player['team']})")
            for key, value in player.items():
                if 'proj' in key and key != 'proj':
                    print(f"  {key}: {value}")
            if 'match_similarity' in player:
                print(f"  match_similarity: {player['match_similarity']}")


if __name__ == "__main__":
    demonstrate_basic_matching()
    print("\n" + "="*60 + "\n")
    demonstrate_projection_combination() 
    print("\n" + "="*60 + "\n")
    demonstrate_merge_strategies()