# nflprojections/base_standardizer.py
# -*- coding: utf-8 -*-
# Copyright (C) 2025 Eric Truett
# Licensed under the MIT License

"""
Base classes for standardizing data formats across different sources
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Union, Optional, Callable, Any


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
    def standardize(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Standardize a list of dictionaries to common format
        
        Args:
            data: List of dictionaries with source-specific keys
            
        Returns:
            List of dictionaries with standardized keys and values
        """
        pass
    
    def remap_columns(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remap columns from source format to standardized format
        
        Args:
            data: List of dictionaries with source column names
            
        Returns:
            List of dictionaries with standardized column names
        """
        result = []
        for row in data:
            new_row = {}
            for key, value in row.items():
                new_key = self.column_mapping.get(key, key)
                new_row[new_key] = value
            result.append(new_row)
        return result
    
    def standardize_players(self, names: List[str], standardize_player_name: Optional[Callable[[str], str]] = None) -> List[str]:
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
        return [standardize_player_name(n) for n in names]

    def standardize_positions(self, positions: List[str], standardize_position: Optional[Callable[[str], str]] = None) -> List[str]:
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
        return [standardize_position(pos) for pos in positions]

    def standardize_teams(self, teams: List[str], standardize_team_code: Optional[Callable[[str], str]] = None) -> List[str]:
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
        return [standardize_team_code(t) for t in teams]


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
        data: List[Dict[str, Any]],
        standardize_player_name: Optional[Callable[[str], str]] = None,
        standardize_position: Optional[Callable[[str], str]] = None,
        standardize_team_code: Optional[Callable[[str], str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Standardize projection data to common format
        
        Args:
            data: List of dictionaries with source-specific keys
            standardize_player_name: Function to standardize player names
            standardize_position: Function to standardize positions
            standardize_team_code: Function to standardize team codes
        Returns:
            List of dictionaries with standardized keys and values
        """
        if not data:
            return data
        
        # First remap columns
        data = self.remap_columns(data)
        
        # Standardize data using provided functions
        for row in data:
            if 'plyr' in row and row['plyr'] is not None:
                if standardize_player_name:
                    row['plyr'] = standardize_player_name(row['plyr'])
            if 'pos' in row and row['pos'] is not None:
                if standardize_position:
                    row['pos'] = standardize_position(row['pos'])
            if 'team' in row and row['team'] is not None:
                if standardize_team_code:
                    row['team'] = standardize_team_code(row['team'])
            
            # Ensure required columns exist
            for col in self.REQUIRED_COLUMNS:
                if col not in row:
                    if col == 'season' and self.season is not None:
                        row[col] = self.season
                    elif col == 'week' and self.week is not None:
                        row[col] = self.week
                    else:
                        row[col] = None
        
        return data


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
        data: List[Dict[str, Any]],
        standardize_player_name: Optional[Callable[[str], str]] = None,
        standardize_position: Optional[Callable[[str], str]] = None,
        standardize_team_code: Optional[Callable[[str], str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Standardize statistical data to common format
        
        Args:
            data: List of dictionaries with source-specific statistical keys
            standardize_player_name: Function to standardize player names
            standardize_position: Function to standardize positions
            standardize_team_code: Function to standardize team codes
        Returns:
            List of dictionaries with standardized statistical keys and values
        """
        if not data:
            return data
        
        # Remap columns
        data = self.remap_columns(data)
        
        # Standardize player/team data if present using provided functions
        for row in data:
            if 'plyr' in row and row['plyr'] is not None:
                if standardize_player_name:
                    row['plyr'] = standardize_player_name(row['plyr'])
            if 'pos' in row and row['pos'] is not None:
                if standardize_position:
                    row['pos'] = standardize_position(row['pos'])
            if 'team' in row and row['team'] is not None:
                if standardize_team_code:
                    row['team'] = standardize_team_code(row['team'])
            
            # Convert statistical columns to numeric
            for col in row.keys():
                if col in self.STAT_COLUMNS:
                    try:
                        row[col] = float(row[col]) if row[col] is not None else 0.0
                    except (ValueError, TypeError):
                        row[col] = 0.0
        
        return data
        
        return df