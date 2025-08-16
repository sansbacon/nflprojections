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

try:
    import nflnames
except ImportError:
    nflnames = None

try:
    import nflschedule
except ImportError:
    nflschedule = None


Standardized = Union[List[str], pd.Series]


import logging
from pathlib import Path
from typing import Dict, List, Optional, Union

import pandas as pd

# Optional imports
try:
    import nflnames
except ImportError:
    nflnames = None

try:
    import nflschedule
except ImportError:
    nflschedule = None

from .scoring import Scorer


class ProjectionSource:
    """Base class for projections"""
    REQUIRED_MAPPED_COLUMNS = {'season', 'week', 'plyr', 'pos', 'team', 'proj'}
    VALID_SLATE_NAMES = {'main', 'early', 'late', 'all', 'tsd', 'ssd', 'msd', 'season', 'playoffs', 'bestball'}
    VALID_FORMATS = {'csv', 'json', 'pkl', 'parquet'}

    def __init__(
        self,
        source_name: str,
        column_mapping: Dict[str, str],
        slate_name: str,
        season: int,
        week: int,
        use_schedule: bool = True,
        use_names: bool = True
    ):
        self.scoring_format = scoring_format
        self.projections_source = source_name
        self.slate_name = slate_name
        self.scorer = scorer

        # Validate column mappings
        assert self.REQUIRED_MAPPED_COLUMNS.issubset(set(column_mapping.values()))
        self.column_mapping = column_mapping

        # Handle optional schedule
        if use_schedule and nflschedule:
            self.season = season if season is not None else nflschedule.current_season()
            self.week = week if week is not None else nflschedule.current_week()
        else:
            self.season = season
            self.week = week

        # Handle optional name standardization
        self.use_names = use_names and nflnames is not None

    def standardize_players(self, names: Union[List[str], pd.Series]) -> Union[List[str], pd.Series]:
        if not self.use_names:
            return names
        if isinstance(names, (list, tuple, set)):
            return [nflnames.standardize_player_name(n) for n in names]
        return names.apply(nflnames.standardize_player_name)

    def standardize_positions(self, positions: Union[List[str], pd.Series]) -> Union[List[str], pd.Series]:
        if not self.use_names:
            return positions
        if isinstance(positions, (list, tuple, set)):
            return [nflnames.standardize_positions(pos) for pos in positions]
        return positions.apply(nflnames.standardize_positions)

    def standardize_teams(self, teams: Union[List[str], pd.Series]) -> Union[List[str], pd.Series]:
        if not self.use_names:
            return teams
        if isinstance(teams, (list, tuple, set)):
            return [nflnames.standardize_team_code(t) for t in teams]
        return teams.apply(nflnames.standardize_team_code)