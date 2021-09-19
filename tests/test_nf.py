# -*- coding: utf-8 -*-
import pandas as pd
import pytest


from nflprojections.nf import Scraper, Parser


def test_scraper():
    assert Scraper()


def test_parser():
    assert Parser()


def test_projections(tprint):
    s = Scraper()
    p = Parser()
    content = s.projections(week=0)
    assert isinstance(content, bytes)
    proj = p.projections(content)
    assert isinstance(proj, pd.DataFrame)
    tprint(proj)
