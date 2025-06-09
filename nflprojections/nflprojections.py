# nflprojections/nflprojections/nflprojections.py
# -*- coding: utf-8 -*-
# Copyright (C) 2020 Eric Truett
# Licensed under the MIT License

import logging
from pathlib import Path
import re
from typing import Dict, List, Optional, Union

import numpy as np
import pandas as pd

import nflnames
import nflschedule


Standardized = Union[List[str], pd.Series]





class ProjectionSource:

    REQUIRED_MAPPED_COLUMNS = {'season', 'week', 'plyr', 'pos', 'team', 'proj'}
    VALID_SCORING_FORMATS = {'dk', 'fd', 'yh', 'ppr', 'half_ppr', 'std', 'yhcustom'}
    VALID_SLATE_NAMES = {'main', 'early', 'late', 'all', 'tsd', 'ssd', 'msd', 'season', 'playoffs', 'bestball'}
    VALID_FORMATS = {'csv', 'json', 'pkl', 'parquet'}

    projections_name = 'base'

    def __init__(self, 
                 rawdir: Path, 
                 procdir: Path, 
                 column_mapping: Dict[str, str], 
                 scoring_format: str, 
                 projections_source: str,
                 season: int, 
                 week: int, 
                 slate_name: str, 
                 raw_format: str = 'csv', 
                 processed_format: str = 'csv',
                 ):
        """Base ProjectionSource object
        
        Args:
            rawdir (Path): the directory for raw files
            procdir (Path): the directory for processed files
            column_mapping (Dict[str, str]): maps to required mapped columns
            season (int): the season, e.g. 2021
            week (int): the week (use 0 for full-season)
            site_name (str): anything in VALID_SITE_NAMES
            slate_name (str): anything in VALID_SLATE_NAMES
            raw_format (str): anything in VALID_FORMATS
            processed_format (str): anything in VALID_FORMATS

        Returns:
            ProjectionSource

        """
        self.rawdir = rawdir
        self.procdir = procdir
        self.season = season if season else nflschedule.current_season()
        self.week = week if week else nflschedule.current_week()
        self.scoring_format = scoring_format
        self.projections_source = projections_source
        self.slate_name = slate_name
        
        # validate column mappings
        assert self.REQUIRED_MAPPED_COLUMNS.issubset(set(column_mapping.values()))
        self.column_mapping = column_mapping

        # validate formats
        if raw_format not in self.VALID_FORMATS:
            raise ValueError(f'Invalid raw format: {raw_format}')
        self.raw_format = raw_format

        if processed_format not in self.VALID_FORMATS:
            raise ValueError(f'Invalid processed format: {processed_format}')
        self.processed_format = processed_format

    @property
    def processed_fn(self) -> Path:
        """Filename always has season/week/projections/site/slate name
        
        Examples:
            2020_w8_rg-core_dk_main.csv

        """
        parts = [str(self.season), f'w{self.week}', self.projections_soure, self.scoring_format, self.slate_name]
        return self.procdir / f'{"_".join([str(item) for item in parts])}.{self.processed_format}' 

    @property
    def raw_fn(self) -> Path:
        """Filename always has season/week/projections/site/slate
        
        Examples:
            2020_w8_rg-core_dk_main.html

        """
        parts = [str(self.season), f'w{self.week}', self.projections_name, self.site_name, self.slate_name]
        return self.rawdir / f'raw/{"_".join([str(item) for item in parts])}.{self.raw_format}'

    def load_raw(self) -> pd.DataFrame:
        """Loads raw projections file"""
        raise NotImplementedError 
        
    def process_raw(self) -> pd.DataFrame:
        raise NotImplementedError

    def remap_columns(self, cols: List[str]) -> List[str]:
        return [self.column_mapping.get(c, c) for c in cols]                        

    def standardize(self) -> pd.DataFrame:
        raise NotImplementedError

    def standardize_players(self, names: Standardized) -> Standardized:
        """Standardizes player names"""
        if isinstance(names, (list, tuple, set)):
            return [nflnames.standardize_player_name(n) for n in names]
        return names.apply(nflnames.standardize_player_name)

    def standardize_positions(self, positions: Standardized) -> Standardized:
        """Standardizes player positions"""
        if isinstance(positions, (list, tuple, set)):
            return [nflnames.standardize_positions(pos) for pos in positions]
        return positions.apply(nflnames.standardize_positions)

    def standardize_teams(self, teams: Standardized) -> Standardized:
        """Standardizes team names"""
        if isinstance(teams, (list, tuple, set)):
            return [nflnames.standardize_team_code(t) for t in teams]
        return teams.apply(nflnames.standardize_team_code)
              

class ScoringFormats:
    """Class for converting raw NFL statistics to fantasy points.
    
    This class provides methods to convert raw NFL statistics (yards, catches, TDs, etc.)
    to fantasy points based on different scoring formats used by various fantasy platforms.
    """
    
    # Standard scoring format definitions
    SCORING_FORMATS = {
        # Standard (non-PPR) scoring
        'std': {
            'pass_yd': 0.04,      # 1 point per 25 passing yards
            'pass_td': 4.0,       # 4 points per passing TD
            'pass_int': -2.0,     # -2 points per interception
            'rush_yd': 0.1,       # 1 point per 10 rushing yards
            'rush_td': 6.0,       # 6 points per rushing TD
            'rec': 0.0,           # 0 points per reception
            'rec_yd': 0.1,        # 1 point per 10 receiving yards
            'rec_td': 6.0,        # 6 points per receiving TD
            'fumble_lost': -2.0,  # -2 points per fumble lost
            'two_pt': 2.0,        # 2 points per 2-point conversion
            'fg': 3.0,            # 3 points per field goal
            'fg_50_plus': 5.0,    # 5 points per 50+ yard field goal
            'xp': 1.0,            # 1 point per extra point
            'dst_td': 6.0,        # 6 points per DST TD
            'dst_int': 2.0,       # 2 points per interception
            'dst_fumble_rec': 2.0,# 2 points per fumble recovery
            'dst_sack': 1.0,      # 1 point per sack
            'dst_safety': 2.0,    # 2 points per safety
            'dst_block': 2.0,     # 2 points per blocked kick
            'dst_ret_td': 6.0,    # 6 points per return TD
            'dst_pts_allowed': {  # Points based on points allowed
                0: 10.0,          # 10 points for shutout
                1: 7.0,           # 7 points for 1-6 points allowed
                7: 4.0,           # 4 points for 7-13 points allowed
                14: 1.0,          # 1 point for 14-20 points allowed
                21: 0.0,          # 0 points for 21-27 points allowed
                28: -1.0,         # -1 point for 28-34 points allowed
                35: -4.0          # -4 points for 35+ points allowed
            }
        },
        
        # Half-PPR scoring
        'half_ppr': {
            'pass_yd': 0.04,
            'pass_td': 4.0,
            'pass_int': -2.0,
            'rush_yd': 0.1,
            'rush_td': 6.0,
            'rec': 0.5,           # 0.5 points per reception
            'rec_yd': 0.1,
            'rec_td': 6.0,
            'fumble_lost': -2.0,
            'two_pt': 2.0,
            'fg': 3.0,
            'fg_50_plus': 5.0,
            'xp': 1.0,
            'dst_td': 6.0,
            'dst_int': 2.0,
            'dst_fumble_rec': 2.0,
            'dst_sack': 1.0,
            'dst_safety': 2.0,
            'dst_block': 2.0,
            'dst_ret_td': 6.0,
            'dst_pts_allowed': {
                0: 10.0,
                1: 7.0,
                7: 4.0,
                14: 1.0,
                21: 0.0,
                28: -1.0,
                35: -4.0
            }
        },
        
        # Full PPR scoring
        'ppr': {
            'pass_yd': 0.04,
            'pass_td': 4.0,
            'pass_int': -2.0,
            'rush_yd': 0.1,
            'rush_td': 6.0,
            'rec': 1.0,           # 1 point per reception
            'rec_yd': 0.1,
            'rec_td': 6.0,
            'fumble_lost': -2.0,
            'two_pt': 2.0,
            'fg': 3.0,
            'fg_50_plus': 5.0,
            'xp': 1.0,
            'dst_td': 6.0,
            'dst_int': 2.0,
            'dst_fumble_rec': 2.0,
            'dst_sack': 1.0,
            'dst_safety': 2.0,
            'dst_block': 2.0,
            'dst_ret_td': 6.0,
            'dst_pts_allowed': {
                0: 10.0,
                1: 7.0,
                7: 4.0,
                14: 1.0,
                21: 0.0,
                28: -1.0,
                35: -4.0
            }
        },
        
        # DraftKings scoring
        'dk': {
            'pass_yd': 0.04,
            'pass_td': 4.0,
            'pass_int': -1.0,     # -1 point per interception
            'pass_300_bonus': 3.0,# 3 point bonus for 300+ passing yards
            'rush_yd': 0.1,
            'rush_td': 6.0,
            'rush_100_bonus': 3.0,# 3 point bonus for 100+ rushing yards
            'rec': 1.0,           # 1 point per reception
            'rec_yd': 0.1,
            'rec_td': 6.0,
            'rec_100_bonus': 3.0, # 3 point bonus for 100+ receiving yards
            'fumble_lost': -1.0,  # -1 point per fumble lost
            'two_pt': 2.0,
            'dst_td': 6.0,
            'dst_int': 2.0,
            'dst_fumble_rec': 2.0,
            'dst_sack': 1.0,
            'dst_safety': 2.0,
            'dst_block': 2.0,
            'dst_ret_td': 6.0,
            'dst_pts_allowed': {
                0: 10.0,
                1: 7.0,
                7: 4.0,
                14: 1.0,
                21: 0.0,
                28: -1.0,
                35: -4.0
            }
        },
        
        # FanDuel scoring
        'fd': {
            'pass_yd': 0.04,
            'pass_td': 4.0,
            'pass_int': -1.0,
            'rush_yd': 0.1,
            'rush_td': 6.0,
            'rec': 0.5,           # 0.5 points per reception
            'rec_yd': 0.1,
            'rec_td': 6.0,
            'fumble_lost': -2.0,
            'two_pt': 2.0,
            'fg_0_39': 3.0,       # 3 points for FGs 0-39 yards
            'fg_40_49': 4.0,      # 4 points for FGs 40-49 yards
            'fg_50_plus': 5.0,    # 5 points for FGs 50+ yards
            'xp': 1.0,
            'dst_td': 6.0,
            'dst_int': 2.0,
            'dst_fumble_rec': 2.0,
            'dst_sack': 1.0,
            'dst_safety': 2.0,
            'dst_block': 2.0,
            'dst_ret_td': 6.0,
            'dst_pts_allowed': {
                0: 10.0,
                1: 7.0,
                7: 4.0,
                14: 1.0,
                21: 0.0,
                28: -1.0,
                35: -4.0
            }
        },
        
        # Yahoo scoring
        'yh': {
            'pass_yd': 0.04,
            'pass_td': 4.0,
            'pass_int': -1.0,
            'rush_yd': 0.1,
            'rush_td': 6.0,
            'rec': 0.5,           # 0.5 points per reception
            'rec_yd': 0.1,
            'rec_td': 6.0,
            'fumble_lost': -2.0,
            'two_pt': 2.0,
            'fg_0_39': 3.0,
            'fg_40_49': 4.0,
            'fg_50_plus': 5.0,
            'xp': 1.0,
            'dst_td': 6.0,
            'dst_int': 2.0,
            'dst_fumble_rec': 2.0,
            'dst_sack': 1.0,
            'dst_safety': 2.0,
            'dst_block': 2.0,
            'dst_ret_td': 6.0,
            'dst_pts_allowed': {
                0: 10.0,
                1: 7.0,
                7: 4.0,
                14: 1.0,
                21: 0.0,
                28: -1.0,
                35: -4.0
            }
        }
    }
    
    def __init__(self, scoring_format: str = 'ppr', custom_scoring: Optional[Dict] = None):
        """Initialize ScoringFormats with a specific scoring format.
        
        Args:
            scoring_format (str): The scoring format to use. Must be one of:
                'std' (Standard), 'half_ppr' (Half PPR), 'ppr' (Full PPR),
                'dk' (DraftKings), 'fd' (FanDuel), 'yh' (Yahoo), or 'custom'.
            custom_scoring (Optional[Dict]): A dictionary defining custom scoring rules.
                Required if scoring_format is 'custom'.
                
        Raises:
            ValueError: If an invalid scoring_format is provided or if custom_scoring
                is not provided when scoring_format is 'custom'.
        """
        if scoring_format not in self.SCORING_FORMATS and scoring_format != 'custom':
            raise ValueError(f"Invalid scoring format: {scoring_format}. "
                            f"Must be one of: {', '.join(self.SCORING_FORMATS.keys())} or 'custom'.")
        
        if scoring_format == 'custom' and custom_scoring is None:
            raise ValueError("Custom scoring format requires a custom_scoring dictionary.")
        
        self.scoring_format = scoring_format
        
        if scoring_format == 'custom':
            self.scoring_rules = custom_scoring
        else:
            self.scoring_rules = self.SCORING_FORMATS[scoring_format]
    
    def calculate_fantasy_points(self, stats: Dict[str, Union[int, float]]) -> float:
        """Calculate fantasy points based on provided statistics.
        
        Args:
            stats (Dict[str, Union[int, float]]): Dictionary of player statistics.
                Keys should match the scoring rule keys.
                
        Returns:
            float: The calculated fantasy points.
            
        Example:
            >>> scoring = ScoringFormats('ppr')
            >>> stats = {
            ...     'pass_yd': 250,
            ...     'pass_td': 2,
            ...     'rush_yd': 30,
            ...     'rec': 5,
            ...     'rec_yd': 60,
            ...     'rec_td': 1
            ... }
            >>> scoring.calculate_fantasy_points(stats)
            30.0
        """
        points = 0.0
        
        for stat, value in stats.items():
            if stat in self.scoring_rules:
                # Handle special case for points allowed
                if stat == 'dst_pts_allowed' and isinstance(self.scoring_rules[stat], dict):
                    # Find the highest threshold that's less than or equal to the points allowed
                    thresholds = sorted(self.scoring_rules[stat].keys())
                    for threshold in reversed(thresholds):
                        if value >= threshold:
                            points += self.scoring_rules[stat][threshold]
                            break
                else:
                    points += value * self.scoring_rules[stat]
            
            # Handle yardage bonuses for DraftKings
            if self.scoring_format == 'dk' or (self.scoring_format == 'custom' and 'pass_300_bonus' in self.scoring_rules):
                if stat == 'pass_yd' and value >= 300:
                    points += self.scoring_rules.get('pass_300_bonus', 0)
                if stat == 'rush_yd' and value >= 100:
                    points += self.scoring_rules.get('rush_100_bonus', 0)
                if stat == 'rec_yd' and value >= 100:
                    points += self.scoring_rules.get('rec_100_bonus', 0)
            
            # Handle field goal distance tiers
            if stat == 'fg_distances' and isinstance(value, list):
                for distance in value:
                    if distance >= 50 and 'fg_50_plus' in self.scoring_rules:
                        points += self.scoring_rules['fg_50_plus']
                    elif 40 <= distance < 50 and 'fg_40_49' in self.scoring_rules:
                        points += self.scoring_rules['fg_40_49']
                    elif 'fg_0_39' in self.scoring_rules:
                        points += self.scoring_rules['fg_0_39']
                    elif 'fg' in self.scoring_rules:
                        points += self.scoring_rules['fg']
        
        return points
    
    def convert_dataframe(self, df: pd.DataFrame, stat_columns: Dict[str, str]) -> pd.DataFrame:
        """Convert a DataFrame of raw statistics to fantasy points.
        
        Args:
            df (pd.DataFrame): DataFrame containing raw statistics.
            stat_columns (Dict[str, str]): Mapping from scoring rule keys to DataFrame column names.
                
        Returns:
            pd.DataFrame: The input DataFrame with an additional 'fantasy_points' column.
            
        Example:
            >>> scoring = ScoringFormats('ppr')
            >>> df = pd.DataFrame({
            ...     'player': ['Tom Brady', 'Derrick Henry'],
            ...     'passing_yards': [300, 0],
            ...     'passing_tds': [3, 0],
            ...     'rushing_yards': [10, 150],
            ...     'rushing_tds': [0, 2],
            ...     'receptions': [0, 2],
            ...     'receiving_yards': [0, 20],
            ... })
            >>> stat_columns = {
            ...     'pass_yd': 'passing_yards',
            ...     'pass_td': 'passing_tds',
            ...     'rush_yd': 'rushing_yards',
            ...     'rush_td': 'rushing_tds',
            ...     'rec': 'receptions',
            ...     'rec_yd': 'receiving_yards',
            ... }
            >>> scoring.convert_dataframe(df, stat_columns)
        """
        # Create a copy of the DataFrame to avoid modifying the original
        result_df = df.copy()
        
        # Calculate fantasy points for each row
        fantasy_points = []
        
        for _, row in df.iterrows():
            # Create a stats dictionary for this player
            stats = {}
            for scoring_key, df_column in stat_columns.items():
                if df_column in row:
                    stats[scoring_key] = row[df_column]
            
            # Calculate fantasy points
            points = self.calculate_fantasy_points(stats)
            fantasy_points.append(points)
        
        # Add fantasy points to the result DataFrame
        result_df['fantasy_points'] = fantasy_points
        
        return result_df
    
    def get_scoring_rules(self) -> Dict:
        """Get the current scoring rules.
        
        Returns:
            Dict: The current scoring rules.
        """
        return self.scoring_rules
    
    def set_custom_scoring_rule(self, stat: str, value: Union[float, Dict]) -> None:
        """Set or update a custom scoring rule.
        
        Args:
            stat (str): The statistic to set a rule for.
            value (Union[float, Dict]): The point value or dictionary of point values.
            
        Example:
            >>> scoring = ScoringFormats('ppr')
            >>> scoring.set_custom_scoring_rule('rec', 0.75)  # Change PPR to 0.75 points per reception
        """
        # Create a copy of the current scoring rules
        if self.scoring_format != 'custom':
            self.scoring_rules = self.SCORING_FORMATS[self.scoring_format].copy()
            self.scoring_format = 'custom'
        
        # Update the scoring rule
        self.scoring_rules[stat] = value


class ProjectionCombiner:

    def __init__(self):
        """Need to document all of the parameters"""
        pass
