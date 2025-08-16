# nflprojections/nflprojections/scoring.py
# -*- coding: utf-8 -*-
# Copyright (C) 2025 Eric Truett
# Licensed under the MIT License

from dataclasses import asdict
import logging
from pathlib import Path
import re
from typing import Dict, List, Optional, Union

import numpy as np
import pandas as pd

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
        def compute_row(row):
            stats = {
                scoring_key: row.get(df_column, 0)
                for scoring_key, df_column in stat_columns.items()
            }
            return self.calculate_fantasy_points(stats)

        return df.assign(fantasy_points=lambda x: x.apply(compute_row, axis=1))
    
    def get_scoring_rules(self) -> Dict:
        """Get the current scoring rules as a dictionary.

        Returns:
            Dict: The current scoring rules.
        """
        return asdict(self.scoring_format)