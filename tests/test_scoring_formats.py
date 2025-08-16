# nflprojections/tests/test_scoring_formats.py
# -*- coding: utf-8 -*-
# Copyright (C) 2025 Eric Truett
# Licensed under the MIT License

import pytest

from nflprojections.scoring_formats import (
    ScoringFormat, StandardScoring, HalfPPRScoring, PPRScoring,
    DraftKingsScoring, FanDuelScoring, YahooScoring, HomeAuctionScoring
)


class TestScoringFormat:
    """Test the base ScoringFormat class."""
    
    def test_instantiation_with_required_fields(self):
        """Test that ScoringFormat can be instantiated with required fields."""
        scoring = ScoringFormat(
            pass_yd=0.04, pass_td=4.0, pass_int=-2.0,
            rush_yd=0.1, rush_td=6.0,
            rec=1.0, rec_yd=0.1, rec_td=6.0,
            fumble_lost=-2.0, two_pt=2.0
        )
        assert scoring.pass_yd == 0.04
        assert scoring.pass_td == 4.0
        assert scoring.rec == 1.0
        assert scoring.xp is None  # Optional field defaults to None
        assert scoring.bonuses == {}  # Default empty dict

    def test_get_score_basic_stats(self):
        """Test get_score method with basic stat calculations."""
        scoring = ScoringFormat(
            pass_yd=0.04, pass_td=4.0, pass_int=-2.0,
            rush_yd=0.1, rush_td=6.0,
            rec=1.0, rec_yd=0.1, rec_td=6.0,
            fumble_lost=-2.0, two_pt=2.0
        )
        
        # Test positive scoring
        assert scoring.get_score('pass_yd', 250) == 10.0  # 250 * 0.04
        assert scoring.get_score('pass_td', 2) == 8.0     # 2 * 4.0
        assert scoring.get_score('rec', 8) == 8.0         # 8 * 1.0
        
        # Test negative scoring
        assert scoring.get_score('pass_int', 1) == -2.0   # 1 * -2.0
        assert scoring.get_score('fumble_lost', 2) == -4.0 # 2 * -2.0

    def test_get_score_unknown_stat(self):
        """Test get_score returns 0 for unknown stats."""
        scoring = ScoringFormat(
            pass_yd=0.04, pass_td=4.0, pass_int=-2.0,
            rush_yd=0.1, rush_td=6.0,
            rec=1.0, rec_yd=0.1, rec_td=6.0,
            fumble_lost=-2.0, two_pt=2.0
        )
        
        assert scoring.get_score('unknown_stat', 10) == 0.0

    def test_get_score_zero_values(self):
        """Test get_score with zero values."""
        scoring = ScoringFormat(
            pass_yd=0.04, pass_td=4.0, pass_int=-2.0,
            rush_yd=0.1, rush_td=6.0,
            rec=1.0, rec_yd=0.1, rec_td=6.0,
            fumble_lost=-2.0, two_pt=2.0
        )
        
        assert scoring.get_score('pass_yd', 0) == 0.0
        assert scoring.get_score('pass_td', 0) == 0.0

    def test_get_score_dst_pts_allowed(self):
        """Test get_score with dst_pts_allowed threshold logic."""
        dst_pts = {0: 10.0, 1: 7.0, 7: 4.0, 14: 1.0, 21: 0.0, 28: -1.0, 35: -4.0}
        scoring = ScoringFormat(
            pass_yd=0.04, pass_td=4.0, pass_int=-2.0,
            rush_yd=0.1, rush_td=6.0,
            rec=1.0, rec_yd=0.1, rec_td=6.0,
            fumble_lost=-2.0, two_pt=2.0,
            dst_pts_allowed=dst_pts
        )
        
        # Test threshold boundaries
        assert scoring.get_score('dst_pts_allowed', 0) == 10.0   # Shutout
        assert scoring.get_score('dst_pts_allowed', 6) == 7.0    # 1-6 points
        assert scoring.get_score('dst_pts_allowed', 7) == 4.0    # 7-13 points
        assert scoring.get_score('dst_pts_allowed', 13) == 4.0   # Still 7-13
        assert scoring.get_score('dst_pts_allowed', 14) == 1.0   # 14-20 points
        assert scoring.get_score('dst_pts_allowed', 21) == 0.0   # 21-27 points
        assert scoring.get_score('dst_pts_allowed', 28) == -1.0  # 28-34 points
        assert scoring.get_score('dst_pts_allowed', 35) == -4.0  # 35+ points
        assert scoring.get_score('dst_pts_allowed', 50) == -4.0  # Still 35+

    def test_get_score_bonuses(self):
        """Test get_score with bonus scoring."""
        bonuses = {('pass_yd', 300): 3.0, ('rush_yd', 100): 5.0}
        scoring = ScoringFormat(
            pass_yd=0.04, pass_td=4.0, pass_int=-2.0,
            rush_yd=0.1, rush_td=6.0,
            rec=1.0, rec_yd=0.1, rec_td=6.0,
            fumble_lost=-2.0, two_pt=2.0,
            bonuses=bonuses
        )
        
        # Test bonus triggered
        assert scoring.get_score('pass_yd', 350) == 17.0  # (350 * 0.04) + 3.0 bonus
        assert scoring.get_score('rush_yd', 120) == 17.0  # (120 * 0.1) + 5.0 bonus
        
        # Test bonus not triggered
        assert scoring.get_score('pass_yd', 250) == 10.0  # 250 * 0.04, no bonus
        assert scoring.get_score('rush_yd', 90) == 9.0    # 90 * 0.1, no bonus
        
        # Test exact threshold
        assert scoring.get_score('pass_yd', 300) == 15.0  # (300 * 0.04) + 3.0 bonus
        assert scoring.get_score('rush_yd', 100) == 15.0  # (100 * 0.1) + 5.0 bonus


class TestStandardScoring:
    """Test StandardScoring format."""
    
    def test_instantiation(self):
        """Test StandardScoring instantiation and default values."""
        scoring = StandardScoring()
        
        # Test key characteristics of standard scoring
        assert scoring.rec == 0.0  # No PPR
        assert scoring.pass_int == -2.0  # -2 for interceptions
        assert scoring.fumble_lost == -2.0  # -2 for fumbles
        assert scoring.xp == 1.0  # Has extra points
        assert scoring.bonuses == {}  # No bonuses

    def test_scoring_calculation(self):
        """Test scoring calculations specific to standard format."""
        scoring = StandardScoring()
        
        # Test that receptions get no points
        assert scoring.get_score('rec', 10) == 0.0
        
        # Test standard interception penalty
        assert scoring.get_score('pass_int', 1) == -2.0


class TestHalfPPRScoring:
    """Test HalfPPRScoring format."""
    
    def test_instantiation(self):
        """Test HalfPPRScoring instantiation and default values."""
        scoring = HalfPPRScoring()
        
        assert scoring.rec == 0.5  # Half point per reception
        assert scoring.pass_int == -2.0
        assert scoring.fumble_lost == -2.0

    def test_scoring_calculation(self):
        """Test scoring calculations specific to half-PPR format."""
        scoring = HalfPPRScoring()
        
        # Test half-PPR scoring
        assert scoring.get_score('rec', 10) == 5.0  # 10 * 0.5


class TestPPRScoring:
    """Test PPRScoring format."""
    
    def test_instantiation(self):
        """Test PPRScoring instantiation and default values."""
        scoring = PPRScoring()
        
        assert scoring.rec == 1.0  # Full point per reception
        assert scoring.pass_int == -2.0
        assert scoring.fumble_lost == -2.0

    def test_scoring_calculation(self):
        """Test scoring calculations specific to PPR format."""
        scoring = PPRScoring()
        
        # Test full PPR scoring
        assert scoring.get_score('rec', 10) == 10.0  # 10 * 1.0


class TestDraftKingsScoring:
    """Test DraftKingsScoring format."""
    
    def test_instantiation(self):
        """Test DraftKingsScoring instantiation and default values."""
        scoring = DraftKingsScoring()
        
        assert scoring.rec == 1.0  # Full PPR
        assert scoring.pass_int == -1.0  # Less penalty than standard
        assert scoring.fumble_lost == -1.0  # Less penalty than standard
        assert scoring.xp is None  # No kicker scoring
        
        # Test bonus structure
        expected_bonuses = {
            ('pass_yd', 300): 3.0,
            ('rush_yd', 100): 3.0,
            ('rec_yd', 100): 3.0
        }
        assert scoring.bonuses == expected_bonuses

    def test_bonus_scoring(self):
        """Test bonus scoring in DraftKings format."""
        scoring = DraftKingsScoring()
        
        # Test 300+ yard passing bonus
        assert scoring.get_score('pass_yd', 350) == 17.0  # (350 * 0.04) + 3.0
        
        # Test 100+ yard rushing bonus
        assert scoring.get_score('rush_yd', 150) == 18.0  # (150 * 0.1) + 3.0
        
        # Test 100+ yard receiving bonus
        assert scoring.get_score('rec_yd', 120) == 15.0  # (120 * 0.1) + 3.0


class TestFanDuelScoring:
    """Test FanDuelScoring format."""
    
    def test_instantiation(self):
        """Test FanDuelScoring instantiation and default values."""
        scoring = FanDuelScoring()
        
        assert scoring.rec == 0.5  # Half PPR
        assert scoring.pass_int == -1.0
        assert scoring.fumble_lost == -2.0
        assert scoring.xp == 1.0  # Has kicker scoring

    def test_scoring_calculation(self):
        """Test scoring calculations specific to FanDuel format."""
        scoring = FanDuelScoring()
        
        # Test half-PPR scoring
        assert scoring.get_score('rec', 8) == 4.0  # 8 * 0.5


class TestYahooScoring:
    """Test YahooScoring format."""
    
    def test_instantiation(self):
        """Test YahooScoring instantiation and default values."""
        scoring = YahooScoring()
        
        assert scoring.rec == 0.5  # Half PPR
        assert scoring.pass_int == -1.0
        assert scoring.fumble_lost == -2.0
        assert scoring.xp == 1.0  # Has kicker scoring


class TestHomeAuctionScoring:
    """Test HomeAuctionScoring format."""
    
    def test_instantiation(self):
        """Test HomeAuctionScoring instantiation and default values."""
        scoring = HomeAuctionScoring()
        
        assert scoring.rec == 1.0  # Full PPR
        assert scoring.pass_int == -1.0
        assert scoring.fumble_lost == -1.0
        assert scoring.xp is None  # No kicker scoring
        
        # Test bonus structure (higher bonuses than DraftKings)
        expected_bonuses = {
            ('pass_yd', 300): 5.0,
            ('rush_yd', 100): 5.0,
            ('rec_yd', 100): 5.0
        }
        assert scoring.bonuses == expected_bonuses

    def test_bonus_scoring(self):
        """Test bonus scoring in HomeAuction format."""
        scoring = HomeAuctionScoring()
        
        # Test higher bonus values
        assert scoring.get_score('pass_yd', 350) == 19.0  # (350 * 0.04) + 5.0
        assert scoring.get_score('rush_yd', 150) == 20.0  # (150 * 0.1) + 5.0


class TestScoringFormatComparisons:
    """Test comparisons between different scoring formats."""
    
    def test_ppr_differences(self):
        """Test reception scoring differences between formats."""
        standard = StandardScoring()
        half_ppr = HalfPPRScoring()
        full_ppr = PPRScoring()
        
        receptions = 10
        
        assert standard.get_score('rec', receptions) == 0.0
        assert half_ppr.get_score('rec', receptions) == 5.0
        assert full_ppr.get_score('rec', receptions) == 10.0

    def test_interception_penalties(self):
        """Test interception penalty differences."""
        standard = StandardScoring()
        draftkings = DraftKingsScoring()
        
        assert standard.get_score('pass_int', 1) == -2.0
        assert draftkings.get_score('pass_int', 1) == -1.0

    def test_bonus_format_differences(self):
        """Test bonus differences between DraftKings and HomeAuction."""
        dk = DraftKingsScoring()
        ha = HomeAuctionScoring()
        
        pass_yards = 350
        
        dk_score = dk.get_score('pass_yd', pass_yards)
        ha_score = ha.get_score('pass_yd', pass_yards)
        
        # Both should have same base score but different bonuses
        base_score = pass_yards * 0.04  # 14.0
        assert dk_score == base_score + 3.0  # 17.0
        assert ha_score == base_score + 5.0  # 19.0


class TestRealisticScenarios:
    """Test realistic player performance scenarios."""
    
    def test_quarterback_performance(self):
        """Test typical QB stat line."""
        ppr = PPRScoring()
        
        # QB: 280 pass yards, 2 pass TDs, 1 INT, 25 rush yards, 1 rush TD
        stats = {
            'pass_yd': 280,
            'pass_td': 2,
            'pass_int': 1,
            'rush_yd': 25,
            'rush_td': 1
        }
        
        expected = (280 * 0.04) + (2 * 4.0) + (1 * -2.0) + (25 * 0.1) + (1 * 6.0)
        # 11.2 + 8.0 - 2.0 + 2.5 + 6.0 = 25.7
        
        total = sum(ppr.get_score(stat, value) for stat, value in stats.items())
        assert total == pytest.approx(25.7)

    def test_running_back_performance(self):
        """Test typical RB stat line with bonus."""
        dk = DraftKingsScoring()
        
        # RB: 120 rush yards, 1 rush TD, 5 receptions, 45 rec yards
        stats = {
            'rush_yd': 120,
            'rush_td': 1,
            'rec': 5,
            'rec_yd': 45
        }
        
        expected = (120 * 0.1 + 3.0) + (1 * 6.0) + (5 * 1.0) + (45 * 0.1)
        # 15.0 + 6.0 + 5.0 + 4.5 = 30.5
        
        total = sum(dk.get_score(stat, value) for stat, value in stats.items())
        assert total == 30.5

    def test_defense_performance(self):
        """Test defense scoring with points allowed."""
        standard = StandardScoring()
        
        # Defense: 2 sacks, 1 INT, 1 fumble recovery, 1 TD, allowed 14 points
        stats = {
            'dst_sack': 2,
            'dst_int': 1,
            'dst_fumble_rec': 1,
            'dst_td': 1,
            'dst_pts_allowed': 14
        }
        
        expected = (2 * 1.0) + (1 * 2.0) + (1 * 2.0) + (1 * 6.0) + 1.0
        # 2.0 + 2.0 + 2.0 + 6.0 + 1.0 = 13.0
        
        total = sum(standard.get_score(stat, value) for stat, value in stats.items())
        assert total == 13.0