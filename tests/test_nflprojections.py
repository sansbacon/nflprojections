# nflprojections/tests/test_nflprojections.py
# -*- coding: utf-8 -*-
# Copyright (C) 2020 Eric Truett
# Licensed under the MIT License

from pathlib import Path

import pandas as pd
import pytest

from nflprojections import ProjectionSource
from nflschedule import current_season, current_week


@pytest.fixture
def mapping():
    return {
      'seas': 'season',
      'wk': 'week',
      'player_name': 'plyr',
      'team': 'team',
      'fppg': 'proj'
    }


@pytest.fixture
def psparams(mapping):
    return {
        'rawdir': Path.home(),
        'procdir': Path.home(),
        'column_mapping': mapping,
        'season': current_season(),
        'week': current_week(),
        'site_name': 'all',
        'slate_name': 'all',
        'raw_format': 'csv',
        'processed_format': 'parquet'
    }
    

@pytest.fixture
def ps(psparams):
    return ProjectionSource(**psparams)
    

def test_init(psparams):
    assert isinstance(ProjectionSource, ProjectionSource(**psparams))


"""
    def load_raw(self) -> pd.DataFrame:       
    def process_raw(self) -> pd.DataFrame:
    def remap_columns(self, cols: List[str]) -> List[str]:
    def standardize(self) -> pd.DataFrame:
    def standardize_players(self, names: Standardized) -> Standardized:
    def standardize_positions(self, positions: Standardized) -> Standardized:
    def standardize_teams(self, teams: Standardized) -> Standardized:
"""

@pytest.mark.skip
def test_projection_source(psparams):
    ps = ProjectionSource(**psparams)
    assert ps.DEFAULT_COLUMN_MAPPING == {}


@pytest.mark.skip
def test_make_raw_fn(fixed_psparams):
    """Tests ps.make_raw_fn()"""
    ps = ProjectionSource(**fixed_psparams)
    fn = ps.make_raw_fn()
    season = fixed_psparams.get('season')
    week = fixed_psparams.get('week')
    assert fn.name == f'{season}_w{week}_ps_all_all.csv'


@pytest.mark.skip
def test_load_raw(ps):
    df = ps.load_raw()
    assert not df.empty
    assert 'ID' in df.columns


@pytest.mark.skip
def test_remap_columns(ps, mapping):
    df = ps.load_raw()
    assert {'player', 'pos', 'team', 'salary'} < set(ps.remap_columns(df, column_remap=mapping))


@pytest.mark.skip
def test_standardize_teams(ps, mapping, tprint):
    df = ps.load_raw()
    df.columns = ps.remap_columns(df, mapping)
    assert 'GBP' in df['team'].unique()
    assert 'KCC' in df['team'].unique()
    df['team'] = ps.standardize_teams(df['team'])
    teams = df['team'].unique()
    assert 'GBP' not in teams
    assert 'GB' in teams
    assert 'KCC' not in teams
    assert 'KC' in teams
