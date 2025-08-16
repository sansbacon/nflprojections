# nflprojections/base_standardizer.py
# -*- coding: utf-8 -*-
# Copyright (C) 2025 Eric Truett
# Licensed under the MIT License

"""
Base classes for standardizing data formats across different sources
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Union, Optional
import pandas as pd

try:
    import nflnames
except ImportError:
    nflnames = None

try:
    import nflschedule
except ImportError:
    nflschedule = None


class DataStandardizer(ABC):
    """Abstract base class for standardizing data across different sources"""
    
    # Standard column names that all sources should map to
    REQUIRED_COLUMNS = {'season', 'week', 'plyr', 'pos', 'team', 'proj'}
    
    def __init__(self, column_mapping: Dict[str, str], use_names: bool = True):
        """
        Initialize the data standardizer
        
        Args:
            column_mapping: Mapping from source columns to standard columns
            use_names: Whether to use nflnames for standardization
        """
        # Validate that all required columns are mapped
        mapped_columns = set(column_mapping.values())
        if not self.REQUIRED_COLUMNS.issubset(mapped_columns):
            missing = self.REQUIRED_COLUMNS - mapped_columns
            raise ValueError(f"Column mapping missing required columns: {missing}")
            
        self.column_mapping = column_mapping
        self.use_names = use_names and nflnames is not None
    
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
    
    def standardize_players(self, names: Union[List[str], pd.Series]) -> Union[List[str], pd.Series]:
        """
        Standardize player names using nflnames
        
        Args:
            names: Player names to standardize
            
        Returns:
            Standardized player names
        """
        if not self.use_names:
            return names
        if isinstance(names, (list, tuple, set)):
            return [nflnames.standardize_player_name(n) for n in names]
        return names.apply(nflnames.standardize_player_name)

    def standardize_positions(self, positions: Union[List[str], pd.Series]) -> Union[List[str], pd.Series]:
        """
        Standardize position names using nflnames
        
        Args:
            positions: Position names to standardize
            
        Returns:
            Standardized position names
        """
        if not self.use_names:
            return positions
        if isinstance(positions, (list, tuple, set)):
            return [nflnames.standardize_positions(pos) for pos in positions]
        return positions.apply(nflnames.standardize_positions)

    def standardize_teams(self, teams: Union[List[str], pd.Series]) -> Union[List[str], pd.Series]:
        """
        Standardize team names/codes using nflnames
        
        Args:
            teams: Team names/codes to standardize
            
        Returns:
            Standardized team codes
        """
        if not self.use_names:
            return teams
        if isinstance(teams, (list, tuple, set)):
            return [nflnames.standardize_team_code(t) for t in teams]
        return teams.apply(nflnames.standardize_team_code)


class ProjectionStandardizer(DataStandardizer):
    """Standardizer specifically for NFL projection data"""
    
    def __init__(
        self, 
        column_mapping: Dict[str, str], 
        season: Optional[int] = None,
        week: Optional[int] = None,
        use_names: bool = True,
        use_schedule: bool = True
    ):
        """
        Initialize projection standardizer
        
        Args:
            column_mapping: Mapping from source columns to standard columns
            season: Season to add if not present in data
            week: Week to add if not present in data  
            use_names: Whether to use nflnames for standardization
            use_schedule: Whether to use nflschedule for season/week defaults
        """
        super().__init__(column_mapping, use_names)
        
        # Handle optional schedule
        if use_schedule and nflschedule:
            self.season = season if season is not None else nflschedule.current_season()
            self.week = week if week is not None else nflschedule.current_week()
        else:
            self.season = season
            self.week = week
    
    def standardize(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize projection DataFrame to common format
        
        Args:
            df: DataFrame with source-specific columns
            
        Returns:
            DataFrame with standardized columns and values
        """
        if df.empty:
            return df
        
        # First remap columns
        df = self.remap_columns(df)
        
        # Standardize data using name standardization
        if 'plyr' in df.columns and self.use_names:
            df['plyr'] = self.standardize_players(df['plyr'])
        if 'pos' in df.columns and self.use_names:
            df['pos'] = self.standardize_positions(df['pos'])
        if 'team' in df.columns and self.use_names:
            df['team'] = self.standardize_teams(df['team'])
            
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
    
    def standardize(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize statistical DataFrame to common format
        
        Args:
            df: DataFrame with source-specific statistical columns
            
        Returns:
            DataFrame with standardized statistical columns and values
        """
        if df.empty:
            return df
        
        # Remap columns
        df = self.remap_columns(df)
        
        # Standardize player/team data if present
        if 'plyr' in df.columns and self.use_names:
            df['plyr'] = self.standardize_players(df['plyr'])
        if 'pos' in df.columns and self.use_names:
            df['pos'] = self.standardize_positions(df['pos'])
        if 'team' in df.columns and self.use_names:
            df['team'] = self.standardize_teams(df['team'])
        
        # Convert statistical columns to numeric
        for col in df.columns:
            if col in self.STAT_COLUMNS:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        return df