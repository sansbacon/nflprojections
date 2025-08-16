# nflprojections/tests/test_scoring.py
# -*- coding: utf-8 -*-
# Copyright (C) 2025 Eric Truett
# Licensed under the MIT License

import pandas as pd
import pytest

from nflprojections.scoring import Scorer
from nflprojections.scoring_formats import (
    ScoringFormat, StandardScoring, PPRScoring, DraftKingsScoring
)


class TestScorer:
    """Test the Scorer class."""
    
    def test_init_with_valid_scoring_format(self):
        """Test Scorer initialization with valid scoring format."""
        scoring_format = StandardScoring()
        scorer = Scorer(scoring_format)
        assert scorer.scoring_format is scoring_format
        
    def test_init_with_invalid_scoring_format(self):
        """Test Scorer initialization with invalid scoring format raises ValueError."""
        with pytest.raises(ValueError, match="scoring_format must be an instance of ScoringFormat"):
            Scorer("invalid")
            
        with pytest.raises(ValueError, match="scoring_format must be an instance of ScoringFormat"):
            Scorer(123)
            
        with pytest.raises(ValueError, match="scoring_format must be an instance of ScoringFormat"):
            Scorer(None)
    
    def test_calculate_fantasy_points_basic(self):
        """Test basic fantasy point calculation."""
        scorer = Scorer(PPRScoring())
        
        stats = {
            'pass_yd': 300,
            'pass_td': 2,
            'rush_yd': 50,
            'rush_td': 1,
            'rec': 5,
            'rec_yd': 75,
            'rec_td': 1
        }
        
        # PPR: pass_yd=0.04, pass_td=4.0, rush_yd=0.1, rush_td=6.0, rec=1.0, rec_yd=0.1, rec_td=6.0
        expected = (300 * 0.04) + (2 * 4.0) + (50 * 0.1) + (1 * 6.0) + (5 * 1.0) + (75 * 0.1) + (1 * 6.0)
        # 12.0 + 8.0 + 5.0 + 6.0 + 5.0 + 7.5 + 6.0 = 49.5
        
        result = scorer.calculate_fantasy_points(stats)
        assert result == pytest.approx(49.5)
        
    def test_calculate_fantasy_points_empty_stats(self):
        """Test fantasy point calculation with empty stats."""
        scorer = Scorer(StandardScoring())
        result = scorer.calculate_fantasy_points({})
        assert result == 0.0
        
    def test_calculate_fantasy_points_zero_values(self):
        """Test fantasy point calculation with zero values."""
        scorer = Scorer(StandardScoring())
        stats = {
            'pass_yd': 0,
            'pass_td': 0,
            'pass_int': 0,
            'rush_yd': 0,
            'rush_td': 0
        }
        result = scorer.calculate_fantasy_points(stats)
        assert result == 0.0
        
    def test_calculate_fantasy_points_negative_stats(self):
        """Test fantasy point calculation with negative scoring stats."""
        scorer = Scorer(StandardScoring())
        stats = {
            'pass_int': 2,  # -2 points each = -4.0
            'fumble_lost': 1  # -2 points = -2.0
        }
        result = scorer.calculate_fantasy_points(stats)
        assert result == -6.0
        
    def test_calculate_fantasy_points_unknown_stats(self):
        """Test that unknown stats are ignored (don't cause errors)."""
        scorer = Scorer(StandardScoring())
        stats = {
            'pass_yd': 200,  # 200 * 0.04 = 8.0
            'unknown_stat': 100,  # Should be ignored
            'another_unknown': 50  # Should be ignored
        }
        result = scorer.calculate_fantasy_points(stats)
        assert result == 8.0
        
    def test_calculate_fantasy_points_with_bonuses(self):
        """Test fantasy point calculation with bonus scoring."""
        scorer = Scorer(DraftKingsScoring())
        
        # DraftKings has 300+ yard passing bonus (+3), 100+ yard rushing bonus (+3)
        stats = {
            'pass_yd': 350,  # (350 * 0.04) + 3.0 bonus = 17.0
            'rush_yd': 120   # (120 * 0.1) + 3.0 bonus = 15.0
        }
        
        result = scorer.calculate_fantasy_points(stats)
        assert result == 32.0
        
    def test_calculate_fantasy_points_dst_stats(self):
        """Test fantasy point calculation with defense/special teams stats."""
        scorer = Scorer(StandardScoring())
        stats = {
            'dst_sack': 3,      # 3 * 1.0 = 3.0
            'dst_int': 2,       # 2 * 2.0 = 4.0
            'dst_fumble_rec': 1, # 1 * 2.0 = 2.0
            'dst_td': 1,        # 1 * 6.0 = 6.0
            'dst_pts_allowed': 14 # 1.0 (14-20 range)
        }
        
        result = scorer.calculate_fantasy_points(stats)
        assert result == 16.0  # 3.0 + 4.0 + 2.0 + 6.0 + 1.0
        
    def test_convert_data_basic(self):
        """Test basic data conversion."""
        scorer = Scorer(PPRScoring())
        
        data = [
            {
                'player': 'Player A',
                'passing_yards': 300,
                'passing_tds': 2,
                'rushing_yards': 50,
                'receptions': 5
            },
            {
                'player': 'Player B',
                'passing_yards': 150,
                'passing_tds': 1,
                'rushing_yards': 100,
                'receptions': 8
            }
        ]
        
        stat_columns = {
            'pass_yd': 'passing_yards',
            'pass_td': 'passing_tds', 
            'rush_yd': 'rushing_yards',
            'rec': 'receptions'
        }
        
        result = scorer.convert_data(data, stat_columns)
        
        # Check that original columns are preserved
        assert 'player' in result[0]
        assert 'passing_yards' in result[0]
        
        # Check that fantasy_points column was added
        assert 'fantasy_points' in result[0]
        assert len(result) == 2
        
        # Check calculations for first player
        # Player A: (300*0.04) + (2*4.0) + (50*0.1) + (5*1.0) = 12+8+5+5 = 30.0
        assert result[0]['fantasy_points'] == pytest.approx(30.0)
        
        # Player B: (150*0.04) + (1*4.0) + (100*0.1) + (8*1.0) = 6+4+10+8 = 28.0  
        assert result[1]['fantasy_points'] == pytest.approx(28.0)
        
    def test_convert_data_missing_columns(self):
        """Test data conversion when some stat columns are missing."""
        scorer = Scorer(StandardScoring())
        
        data = [
            {
                'player': 'Player A',
                'passing_yards': 250
                # Missing other stat columns
            }
        ]
        
        stat_columns = {
            'pass_yd': 'passing_yards',
            'pass_td': 'passing_tds',  # This column doesn't exist
            'rush_yd': 'rushing_yards'  # This column doesn't exist
        }
        
        result = scorer.convert_data(data, stat_columns)
        
        # Should handle missing columns gracefully (treat as 0)
        # Player A: (250*0.04) + (0*4.0) + (0*0.1) = 10.0
        assert result[0]['fantasy_points'] == pytest.approx(10.0)
        
    def test_convert_data_empty_data(self):
        """Test data conversion with empty data."""
        scorer = Scorer(StandardScoring())
        
        data = []
        stat_columns = {'pass_yd': 'passing_yards'}
        
        result = scorer.convert_data(data, stat_columns)
        
        assert len(result) == 0
        
    def test_get_scoring_rules(self):
        """Test getting scoring rules as dictionary."""
        scoring_format = PPRScoring()
        scorer = Scorer(scoring_format)
        
        rules = scorer.get_scoring_rules()
        
        # Check that it returns a dictionary
        assert isinstance(rules, dict)
        
        # Check that key scoring rules are present
        assert 'pass_yd' in rules
        assert 'pass_td' in rules
        assert 'rec' in rules
        
        # Check some expected values for PPR
        assert rules['pass_yd'] == 0.04
        assert rules['pass_td'] == 4.0
        assert rules['rec'] == 1.0  # PPR gives 1 point per reception
        
    def test_scorer_with_different_scoring_formats(self):
        """Test Scorer works correctly with different scoring formats."""
        stats = {'rec': 10}  # 10 receptions
        
        # Standard scoring: 0 points per reception
        standard_scorer = Scorer(StandardScoring())
        standard_result = standard_scorer.calculate_fantasy_points(stats)
        assert standard_result == 0.0
        
        # PPR scoring: 1 point per reception  
        ppr_scorer = Scorer(PPRScoring())
        ppr_result = ppr_scorer.calculate_fantasy_points(stats)
        assert ppr_result == 10.0
        
        # Verify they produce different results
        assert standard_result != ppr_result


class TestScorerIntegration:
    """Integration tests for Scorer with realistic scenarios."""
    
    def test_quarterback_scoring_scenario(self):
        """Test realistic QB scoring scenario."""
        scorer = Scorer(PPRScoring())
        
        # Tom Brady type performance
        qb_stats = {
            'pass_yd': 325,
            'pass_td': 3, 
            'pass_int': 1,
            'rush_yd': 5,
            'two_pt': 1
        }
        
        # PPR: (325*0.04) + (3*4.0) + (1*-2.0) + (5*0.1) + (1*2.0)
        # = 13.0 + 12.0 - 2.0 + 0.5 + 2.0 = 25.5
        result = scorer.calculate_fantasy_points(qb_stats)
        assert result == pytest.approx(25.5)
        
    def test_running_back_scoring_scenario(self):
        """Test realistic RB scoring scenario."""
        scorer = Scorer(DraftKingsScoring())  # Has rushing bonuses
        
        # Elite RB performance with bonus
        rb_stats = {
            'rush_yd': 150,  # Gets 100+ yard bonus
            'rush_td': 2,
            'rec': 6,
            'rec_yd': 45,
            'fumble_lost': 1
        }
        
        # DraftKings: (150*0.1 + 3.0 bonus) + (2*6.0) + (6*1.0) + (45*0.1) + (1*-1.0)
        # = 18.0 + 12.0 + 6.0 + 4.5 - 1.0 = 39.5
        result = scorer.calculate_fantasy_points(rb_stats)
        assert result == pytest.approx(39.5)
        
    def test_wide_receiver_scoring_scenario(self):
        """Test realistic WR scoring scenario.""" 
        scorer = Scorer(PPRScoring())
        
        wr_stats = {
            'rec': 12,
            'rec_yd': 140,
            'rec_td': 2,
            'rush_yd': 15,  # End around
            'fumble_lost': 0
        }
        
        # PPR: (12*1.0) + (140*0.1) + (2*6.0) + (15*0.1)
        # = 12.0 + 14.0 + 12.0 + 1.5 = 39.5
        result = scorer.calculate_fantasy_points(wr_stats)
        assert result == pytest.approx(39.5)
        
    def test_defense_scoring_scenario(self):
        """Test realistic DEF scoring scenario."""
        scorer = Scorer(StandardScoring())
        
        def_stats = {
            'dst_sack': 4,
            'dst_int': 1, 
            'dst_fumble_rec': 2,
            'dst_td': 1,
            'dst_safety': 1,
            'dst_pts_allowed': 10  # 7-13 points allowed
        }
        
        # Standard: (4*1.0) + (1*2.0) + (2*2.0) + (1*6.0) + (1*2.0) + 4.0
        # = 4.0 + 2.0 + 4.0 + 6.0 + 2.0 + 4.0 = 22.0
        result = scorer.calculate_fantasy_points(def_stats)
        assert result == pytest.approx(22.0)