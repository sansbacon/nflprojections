import pandas as pd
import pytest

from nflprojections import Ffa


def test_ffa_init():
    assert Ffa()
    obj = Ffa(season=2020, week=1, projections_name='ffa')
    assert obj.season == 2020
    assert obj.week == 1
    assert obj.projections_name == 'ffa'


def test_ffa_process_raw(raw_directory, tprint):
    season = 2020
    week = 6
    projections_name = 'ffa'
    obj = Ffa(season=season, week=week, projections_name=projections_name)
    fn = f'{obj.season}_w{obj.week}_{obj.projections_name}_dkproj.csv'   
    df = pd.read_csv(raw_directory / fn)
    newdf = obj.process_raw(df, column_remap={})
    assert 'fpts' not in newdf.columns    
    newdf = obj.process_raw(df, column_remap='default')
    assert 'fpts' in newdf.columns
    newdf = obj.process_raw(df, column_prefix='ffa')
    assert 'ffa_pos' in newdf.columns