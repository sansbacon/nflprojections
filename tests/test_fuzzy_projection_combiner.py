# tests/test_fuzzy_projection_combiner.py
# -*- coding: utf-8 -*-
# Copyright (C) 2025 Eric Truett
# Licensed under the MIT License

"""Tests for the enhanced ProjectionCombiner with fuzzy matching"""

import pytest
import pandas as pd
import numpy as np
from nflprojections.combine import ProjectionCombiner, CombinationMethod


class TestFuzzyProjectionCombiner:
    """Test the ProjectionCombiner with fuzzy matching functionality"""
    
    @pytest.fixture
    def sample_projections_list(self):
        """Sample projection data as list of DataFrames with slight variations"""
        source1_data = [
            {"plyr": "Josh Allen", "pos": "QB", "team": "BUF", "proj": 25.4},
            {"plyr": "Jonathan Taylor", "pos": "RB", "team": "IND", "proj": 18.2},
            {"plyr": "Davante Adams", "pos": "WR", "team": "LV", "proj": 16.8},
            {"plyr": "Travis Kelce", "pos": "TE", "team": "KC", "proj": 14.5},
        ]
        
        source2_data = [
            {"plyr": "J. Allen", "pos": "QB", "team": "Buffalo", "proj": 24.1},
            {"plyr": "Jon Taylor", "pos": "RB", "team": "Indianapolis", "proj": 17.9},
            {"plyr": "D. Adams", "pos": "WR", "team": "Las Vegas", "proj": 16.2},
            {"plyr": "T. Kelce", "pos": "TE", "team": "Kansas City", "proj": 15.1},
            {"plyr": "Patrick Mahomes", "pos": "QB", "team": "KC", "proj": 23.8},
        ]
        
        return [pd.DataFrame(source1_data), pd.DataFrame(source2_data)]
    
    def test_combiner_without_fuzzy_matching(self, sample_projections_list):
        """Test basic combiner without fuzzy matching (should work as before)"""
        combiner = ProjectionCombiner(use_fuzzy_matching=False)
        
        # This should use exact string matching (traditional behavior)
        result = combiner.combine_projections(sample_projections_list)
        
        # Should have some results but likely not all players matched due to name differences
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0
        assert 'combined_proj' in result.columns
    
    def test_combiner_with_fuzzy_matching(self, sample_projections_list):
        """Test combiner with fuzzy matching enabled"""
        combiner = ProjectionCombiner(
            use_fuzzy_matching=True,
            matcher_config={
                'name_threshold': 0.6,
                'team_threshold': 0.4,
                'overall_threshold': 0.5
            }
        )
        
        result = combiner.combine_projections(sample_projections_list)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0
        assert 'combined_proj' in result.columns
        
        # Should have match similarity info for matched players
        if 'match_similarity' in result.columns:
            matched_players = result.dropna(subset=['match_similarity'])
            assert len(matched_players) > 0
    
    def test_fuzzy_matching_improves_matches(self, sample_projections_list):
        """Test that fuzzy matching finds more matches than exact matching"""
        # Test with exact matching
        exact_combiner = ProjectionCombiner(use_fuzzy_matching=False)
        exact_result = exact_combiner.combine_projections(sample_projections_list)
        
        # Test with fuzzy matching
        fuzzy_combiner = ProjectionCombiner(
            use_fuzzy_matching=True,
            matcher_config={
                'name_threshold': 0.6,
                'team_threshold': 0.4,
                'overall_threshold': 0.5
            }
        )
        fuzzy_result = fuzzy_combiner.combine_projections(sample_projections_list)
        
        # Count non-null projection pairs
        exact_matched = exact_result[['proj_0', 'proj_1']].dropna().shape[0]
        fuzzy_matched = fuzzy_result[['proj_0', 'proj_1']].dropna().shape[0]
        
        # Fuzzy matching should find at least as many matches as exact matching
        assert fuzzy_matched >= exact_matched
    
    def test_single_projection_source(self):
        """Test combiner with only one projection source"""
        single_source = [pd.DataFrame([
            {"plyr": "Josh Allen", "pos": "QB", "team": "BUF", "proj": 25.4},
            {"plyr": "Jonathan Taylor", "pos": "RB", "team": "IND", "proj": 18.2},
        ])]
        
        combiner = ProjectionCombiner(use_fuzzy_matching=True)
        result = combiner.combine_projections(single_source)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert 'combined_proj' in result.columns
        # Should just be the original projections
        assert result['combined_proj'].tolist() == [25.4, 18.2]
    
    def test_empty_projections(self):
        """Test combiner with empty projection list"""
        combiner = ProjectionCombiner(use_fuzzy_matching=True)
        result = combiner.combine_projections([])
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
    
    def test_fuzzy_matching_with_different_methods(self, sample_projections_list):
        """Test fuzzy matching with different combination methods"""
        combiner = ProjectionCombiner(
            method=CombinationMethod.MEDIAN,
            use_fuzzy_matching=True,
            matcher_config={
                'name_threshold': 0.6,
                'team_threshold': 0.4,
                'overall_threshold': 0.5
            }
        )
        
        result = combiner.combine_projections(sample_projections_list)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0
        assert 'combined_proj' in result.columns
    
    def test_matcher_config_validation(self):
        """Test that matcher config is properly passed to PlayerMatcher"""
        custom_config = {
            'name_threshold': 0.5,
            'position_threshold': 0.9,
            'team_threshold': 0.3,
            'overall_threshold': 0.4
        }
        
        combiner = ProjectionCombiner(
            use_fuzzy_matching=True,
            matcher_config=custom_config
        )
        
        # Verify the matcher was created with the right config
        assert combiner.player_matcher is not None
        assert combiner.player_matcher.name_threshold == 0.5
        assert combiner.player_matcher.position_threshold == 0.9
        assert combiner.player_matcher.team_threshold == 0.3
        assert combiner.player_matcher.overall_threshold == 0.4
    
    def test_list_dict_input_with_fuzzy_matching(self):
        """Test fuzzy matching with list of dict input format"""
        source1_data = [
            {"plyr": "Josh Allen", "pos": "QB", "team": "BUF", "proj": 25.4},
            {"plyr": "Jonathan Taylor", "pos": "RB", "team": "IND", "proj": 18.2},
        ]
        
        source2_data = [
            {"plyr": "J. Allen", "pos": "QB", "team": "Buffalo", "proj": 24.1},
            {"plyr": "Jon Taylor", "pos": "RB", "team": "Indianapolis", "proj": 17.9},
        ]
        
        combiner = ProjectionCombiner(
            use_fuzzy_matching=True,
            matcher_config={
                'name_threshold': 0.6,
                'team_threshold': 0.4,
                'overall_threshold': 0.5
            }
        )
        
        result = combiner.combine_projections([source1_data, source2_data])
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0
        assert 'combined_proj' in result.columns
    
    def test_mixed_input_formats(self, sample_projections_list):
        """Test combiner with mixed DataFrame and list input formats"""
        source1_df = sample_projections_list[0]  # DataFrame
        source2_list = sample_projections_list[1].to_dict('records')  # List of dicts
        
        combiner = ProjectionCombiner(use_fuzzy_matching=True)
        result = combiner.combine_projections([source1_df, source2_list])
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0
        assert 'combined_proj' in result.columns
    
    def test_fuzzy_matching_preserves_player_info(self, sample_projections_list):
        """Test that fuzzy matching preserves player information from first source"""
        combiner = ProjectionCombiner(
            use_fuzzy_matching=True,
            matcher_config={
                'name_threshold': 0.6,
                'team_threshold': 0.4,
                'overall_threshold': 0.5
            }
        )
        
        result = combiner.combine_projections(sample_projections_list)
        
        # Should preserve key player info columns
        required_columns = {'plyr', 'pos', 'team'}
        assert required_columns.issubset(set(result.columns))
        
        # Player names should match the first source format
        first_source_players = set(sample_projections_list[0]['plyr'])
        result_players = set(result['plyr'].dropna())
        
        # There should be significant overlap with the first source
        overlap = len(first_source_players & result_players)
        assert overlap > 0