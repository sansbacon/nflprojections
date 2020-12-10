from pathlib import Path
from nflschedule.nflschedule import current_season

import pandas as pd
import pytest

from nflprojections import ProjectionSource
from nflschedule import current_season, current_week


@pytest.fixture
def mapping():
    return {
        'ID': 'dk_slate_id',
        'Name': 'player',
        'Position': 'pos',
        'TeamAbbrev': 'team',
        'Salary': 'salary',
        'AvgPointsPerGame': 'fpts',
    }


@pytest.fixture
def fixed_psparams(test_directory):
    return {
        'basedir': test_directory / 'testdata/2020/6',
        'season': 2020,
        'week': 6,
        'projections_name': 'ps',
        'site_name': 'all',
        'slate_name': 'all'
    }


@pytest.fixture
def psparams():
    return {
        'basedir': Path.home(),
        'season': current_season(),
        'week': current_week(),
        'projections_name': 'ps',
        'site_name': 'all',
        'slate_name': 'all'
    }
    

@pytest.fixture
def ps(fixed_psparams):
    return ProjectionSource(**fixed_psparams)
    

def test_projection_source(psparams):
    ps = ProjectionSource(**psparams)
    assert ps.DEFAULT_COLUMN_MAPPING == {}


def test_make_raw_fn(fixed_psparams):
    """Tests ps.make_raw_fn()"""
    ps = ProjectionSource(**fixed_psparams)
    fn = ps.make_raw_fn()
    season = fixed_psparams.get('season')
    week = fixed_psparams.get('week')
    assert fn.name == f'{season}_w{week}_ps_all_all.csv'


def test_load_raw(ps):
    df = ps.load_raw()
    assert not df.empty
    assert 'ID' in df.columns


def test_remap_columns(ps, mapping):
    df = ps.load_raw()
    assert {'player', 'pos', 'team', 'salary'} < set(ps.remap_columns(df, column_remap=mapping))


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
