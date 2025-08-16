# nflprojections/espn_parser.py
# -*- coding: utf-8 -*-
# Copyright (C) 2025 Eric Truett
# Licensed under the MIT License

"""
ESPN API specific parser implementation
"""

import logging
from typing import Dict, List, Any

from .base_parser import JSONParser


logger = logging.getLogger(__name__)


class ESPNParser(JSONParser):
    """Parser specifically for ESPN fantasy projections JSON"""
    
    POSITION_MAP = {
        1: "QB",
        2: "RB",
        3: "WR",
        4: "TE",
        5: "K",
        16: "DST",
    }

    STAT_MAP = {
        "0": "pass_att",
        "1": "pass_cmp",
        "3": "pass_yds",
        "4": "pass_td",
        "19": "pass_tpc",
        "20": "pass_int",
        "23": "rush_att",
        "24": "rush_yds",
        "25": "rush_td",
        "26": "rush_tpc",
        "53": "rec_rec",
        "42": "rec_yds",
        "43": "rec_td",
        "44": "rec_tpc",
        "58": "rec_tar",
        "72": "fum_lost",
        "74": "madeFieldGoalsFrom50Plus",
        "77": "madeFieldGoalsFrom40To49",
        "80": "madeFieldGoalsFromUnder40",
        "85": "missedFieldGoals",
        "86": "madeExtraPoints",
        "88": "missedExtraPoints",
        "89": "defensive0PointsAllowed",
        "90": "defensive1To6PointsAllowed",
        "91": "defensive7To13PointsAllowed",
        "92": "defensive14To17PointsAllowed",
        "93": "defensiveBlockedKickForTouchdowns",
        "95": "defensiveInterceptions",
        "96": "defensiveFumbles",
        "97": "defensiveBlockedKicks",
        "98": "defensiveSafeties",
        "99": "defensiveSacks",
        "101": "kickoffReturnTouchdown",
        "102": "puntReturnTouchdown",
        "103": "fumbleReturnTouchdown",
        "104": "interceptionReturnTouchdown",
        "123": "defensive28To34PointsAllowed",
        "124": "defensive35To45PointsAllowed",
        "129": "defensive100To199YardsAllowed",
        "130": "defensive200To299YardsAllowed",
        "132": "defensive350To399YardsAllowed",
        "133": "defensive400To449YardsAllowed",
        "134": "defensive450To499YardsAllowed",
        "135": "defensive500To549YardsAllowed",
        "136": "defensiveOver550YardsAllowed",
    }

    TEAM_MAP = {
        "ARI": 22,
        "ATL": 1,
        "BAL": 33,
        "BUF": 2,
        "CAR": 29,
        "CHI": 3,
        "CIN": 4,
        "CLE": 5,
        "DAL": 6,
        "DEN": 7,
        "DET": 8,
        "GB": 9,
        "HOU": 34,
        "IND": 11,
        "JAC": 30,
        "JAX": 30,
        "KC": 12,
        "LAC": 24,
        "LA": 14,
        "LAR": 14,
        "MIA": 15,
        "MIN": 16,
        "NE": 17,
        "NO": 18,
        "NYG": 19,
        "NYJ": 20,
        "OAK": 13,
        "PHI": 21,
        "PIT": 23,
        "SEA": 26,
        "SF": 25,
        "TB": 27,
        "TEN": 10,
        "WAS": 28,
        "WSH": 28,
        "FA": 0,
    }

    TEAM_ID_MAP = {v: k for k, v in TEAM_MAP.items()}

    def __init__(self, season: int = 2025, week: int = None, **kwargs):
        """
        Initialize ESPN parser
        
        Args:
            season: NFL season year
            week: NFL week (for weekly projections, None for season)
            **kwargs: Additional configuration
        """
        super().__init__(source_name="espn", **kwargs)
        self.season = season
        self.week = week

    def parse_raw_data(self, raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse ESPN API JSON response into list of dictionaries
        
        Args:
            raw_data: ESPN API JSON response
            
        Returns:
            List of dictionaries with parsed player projection data
        """
        if not isinstance(raw_data, dict):
            logger.error("ESPN raw data must be a dictionary")
            return []
        
        if "players" not in raw_data:
            logger.error("No 'players' key found in ESPN response")
            return []
        
        # Use weekly projections if week is specified, otherwise seasonal
        if self.week is not None:
            return self._parse_weekly_projections(raw_data)
        else:
            return self._parse_seasonal_projections(raw_data)

    def _parse_seasonal_projections(self, content: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse seasonal projections from ESPN data"""
        projections = []

        top_level_keys = {
            "id": "source_player_id",
            "fullName": "source_player_name",
            "proTeamId": "source_team_id",
        }

        for player_item in content["players"]:
            player = player_item["player"]
            p = {
                top_level_keys.get(k): v
                for k, v in player.items()
                if k in top_level_keys
            }

            p["source_team_code"] = self._espn_team(team_id=p.get("source_team_id", 0))
            p['source_player_position'] = self.POSITION_MAP.get(int(player['defaultPositionId']))

            # Add season and week for standardization
            p['season'] = self.season
            p['week'] = self.week

            # Find seasonal projection
            stat = self._find_projection(player["stats"])
            if stat:
                p["source_player_projection"] = stat["appliedTotal"]
                p.update(self._parse_stats(stat["stats"]))
            else:
                p["source_player_projection"] = None
            
            projections.append(p)
        
        return projections

    def _parse_weekly_projections(self, content: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse weekly projections from ESPN data"""
        projections = []

        top_level_keys = {
            "id": "source_player_id",
            "fullName": "source_player_name",
            "proTeamId": "source_team_id",
            "defaultPositionId": "source_player_position"
        }

        for player_item in content["players"]:
            player = player_item["player"]
            p = {
                top_level_keys.get(k): v
                for k, v in player.items()
                if k in top_level_keys
            }

            p["source_team_code"] = self._espn_team(team_id=p.get("source_team_id", 0))
            p["source_player_position"] = self.POSITION_MAP.get(p["source_player_position"], "UNK")

            # Add season and week for standardization
            p['season'] = self.season
            p['week'] = self.week

            # Find weekly projection
            try:
                stat = self._find_projection(player["stats"])
                if stat:
                    p["source_player_projection"] = stat["appliedTotal"]
                    p.update(self._parse_stats(stat["stats"]))
                else:
                    p["source_player_projection"] = None
            except KeyError:
                p["source_player_projection"] = None
            
            projections.append(p)
        
        return projections

    def _find_projection(self, stats: List[Dict]) -> Dict:
        """Find projection or result for the specified season and week"""
        mapping = {
            "seasonId": self.season,
            "scoringPeriodId": self.week or 0,
            "statSourceId": 1,
            "statSplitTypeId": 0
        }

        for item in stats:
            if {k: item.get(k) for k in mapping} == mapping:
                return item
        return None

    def _parse_stats(self, stat: Dict[str, Any]) -> Dict[str, float]:
        """Parse stats dictionary into meaningful stat names"""
        return {
            self.STAT_MAP.get(str(k)): float(v)
            for k, v in stat.items()
            if str(k) in self.STAT_MAP
        }

    def _espn_team(self, team_code: str = None, team_id: int = None) -> str:
        """Convert between ESPN team codes and team IDs"""
        if team_code:
            return self.TEAM_MAP.get(team_code)
        return self.TEAM_ID_MAP.get(int(team_id)) if team_id else None

    def validate_parsed_data(self, data: List[Dict[str, Any]]) -> bool:
        """
        Validate that parsed ESPN data has expected structure
        
        Args:
            data: Parsed data as list of dictionaries
            
        Returns:
            True if data is valid, False otherwise
        """
        if not data or not isinstance(data, list):
            return False
        
        # Check first item has expected keys
        if not isinstance(data[0], dict):
            return False
        
        required_keys = {"source_player_name", "source_player_position", "source_team_code"}
        return all(key in data[0] for key in required_keys)