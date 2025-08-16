# nflprojections/nflprojections/scoring.py
# -*- coding: utf-8 -*-
# Copyright (C) 2025 Eric Truett
# Licensed under the MIT License

from dataclasses import asdict
import logging
from pathlib import Path
import re
from typing import Dict, List, Optional, Union, Any

from .scoring_formats import ScoringFormat


class Scorer:
    """Class for converting raw NFL statistics to fantasy points using a ScoringFormat object."""

    def __init__(self, scoring_format: ScoringFormat):
        """
        Args:
            scoring_format (ScoringFormat): An instance of a scoring format subclass.
        """
        if not isinstance(scoring_format, ScoringFormat):
            raise ValueError("scoring_format must be an instance of ScoringFormat or its subclass.")
        self.scoring_format = scoring_format

    def calculate_fantasy_points(self, stats: Dict[str, Union[int, float]]) -> float:
        """
        Calculate fantasy points based on provided statistics.

        Args:
            stats (Dict[str, Union[int, float]]): Dictionary of player statistics.

        Returns:
            float: The calculated fantasy points.
        """
        get_score = self.scoring_format.get_score
        return sum(get_score(stat, value) for stat, value in stats.items())
    
    def convert_data(self, data: List[Dict[str, Any]], stat_columns: Dict[str, str]) -> List[Dict[str, Any]]:
        """Convert a list of raw statistics dictionaries to fantasy points.
        
        Args:
            data (List[Dict[str, Any]]): List of dictionaries containing raw statistics.
            stat_columns (Dict[str, str]): Mapping from scoring rule keys to data column names.
                
        Returns:
            List[Dict[str, Any]]: The input data with an additional 'fantasy_points' field for each record.
            
        Example:
            >>> scoring = ScoringFormats('ppr')
            >>> data = [
            ...     {
            ...         'player': 'Tom Brady',
            ...         'passing_yards': 300,
            ...         'passing_tds': 3,
            ...         'rushing_yards': 10,
            ...         'rushing_tds': 0,
            ...         'receptions': 0,
            ...         'receiving_yards': 0,
            ...     },
            ...     {
            ...         'player': 'Derrick Henry',
            ...         'passing_yards': 0,
            ...         'passing_tds': 0,
            ...         'rushing_yards': 150,
            ...         'rushing_tds': 2,
            ...         'receptions': 2,
            ...         'receiving_yards': 20,
            ...     }
            ... ]
            >>> stat_columns = {
            ...     'pass_yd': 'passing_yards',
            ...     'pass_td': 'passing_tds',
            ...     'rush_yd': 'rushing_yards',
            ...     'rush_td': 'rushing_tds',
            ...     'rec': 'receptions',
            ...     'rec_yd': 'receiving_yards',
            ... }
            >>> scoring.convert_data(data, stat_columns)
        """
        result = []
        for row in data:
            stats = {
                scoring_key: row.get(df_column, 0)
                for scoring_key, df_column in stat_columns.items()
            }
            new_row = row.copy()
            new_row['fantasy_points'] = self.calculate_fantasy_points(stats)
            result.append(new_row)
        
        return result
    
    def get_scoring_rules(self) -> Dict:
        """Get the current scoring rules as a dictionary.

        Returns:
            Dict: The current scoring rules.
        """
        return asdict(self.scoring_format)