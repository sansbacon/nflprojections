# nflprojections/base_standardizer.py
# -*- coding: utf-8 -*-
# Copyright (C) 2025 Eric Truett
# Licensed under the MIT License

"""
Base classes for standardizing data formats across different sources
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Union, Optional, Callable
import pandas as pd


class DataStandardizer(ABC):
    """Abstract base class for standardizing data across different sources"""
    
    # Standard column names that all sources should map to
    REQUIRED_COLUMNS = {'season', 'week', 'plyr', 'pos', 'team', 'proj'}
    
    def __init__(self, column_mapping: Dict[str, str]):
        """
        Initialize the data standardizer
        
        Args:
            column_mapping: Mapping from source columns to standard columns
        """
        # Validate that all required columns are mapped
        mapped_columns = set(column_mapping.values())
        if not self.REQUIRED_COLUMNS.issubset(mapped_columns):
            missing = self.REQUIRED_COLUMNS - mapped_columns
            raise ValueError(f"Column mapping missing required columns: {missing}")
            
        self.column_mapping = column_mapping
    
    @abstractmethod
    def standardize(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize a DataFrame to common format
        
        Args:
            df: DataFrame with source-specific columns
            
        Returns:
            DataFrame with standardized columns and values
        """
        pass
    
    def remap_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Remap columns from source format to standardized format
        
        Args:
            df: DataFrame with source columns
            
        Returns:
            DataFrame with standardized column names
        """
        return df.rename(columns=self.column_mapping)
    
    def standardize_players(self, names: Union[List[str], pd.Series], standardize_player_name: Optional[Callable[[str], str]] = None) -> Union[List[str], pd.Series]:
        """
        Standardize player names using provided function
        Args:
            names: Player names to standardize
            standardize_player_name: Function to standardize a player name
        Returns:
            Standardized player names
        """
        if standardize_player_name is None:
            return names
        if isinstance(names, (list, tuple, set)):
            return [standardize_player_name(n) for n in names]
        return names.apply(standardize_player_name)

    def standardize_positions(self, positions: Union[List[str], pd.Series], standardize_position: Optional[Callable[[str], str]] = None) -> Union[List[str], pd.Series]:
        """
        Standardize position names using provided function
        Args:
            positions: Position names to standardize
            standardize_position: Function to standardize a position
        Returns:
            Standardized position names
        """
        if standardize_position is None:
            return positions
        if isinstance(positions, (list, tuple, set)):
            return [standardize_position(pos) for pos in positions]
        return positions.apply(standardize_position)

    def standardize_teams(self, teams: Union[List[str], pd.Series], standardize_team_code: Optional[Callable[[str], str]] = None) -> Union[List[str], pd.Series]:
        """
        Standardize team names/codes using provided function
        Args:
            teams: Team names/codes to standardize
            standardize_team_code: Function to standardize a team code
        Returns:
            Standardized team codes
        """
        if standardize_team_code is None:
            return teams
        if isinstance(teams, (list, tuple, set)):
            return [standardize_team_code(t) for t in teams]
        return teams.apply(standardize_team_code)


class ProjectionStandardizer(DataStandardizer):
    """Standardizer specifically for NFL projection data"""
    
    def __init__(
        self,
        column_mapping: Dict[str, str],
        season: Optional[int] = None,
        week: Optional[int] = None
    ):
        """
        Initialize projection standardizer
        Args:
            column_mapping: Mapping from source columns to standard columns
            season: Season to add if not present in data
            week: Week to add if not present in data
        """
        super().__init__(column_mapping)
        self.season = season
        self.week = week
    
    def standardize(
        self,
        df: pd.DataFrame,
        standardize_player_name: Optional[Callable[[str], str]] = None,
        standardize_position: Optional[Callable[[str], str]] = None,
        standardize_team_code: Optional[Callable[[str], str]] = None
    ) -> pd.DataFrame:
        """
        Standardize projection DataFrame to common format
        
        Args:
            df: DataFrame with source-specific columns
            standardize_player_name: Function to standardize player names
            standardize_position: Function to standardize positions
            standardize_team_code: Function to standardize team codes
        Returns:
            DataFrame with standardized columns and values
        """
        if df.empty:
            return df
        
        # First remap columns
        df = self.remap_columns(df)
        
        # Standardize data using provided functions
        if 'plyr' in df.columns:
            df['plyr'] = self.standardize_players(df['plyr'], standardize_player_name)
        if 'pos' in df.columns:
            df['pos'] = self.standardize_positions(df['pos'], standardize_position)
        if 'team' in df.columns:
            df['team'] = self.standardize_teams(df['team'], standardize_team_code)
            
        # Ensure required columns exist
        for col in self.REQUIRED_COLUMNS:
            if col not in df.columns:
                if col == 'season' and self.season is not None:
                    df[col] = self.season
                elif col == 'week' and self.week is not None:
                    df[col] = self.week
                else:
                    df[col] = None
        
        return df


class StatStandardizer(DataStandardizer):
    """Standardizer for NFL statistical data"""
    
    # Standard statistical columns
    STAT_COLUMNS = {
        'pass_att', 'pass_comp', 'pass_yd', 'pass_td', 'pass_int',
        'rush_att', 'rush_yd', 'rush_td', 'rec', 'rec_yd', 'rec_td',
        'fumble_lost', 'two_pt', 'xp', 'fg_att', 'fg_made'
    }
    
    def standardize(
        self,
        df: pd.DataFrame,
        standardize_player_name: Optional[Callable[[str], str]] = None,
        standardize_position: Optional[Callable[[str], str]] = None,
        standardize_team_code: Optional[Callable[[str], str]] = None
    ) -> pd.DataFrame:
        """
        Standardize statistical DataFrame to common format
        
        Args:
            df: DataFrame with source-specific statistical columns
            standardize_player_name: Function to standardize player names
            standardize_position: Function to standardize positions
            standardize_team_code: Function to standardize team codes
        Returns:
            DataFrame with standardized statistical columns and values
        """
        if df.empty:
            return df
        
        # Remap columns
        df = self.remap_columns(df)
        
        # Standardize player/team data if present using provided functions
        if 'plyr' in df.columns:
            df['plyr'] = self.standardize_players(df['plyr'], standardize_player_name)
        if 'pos' in df.columns:
            df['pos'] = self.standardize_positions(df['pos'], standardize_position)
        if 'team' in df.columns:
            df['team'] = self.standardize_teams(df['team'], standardize_team_code)
        
        # Convert statistical columns to numeric
        for col in df.columns:
            if col in self.STAT_COLUMNS:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        return df