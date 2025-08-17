# examples/complete_matching_workflow.py
# -*- coding: utf-8 -*-
# Copyright (C) 2025 Eric Truett  
# Licensed under the MIT License

"""
Complete workflow example demonstrating player matching across NFL projection sources.

This example shows how the new fuzzy matching functionality can dramatically improve
the accuracy of projection combination when dealing with real-world data variations.
"""

import pandas as pd
from nflprojections import PlayerMatcher, ProjectionCombiner, CombinationMethod


def create_realistic_sample_data():
    """Create realistic sample projection data with common variations"""
    
    # NFL.com style projections
    nfl_projections = pd.DataFrame([
        {"plyr": "Josh Allen", "pos": "QB", "team": "BUF", "proj": 25.4, "source": "NFL.com"},
        {"plyr": "Jonathan Taylor", "pos": "RB", "team": "IND", "proj": 18.2, "source": "NFL.com"},
        {"plyr": "Davante Adams", "pos": "WR", "team": "LV", "proj": 16.8, "source": "NFL.com"},
        {"plyr": "Travis Kelce", "pos": "TE", "team": "KC", "proj": 14.5, "source": "NFL.com"},
        {"plyr": "Lamar Jackson", "pos": "QB", "team": "BAL", "proj": 24.8, "source": "NFL.com"},
        {"plyr": "Christian McCaffrey", "pos": "RB", "team": "SF", "proj": 19.1, "source": "NFL.com"},
    ])
    
    # ESPN style projections (different naming conventions)  
    espn_projections = pd.DataFrame([
        {"plyr": "J. Allen", "pos": "QB", "team": "Buffalo", "proj": 24.1, "source": "ESPN"},
        {"plyr": "Jon Taylor", "pos": "RB", "team": "Indianapolis", "proj": 17.9, "source": "ESPN"},  
        {"plyr": "D. Adams", "pos": "WR", "team": "Las Vegas", "proj": 16.2, "source": "ESPN"},
        {"plyr": "T. Kelce", "pos": "TE", "team": "Kansas City", "proj": 15.1, "source": "ESPN"},
        {"plyr": "L. Jackson", "pos": "QB", "team": "Baltimore", "proj": 23.9, "source": "ESPN"},
        {"plyr": "C. McCaffrey", "pos": "RB", "team": "San Francisco", "proj": 18.8, "source": "ESPN"},
        {"plyr": "Patrick Mahomes", "pos": "QB", "team": "Kansas City", "proj": 23.5, "source": "ESPN"},
    ])
    
    # FantasyPros style (yet another variation)
    fp_projections = pd.DataFrame([
        {"plyr": "Josh Allen (BUF)", "pos": "QB", "team": "BUF", "proj": 25.8, "source": "FantasyPros"},
        {"plyr": "Jonathan Taylor (IND)", "pos": "RB", "team": "IND", "proj": 18.5, "source": "FantasyPros"},
        {"plyr": "Davante Adams (LV)", "pos": "WR", "team": "LV", "proj": 17.1, "source": "FantasyPros"},
        {"plyr": "Lamar Jackson (BAL)", "pos": "QB", "team": "BAL", "proj": 24.2, "source": "FantasyPros"},
        {"plyr": "Chris McCaffrey (SF)", "pos": "RB", "team": "SF", "proj": 19.4, "source": "FantasyPros"},
        {"plyr": "Tyreek Hill (MIA)", "pos": "WR", "team": "MIA", "proj": 16.9, "source": "FantasyPros"},
    ])
    
    return nfl_projections, espn_projections, fp_projections


def analyze_matching_effectiveness():
    """Analyze how effective fuzzy matching is compared to exact matching"""
    
    print("=== NFL Projection Matching Analysis ===\n")
    
    nfl_data, espn_data, fp_data = create_realistic_sample_data()
    
    print("Sample data from three sources:")
    print("\nNFL.com projections:")
    print(nfl_data[['plyr', 'pos', 'team', 'proj']])
    print(f"Total players: {len(nfl_data)}")
    
    print("\nESPN projections:")  
    print(espn_data[['plyr', 'pos', 'team', 'proj']])
    print(f"Total players: {len(espn_data)}")
    
    print("\nFantasyPros projections:")
    print(fp_data[['plyr', 'pos', 'team', 'proj']])
    print(f"Total players: {len(fp_data)}")
    
    # Test exact vs fuzzy matching between NFL.com and ESPN
    print("\n" + "="*60)
    print("NFL.com vs ESPN Matching Comparison")
    print("="*60)
    
    # Exact matching
    exact_combiner = ProjectionCombiner(use_fuzzy_matching=False)
    exact_result = exact_combiner.combine_projections([nfl_data, espn_data])
    exact_matches = exact_result[['proj_0', 'proj_1']].dropna().shape[0]
    
    print(f"\nExact matching results:")
    print(f"Total entries: {len(exact_result)}")
    print(f"Successful matches: {exact_matches}")
    print(f"Match rate: {exact_matches/min(len(nfl_data), len(espn_data))*100:.1f}%")
    
    # Fuzzy matching
    fuzzy_combiner = ProjectionCombiner(
        use_fuzzy_matching=True,
        matcher_config={
            'name_threshold': 0.6,
            'team_threshold': 0.3,  # Very lenient for team names
            'overall_threshold': 0.5
        }
    )
    fuzzy_result = fuzzy_combiner.combine_projections([nfl_data, espn_data])
    fuzzy_matches = fuzzy_result[['proj_0', 'proj_1']].dropna().shape[0]
    
    print(f"\nFuzzy matching results:")
    print(f"Total entries: {len(fuzzy_result)}")  
    print(f"Successful matches: {fuzzy_matches}")
    print(f"Match rate: {fuzzy_matches/min(len(nfl_data), len(espn_data))*100:.1f}%")
    
    improvement = fuzzy_matches - exact_matches
    print(f"\nImprovement: +{improvement} matches ({improvement/min(len(nfl_data), len(espn_data))*100:.1f} percentage points)")
    
    # Show the matched players with similarity scores
    if 'match_similarity' in fuzzy_result.columns:
        matched_players = fuzzy_result.dropna(subset=['match_similarity'])
        print(f"\nMatched players with similarity scores:")
        for _, player in matched_players.iterrows():
            print(f"  {player['plyr']} - Similarity: {player['match_similarity']:.3f}")
            print(f"    Projections: {player['proj_0']:.1f} vs {player['proj_1']:.1f}")


def demonstrate_three_source_combination():
    """Demonstrate combining projections from three different sources"""
    
    print("\n" + "="*60)
    print("Three-Source Projection Combination")
    print("="*60)
    
    nfl_data, espn_data, fp_data = create_realistic_sample_data()
    
    # Use fuzzy matching to combine all three sources
    combiner = ProjectionCombiner(
        method=CombinationMethod.AVERAGE,
        use_fuzzy_matching=True,
        matcher_config={
            'name_threshold': 0.5,     # More lenient for FantasyPros format
            'team_threshold': 0.3,
            'overall_threshold': 0.45
        }
    )
    
    combined_result = combiner.combine_projections([nfl_data, espn_data, fp_data])
    
    print(f"\nCombined results from all three sources:")
    print(f"Total unique players: {len(combined_result)}")
    
    # Show players that were matched across multiple sources
    multi_source_matches = combined_result[
        combined_result[['proj_0', 'proj_1', 'proj_2']].count(axis=1) >= 2
    ]
    
    print(f"Players found in multiple sources: {len(multi_source_matches)}")
    
    if len(multi_source_matches) > 0:
        print("\nMulti-source matches:")
        display_cols = ['plyr', 'pos', 'proj_0', 'proj_1', 'proj_2', 'combined_proj']
        if 'match_similarity' in multi_source_matches.columns:
            display_cols.append('match_similarity')
        
        for _, player in multi_source_matches.iterrows():
            print(f"\n{player['plyr']} ({player['pos']}):")
            print(f"  NFL.com: {player['proj_0'] or 'N/A'}")
            print(f"  ESPN: {player['proj_1'] or 'N/A'}")  
            print(f"  FantasyPros: {player['proj_2'] or 'N/A'}")
            print(f"  Combined: {player['combined_proj']:.1f}")


def demonstrate_custom_matching_thresholds():
    """Show how different threshold settings affect matching"""
    
    print("\n" + "="*60) 
    print("Custom Threshold Analysis")
    print("="*60)
    
    nfl_data, espn_data, _ = create_realistic_sample_data()
    
    threshold_configs = [
        {
            'name': 'Strict',
            'config': {
                'name_threshold': 0.8,
                'team_threshold': 0.7, 
                'overall_threshold': 0.75
            }
        },
        {
            'name': 'Moderate', 
            'config': {
                'name_threshold': 0.6,
                'team_threshold': 0.4,
                'overall_threshold': 0.55
            }
        },
        {
            'name': 'Lenient',
            'config': {
                'name_threshold': 0.4,
                'team_threshold': 0.2,
                'overall_threshold': 0.35
            }
        }
    ]
    
    print("Testing different threshold configurations:\n")
    
    for threshold_set in threshold_configs:
        combiner = ProjectionCombiner(
            use_fuzzy_matching=True,
            matcher_config=threshold_set['config']
        )
        
        result = combiner.combine_projections([nfl_data, espn_data])
        matches = result[['proj_0', 'proj_1']].dropna().shape[0]
        match_rate = matches / min(len(nfl_data), len(espn_data)) * 100
        
        print(f"{threshold_set['name']} thresholds:")
        print(f"  Matches found: {matches}/{min(len(nfl_data), len(espn_data))} ({match_rate:.1f}%)")
        
        if 'match_similarity' in result.columns:
            matched_data = result.dropna(subset=['match_similarity'])
            if len(matched_data) > 0:
                avg_similarity = matched_data['match_similarity'].mean()
                print(f"  Average similarity: {avg_similarity:.3f}")
        print()


if __name__ == "__main__":
    analyze_matching_effectiveness()
    demonstrate_three_source_combination()
    demonstrate_custom_matching_thresholds()
    
    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    print("The fuzzy matching system successfully handles common variations in:")
    print("• Player name formats (Josh Allen vs J. Allen)")
    print("• Team abbreviations (BUF vs Buffalo)")  
    print("• Name suffixes and prefixes (Jonathan vs Jon)")
    print("• Team name variations (Kansas City vs KC)")
    print("\nThis dramatically improves projection combination accuracy!")