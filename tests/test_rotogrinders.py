from pathlib import Path

import pandas as pd
import pytest

from nflprojections import Rotogrinders
from nflschedule import current_season, current_week


@pytest.fixture
def fixed_psparams(test_directory):
    return {
        'basedir': test_directory / 'testdata/2020/6',
        'season': 2020,
        'week': 6,
        'projections_name': 'rg-blitz',
        'site_name': 'dk',
        'slate_name': 'all'
    }


@pytest.fixture
def psparams():
    return {
        'basedir': Path.home(),
        'season': current_season(),
        'week': current_week(),
        'projections_name': 'rg-core',
        'site_name': 'dk',
        'slate_name': 'all'
    }
    

@pytest.fixture
def rg(fixed_psparams):
    return Rotogrinders(**fixed_psparams)


def test_rg_init(psparams):
    rg = Rotogrinders(**psparams)
    assert rg.season >= 0
    assert rg.week >= 0
    assert rg.projections_name
    assert rg.site_name
    assert rg.slate_name


def test_rg_parse_rg_page(rg):
    """Tests parse_rg_page (converts js variable embedded in HTML source to DataFrame)"""
    df = rg.parse_rg_page(save_file=False)
    assert isinstance(df, pd.core.api.DataFrame)   
    assert  'fpts' in df.columns

    rg.projections_name = 'rg-core'
    df = rg.parse_rg_page()
    assert isinstance(df, pd.core.api.DataFrame)   
    assert  'fpts' in df.columns


def test_rg_process_raw(rg, tprint):
    df = rg.parse_rg_page(save_file=False)
    newdf = rg.process_raw(df)
    assert not newdf.loc[newdf.pos == 'DST'].empty
    tprint(newdf)