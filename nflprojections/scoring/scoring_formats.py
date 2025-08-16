from dataclasses import dataclass, field
from typing import Optional, Dict, Tuple


@dataclass
class ScoringFormat:
    # Required fields
    pass_yd: float
    pass_td: float
    pass_int: float
    rush_yd: float
    rush_td: float
    rec: float
    rec_yd: float
    rec_td: float
    fumble_lost: float
    two_pt: float

    # Optional fields
    xp: Optional[float] = None
    dst_td: Optional[float] = None
    dst_int: Optional[float] = None
    dst_fumble_rec: Optional[float] = None
    dst_sack: Optional[float] = None
    dst_safety: Optional[float] = None
    dst_block: Optional[float] = None
    dst_ret_td: Optional[float] = None
    dst_pts_allowed: Optional[Dict[int, float]] = field(default_factory=dict)

    # Bonus scoring rules
    bonuses: Dict[Tuple[str, int], float] = field(default_factory=dict)

    def get_score(self, stat: str, value: float) -> float:
        score = 0.0

        # Regular scoring
        if stat == 'dst_pts_allowed' and self.dst_pts_allowed:
            thresholds = sorted(self.dst_pts_allowed.keys())
            for threshold in reversed(thresholds):
                if value >= threshold:
                    score += self.dst_pts_allowed[threshold]
                    break
        else:
            score += getattr(self, stat, 0.0) * value

        # Bonus scoring
        for (bonus_stat, threshold), bonus_value in self.bonuses.items():
            if stat == bonus_stat and value >= threshold:
                score += bonus_value

        return score


@dataclass
class StandardScoring(ScoringFormat):
    pass_yd: float = 0.04
    pass_td: float = 4.0
    pass_int: float = -2.0
    rush_yd: float = 0.1
    rush_td: float = 6.0
    rec: float = 0.0
    rec_yd: float = 0.1
    rec_td: float = 6.0
    fumble_lost: float = -2.0
    two_pt: float = 2.0

    xp: float = 1.0
    dst_td: float = 6.0
    dst_int: float = 2.0
    dst_fumble_rec: float = 2.0
    dst_sack: float = 1.0
    dst_safety: float = 2.0
    dst_block: float = 2.0
    dst_ret_td: float = 6.0
    dst_pts_allowed: Dict[int, float] = field(default_factory=lambda: {
        0: 10.0, 1: 7.0, 7: 4.0, 14: 1.0, 21: 0.0, 28: -1.0, 35: -4.0
    })


@dataclass
class HalfPPRScoring(ScoringFormat):
    pass_yd: float = 0.04
    pass_td: float = 4.0
    pass_int: float = -2.0
    rush_yd: float = 0.1
    rush_td: float = 6.0
    rec: float = 0.5
    rec_yd: float = 0.1
    rec_td: float = 6.0
    fumble_lost: float = -2.0
    two_pt: float = 2.0

    xp: float = 1.0
    dst_td: float = 6.0
    dst_int: float = 2.0
    dst_fumble_rec: float = 2.0
    dst_sack: float = 1.0
    dst_safety: float = 2.0
    dst_block: float = 2.0
    dst_ret_td: float = 6.0
    dst_pts_allowed: Dict[int, float] = field(default_factory=lambda: {
        0: 10.0, 1: 7.0, 7: 4.0, 14: 1.0, 21: 0.0, 28: -1.0, 35: -4.0
    })


@dataclass
class PPRScoring(ScoringFormat):
    pass_yd: float = 0.04
    pass_td: float = 4.0
    pass_int: float = -2.0
    rush_yd: float = 0.1
    rush_td: float = 6.0
    rec: float = 1.0
    rec_yd: float = 0.1
    rec_td: float = 6.0
    fumble_lost: float = -2.0
    two_pt: float = 2.0

    xp: float = 1.0
    dst_td: float = 6.0
    dst_int: float = 2.0
    dst_fumble_rec: float = 2.0
    dst_sack: float = 1.0
    dst_safety: float = 2.0
    dst_block: float = 2.0
    dst_ret_td: float = 6.0
    dst_pts_allowed: Dict[int, float] = field(default_factory=lambda: {
        0: 10.0, 1: 7.0, 7: 4.0, 14: 1.0, 21: 0.0, 28: -1.0, 35: -4.0
    })


@dataclass
class DraftKingsScoring(ScoringFormat):
    pass_yd: float = 0.04
    pass_td: float = 4.0
    pass_int: float = -1.0
    rush_yd: float = 0.1
    rush_td: float = 6.0
    rec: float = 1.0
    rec_yd: float = 0.1
    rec_td: float = 6.0
    fumble_lost: float = -1.0
    two_pt: float = 2.0

    dst_td: float = 6.0
    dst_int: float = 2.0
    dst_fumble_rec: float = 2.0
    dst_sack: float = 1.0
    dst_safety: float = 2.0
    dst_block: float = 2.0
    dst_ret_td: float = 6.0
    dst_pts_allowed: Dict[int, float] = field(default_factory=lambda: {
        0: 10.0, 1: 7.0, 7: 4.0, 14: 1.0, 21: 0.0, 28: -1.0, 35: -4.0
    })

    bonuses: Dict[Tuple[str, int], float] = field(default_factory=lambda: {
        ('pass_yd', 300): 3.0,
        ('rush_yd', 100): 3.0,
        ('rec_yd', 100): 3.0
    })


@dataclass
class FanDuelScoring(ScoringFormat):
    pass_yd: float = 0.04
    pass_td: float = 4.0
    pass_int: float = -1.0
    rush_yd: float = 0.1
    rush_td: float = 6.0
    rec: float = 0.5
    rec_yd: float = 0.1
    rec_td: float = 6.0
    fumble_lost: float = -2.0
    two_pt: float = 2.0

    xp: float = 1.0
    dst_td: float = 6.0
    dst_int: float = 2.0
    dst_fumble_rec: float = 2.0
    dst_sack: float = 1.0
    dst_safety: float = 2.0
    dst_block: float = 2.0
    dst_ret_td: float = 6.0
    dst_pts_allowed: Dict[int, float] = field(default_factory=lambda: {
        0: 10.0, 1: 7.0, 7: 4.0, 14: 1.0, 21: 0.0, 28: -1.0, 35: -4.0
    })


@dataclass
class YahooScoring(ScoringFormat):
    pass_yd: float = 0.04
    pass_td: float = 4.0
    pass_int: float = -1.0
    rush_yd: float = 0.1
    rush_td: float = 6.0
    rec: float = 0.5
    rec_yd: float = 0.1
    rec_td: float = 6.0
    fumble_lost: float = -2.0
    two_pt: float = 2.0

    xp: float = 1.0
    dst_td: float = 6.0
    dst_int: float = 2.0
    dst_fumble_rec: float = 2.0
    dst_sack: float = 1.0
    dst_safety: float = 2.0
    dst_block: float = 2.0
    dst_ret_td: float = 6.0
    dst_pts_allowed: Dict[int, float] = field(default_factory=lambda: {
        0: 10.0, 1: 7.0, 7: 4.0, 14: 1.0, 21: 0.0, 28: -1.0, 35: -4.0
    })


@dataclass
class HomeAuctionScoring(ScoringFormat):
    pass_yd: float = 0.04
    pass_td: float = 4.0
    pass_int: float = -1.0
    rush_yd: float = 0.1
    rush_td: float = 6.0
    rec: float = 1.0
    rec_yd: float = 0.1
    rec_td: float = 6.0
    fumble_lost: float = -1.0
    two_pt: float = 2.0

    dst_td: float = 6.0
    dst_int: float = 2.0
    dst_fumble_rec: float = 2.0
    dst_sack: float = 1.0
    dst_safety: float = 2.0
    dst_block: float = 2.0
    dst_ret_td: float = 6.0
    dst_pts_allowed: Dict[int, float] = field(default_factory=lambda: {
        0: 10.0, 1: 7.0, 7: 4.0, 14: 1.0, 21: 0.0, 28: -1.0, 35: -4.0
    })

    bonuses: Dict[Tuple[str, int], float] = field(default_factory=lambda: {
        ('pass_yd', 300): 5.0,
        ('rush_yd', 100): 5.0,
        ('rec_yd', 100): 5.0
    })