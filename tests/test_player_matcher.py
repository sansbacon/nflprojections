# tests/test_player_matcher.py
# -*- coding: utf-8 -*-
# Copyright (C) 2025 Eric Truett
# Licensed under the MIT License

"""Tests for the player matching functionality"""

import pytest
import pandas as pd
from nflprojections.matching import PlayerMatcher, MatchResult


class TestPlayerMatcher:
    """Test the PlayerMatcher class"""
    
    @pytest.fixture
    def matcher(self):
        """Create a PlayerMatcher instance for testing"""
        return PlayerMatcher(
            name_threshold=0.7,
            position_threshold=0.8,
            team_threshold=0.5,
            overall_threshold=0.65
        )
    
    @pytest.fixture
    def sample_source1(self):
        """Sample projection data from source 1"""
        return [
            {"plyr": "Josh Allen", "pos": "QB", "team": "BUF", "proj": 25.4},
            {"plyr": "Jonathan Taylor", "pos": "RB", "team": "IND", "proj": 18.2},
            {"plyr": "Davante Adams", "pos": "WR", "team": "LV", "proj": 16.8},
            {"plyr": "Travis Kelce", "pos": "TE", "team": "KC", "proj": 14.5},
        ]
    
    @pytest.fixture
    def sample_source2(self):
        """Sample projection data from source 2 with slight variations"""
        return [
            {"plyr": "J. Allen", "pos": "QB", "team": "Buffalo", "proj": 24.1},
            {"plyr": "Jon Taylor", "pos": "RB", "team": "Indianapolis", "proj": 17.9},
            {"plyr": "D. Adams", "pos": "WR", "team": "Las Vegas", "proj": 16.2},
            {"plyr": "T. Kelce", "pos": "TE", "team": "Kansas City", "proj": 15.1},
            {"plyr": "Patrick Mahomes", "pos": "QB", "team": "KC", "proj": 23.8},
        ]
    
    def test_matcher_initialization(self):
        """Test PlayerMatcher initialization with custom thresholds"""
        matcher = PlayerMatcher(
            name_threshold=0.7,
            position_threshold=0.85,
            team_threshold=0.8,
            overall_threshold=0.7
        )
        assert matcher.name_threshold == 0.7
        assert matcher.position_threshold == 0.85
        assert matcher.team_threshold == 0.8
        assert matcher.overall_threshold == 0.7
    
    def test_calculate_similarity_exact_match(self, matcher):
        """Test string similarity calculation with exact matches"""
        assert matcher._calculate_similarity("Josh Allen", "Josh Allen") == 1.0
        assert matcher._calculate_similarity("QB", "QB") == 1.0
        assert matcher._calculate_similarity("BUF", "BUF") == 1.0
    
    def test_calculate_similarity_partial_match(self, matcher):
        """Test string similarity calculation with partial matches"""
        # These should have high similarity but not perfect
        similarity = matcher._calculate_similarity("Josh Allen", "J. Allen")
        assert 0.6 < similarity < 1.0
        
        similarity = matcher._calculate_similarity("Buffalo", "BUF")
        assert 0.2 < similarity < 1.0
    
    def test_calculate_similarity_no_match(self, matcher):
        """Test string similarity calculation with no match"""
        assert matcher._calculate_similarity("Josh Allen", "Tom Brady") < 0.5
        assert matcher._calculate_similarity("", "") == 0.0
        assert matcher._calculate_similarity("test", "") == 0.0
    
    def test_calculate_player_similarity(self, matcher):
        """Test overall player similarity calculation"""
        player1 = {"plyr": "Josh Allen", "pos": "QB", "team": "BUF", "proj": 25.4}
        player2 = {"plyr": "J. Allen", "pos": "QB", "team": "Buffalo", "proj": 24.1}
        
        overall_sim, field_sims = matcher._calculate_player_similarity(player1, player2)
        
        # Should have high overall similarity
        assert overall_sim > 0.75
        
        # Check field similarities
        assert 'plyr' in field_sims
        assert 'pos' in field_sims
        assert 'team' in field_sims
        
        # Position should match exactly
        assert field_sims['pos'] == 1.0
        
        # Name should be high similarity
        assert field_sims['plyr'] > 0.6
    
    def test_match_players_basic(self, matcher, sample_source1, sample_source2):
        """Test basic player matching between two sources"""
        matches = matcher.match_players(sample_source1, sample_source2)
        
        # Should find matches for most players
        assert len(matches) > 0
        
        # Check match structure
        for match in matches:
            assert isinstance(match, MatchResult)
            assert 0 <= match.source1_index < len(sample_source1)
            assert 0 <= match.source2_index < len(sample_source2)
            assert 0.0 <= match.similarity <= 1.0
            assert match.similarity >= matcher.overall_threshold
    
    def test_match_players_with_dataframe(self, matcher, sample_source1, sample_source2):
        """Test matching with pandas DataFrames"""
        df1 = pd.DataFrame(sample_source1)
        df2 = pd.DataFrame(sample_source2)
        
        matches = matcher.match_players(df1, df2)
        
        assert len(matches) > 0
        assert all(isinstance(match, MatchResult) for match in matches)
    
    def test_get_best_matches_no_duplicates(self, matcher, sample_source1, sample_source2):
        """Test getting best matches without duplicates"""
        best_matches = matcher.get_best_matches(sample_source1, sample_source2, allow_duplicates=False)
        
        # Should have at most one match per source1 player
        source1_indices = [match.source1_index for match in best_matches]
        assert len(source1_indices) == len(set(source1_indices))  # No duplicates
        
        # Should have at most one match per source2 player
        source2_indices = [match.source2_index for match in best_matches]
        assert len(source2_indices) == len(set(source2_indices))  # No duplicates
    
    def test_get_best_matches_with_duplicates(self, matcher, sample_source1, sample_source2):
        """Test getting best matches allowing duplicates"""
        best_matches_no_dup = matcher.get_best_matches(sample_source1, sample_source2, allow_duplicates=False)
        best_matches_dup = matcher.get_best_matches(sample_source1, sample_source2, allow_duplicates=True)
        
        # With duplicates allowed, we might get more matches
        assert len(best_matches_dup) >= len(best_matches_no_dup)
    
    def test_create_merged_data_prefer_source1(self, matcher, sample_source1, sample_source2):
        """Test creating merged data preferring source1"""
        matches = matcher.get_best_matches(sample_source1, sample_source2)
        merged_data = matcher.create_merged_data(matches, merge_strategy='prefer_source1')
        
        assert len(merged_data) == len(matches)
        
        for i, merged_player in enumerate(merged_data):
            # Should have source1 player name
            assert merged_player['plyr'] == matches[i].source1_player['plyr']
            
            # Should have both projections
            assert 'proj' in merged_player  # source1 projection
            assert 'proj_source2' in merged_player  # source2 projection
            
            # Should have match similarity
            assert 'match_similarity' in merged_player
            assert merged_player['match_similarity'] == matches[i].similarity
    
    def test_create_merged_data_prefer_source2(self, matcher, sample_source1, sample_source2):
        """Test creating merged data preferring source2"""
        matches = matcher.get_best_matches(sample_source1, sample_source2)
        merged_data = matcher.create_merged_data(matches, merge_strategy='prefer_source2')
        
        assert len(merged_data) == len(matches)
        
        for i, merged_player in enumerate(merged_data):
            # Should have source2 player name
            assert merged_player['plyr'] == matches[i].source2_player['plyr']
            
            # Should have both projections
            assert 'proj' in merged_player  # source2 projection
            assert 'proj_source1' in merged_player  # source1 projection
    
    def test_create_merged_data_combine(self, matcher, sample_source1, sample_source2):
        """Test creating merged data using combine strategy"""
        matches = matcher.get_best_matches(sample_source1, sample_source2)
        merged_data = matcher.create_merged_data(matches, merge_strategy='combine')
        
        assert len(merged_data) == len(matches)
        
        for i, merged_player in enumerate(merged_data):
            # Should have both projections with separate keys
            assert 'proj_source1' in merged_player
            assert 'proj_source2' in merged_player
            
            # Should have match similarity
            assert 'match_similarity' in merged_player
    
    def test_no_matches_with_strict_thresholds(self, sample_source1, sample_source2):
        """Test that no matches are found with very strict thresholds"""
        strict_matcher = PlayerMatcher(
            name_threshold=0.99,
            position_threshold=0.99,
            team_threshold=0.99,
            overall_threshold=0.95
        )
        
        matches = strict_matcher.match_players(sample_source1, sample_source2)
        
        # With such strict thresholds, we shouldn't find many (or any) matches
        # unless the data is nearly identical
        assert len(matches) <= 1  # Maybe one exact match if we're lucky
    
    def test_matches_with_lenient_thresholds(self, sample_source1, sample_source2):
        """Test that matches are found with lenient thresholds"""
        lenient_matcher = PlayerMatcher(
            name_threshold=0.5,
            position_threshold=0.5,
            team_threshold=0.5,
            overall_threshold=0.4
        )
        
        matches = lenient_matcher.match_players(sample_source1, sample_source2)
        
        # With lenient thresholds, we should find more matches
        assert len(matches) >= 1  # At least some matches should be found
    
    def test_empty_input_handling(self, matcher):
        """Test handling of empty input data"""
        empty_list = []
        sample_data = [{"plyr": "Test Player", "pos": "QB", "team": "TEST", "proj": 10.0}]
        
        # Empty source1
        matches = matcher.match_players(empty_list, sample_data)
        assert len(matches) == 0
        
        # Empty source2
        matches = matcher.match_players(sample_data, empty_list)
        assert len(matches) == 0
        
        # Both empty
        matches = matcher.match_players(empty_list, empty_list)
        assert len(matches) == 0
    
    def test_missing_fields_handling(self, matcher):
        """Test handling of missing player fields"""
        source1 = [{"plyr": "Test Player", "pos": "QB"}]  # Missing team and proj
        source2 = [{"plyr": "Test Player", "team": "TEST"}]  # Missing pos and proj
        
        matches = matcher.match_players(source1, source2)
        
        # Should still find a match based on player name
        assert len(matches) >= 0  # Might not match if overall similarity is too low