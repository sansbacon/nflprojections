# -*- coding: utf-8 -*-
import json
import logging
from pathlib import Path
import pandas as pd
import pytest
import random


from nflprojections.espnapi import Scraper, Parser


def test_scraper():
    assert Scraper(2020)


def test_playerstats(tprint, raw_directory):
    season = 2020
    week = 8
    s = Scraper(season)
    p = Parser(season)
    data = s.playerstats()
    assert isinstance(data, dict)
    players = p.weekly_projections(data, week)
    assert isinstance(players, list)
    assert isinstance(players[0], dict)
    tprint(players[0])
    