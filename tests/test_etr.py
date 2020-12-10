import pytest

from nflprojections import EstablishTheRun


def test_etr_init():
    assert EstablishTheRun()


def test_process_raw(base_directory, tprint):   
    etr = EstablishTheRun(basedir=base_directory, season=2020, week=6, slate_name='main')
    df = etr.load_raw()
    df = etr.process_raw(df)
    fields = {'player', 'team', 'opp', 'pos', 'salary', 
              'fpts', 'value', 'ownership', 'dk_slate_id'}
    tprint(df)
    assert fields <= set(df.columns)
    

