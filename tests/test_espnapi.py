# -*- coding: utf-8 -*-
from functools import lru_cache
import json
import pandas as pd
import pytest


from nflprojections.espnapi import Scraper, Parser


SEASON = 2021

#@lru_cache
@pytest.fixture
def content(test_directory):
    return json.loads((test_directory / 'testdata' / 'espn.json').read_text())


def test_scraper():
    assert Scraper(SEASON)


def test_parser():
    assert Parser(SEASON, 0)


def test_season_projections(content, tprint):
    p = Parser(season=SEASON, week=0)
    proj = p.projections(content)
    assert isinstance(proj, list)
    assert isinstance(proj[0], dict)

