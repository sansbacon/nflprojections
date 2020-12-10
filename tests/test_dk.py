from pathlib import Path

import pytest

from nflprojections import Dk


def test_dk_init():
    season = 2020
    week = 6
    obj = Dk(season=season, week=week)
    assert obj.basedir == Path.home()
    assert obj.season == season
    assert obj.week == week
    assert obj.projections_name == 'DKSalaries'


def test_dk_process_raw(base_directory, raw_directory, tprint):
    season = 2020
    week = 6
    obj = Dk(basedir=base_directory, season=season, week=week)

    # read the raw DK salaries file
    df = obj.load_raw()
    assert 'Salary' in df.columns

    # clean up raw file
    newdf = obj.process_raw(df)
    assert 'fpts' in newdf.columns    
    tprint(newdf)

    # test column prefix
    newdf = obj.process_raw(df, column_prefix='dk')
    assert 'dk_pos' in newdf.columns