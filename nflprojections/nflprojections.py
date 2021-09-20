# nflprojections/nflprojections/nflprojections.py
# -*- coding: utf-8 -*-
# Copyright (C) 2020 Eric Truett
# Licensed under the MIT License

import logging
from pathlib import Path
import re
from typing import Dict, List, Union

import numpy as np
import pandas as pd

import nflnames
import nflschedule


Standardized = Union[List[str], pd.Series]


class ProjectionSource:

    REQUIRED_MAPPED_COLUMNS = {'season', 'week', 'plyr', 'pos', 'team', 'proj'}
    VALID_SITE_NAMES = {'dk', 'fd', 'yh', 'all'}
    VALID_SLATE_NAMES = {'main', 'early', 'late', 'all', 'tsd', 'ssd', 'msd'}
    VALID_FORMATS = {'csv', 'json', 'pkl', 'parquet'}

    projections_name = 'base'

    def __init__(self, 
                 rawdir: Path, 
                 procdir: Path, 
                 column_mapping: Dict[str, str], 
                 season: int = None, 
                 week: int = None, 
                 site_name: str = 'all', 
                 slate_name: str = 'all', 
                 raw_format: str = 'csv', 
                 processed_format: str = 'csv'):
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

        # validate site_name
        if site_name not in self.VALID_SITE_NAMES:
            raise ValueError(f'Invalid site name: {site_name}')
        self.site_name = site_name

        # validate slate_name
        if slate_name not in self.VALID_SLATE_NAMES:
            raise ValueError(f'Invalid slate name: {slate_name}')
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
        parts = [str(self.season), f'w{self.week}', self.projections_name, self.site_name, self.slate_name]
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
              

class ProjectionCombiner:

    def __init__(self):
        """Need to document all of the parameters"""
        pass
