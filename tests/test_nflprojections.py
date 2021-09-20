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
      'fppg': 'proj',
      'position': 'pos'
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
    assert isinstance(ProjectionSource(**psparams), ProjectionSource)


def test_init_missing_param(psparams):
    with pytest.raises(TypeError):      
        _ = psparams.pop('rawdir')
        ps = ProjectionSource(**psparams)


def test_init_missing_mapping(psparams):
    with pytest.raises(AssertionError):      
        _ = psparams['column_mapping'].pop('wk')
        ps = ProjectionSource(**psparams)


def test_load_raw(ps):
    with pytest.raises(NotImplementedError):
        ps.load_raw()


def test_proc_fn(ps, psparams):
    """Tests ps.processed_fn"""
    fn = ps.raw_fn
    season = psparams.get('season')
    week = psparams.get('week')
    assert fn.name == f'{season}_w{week}_base_all_all.csv'


def test_raw_fn(ps, psparams):
    """Tests ps.raw_fn"""
    fn = ps.raw_fn
    season = psparams.get('season')
    week = psparams.get('week')
    assert fn.name == f'{season}_w{week}_base_all_all.csv'


def test_remap_columns(ps, mapping):
    cols = list(mapping.keys())
    assert set(ps.remap_columns(cols)) == set(mapping.values())


def test_remap_columns_extras(psparams, mapping):
    newmapping = mapping | {'extra_key': 'extra_value'}
    psparams['column_mapping'] = newmapping
    newps = ProjectionSource(**psparams)
    cols = list(newmapping.keys())
    assert set(newps.remap_columns(cols)) == set(newmapping.values())


def test_standardize(ps):
    with pytest.raises(NotImplementedError):
        ps.standardize()


def test_standardize_players(ps):
    """Tests standardize_players"""
    # def standardize_players(self, names: Standardized) -> Standardized:
    s = ['Henry Ruggs IV', 'Will Fuller V']
    assert ps.standardize_players(s) == ['henry ruggs', 'will fuller']


def test_standardize_positions(ps):
    """Tests standardize_positions"""
    # def standardize_positions(self, positions: Standardized) -> Standardized:
    positions = ['QB', 'Defense', 'Kicker']
    assert ps.standardize_positions(positions) == ['QB', 'DST', 'K']


def test_standardize_teams(ps):
    """Tests standardize_teams"""
    teams = ['KCC', 'GBP', 'LAC']
    assert ps.standardize_teams(teams) == ['KC', 'GB', 'LAC']

