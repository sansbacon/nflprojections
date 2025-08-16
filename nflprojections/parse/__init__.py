# nflprojections/parse/__init__.py
# -*- coding: utf-8 -*-
# Copyright (C) 2020 Eric Truett
# Licensed under the MIT License

"""Data parsing components for NFL projections."""

from .base_parser import DataSourceParser, HTMLTableParser, CSVParser, JSONParser
from .nflcom_parser import NFLComParser
from .etr_parser import ETRParser
from .rotogrinders_parser import RotogrindersJSONParser
from .espn_parser import ESPNParser
from .fantasylife_parser import FantasyLifeParser

__all__ = [
    'DataSourceParser',
    'HTMLTableParser',
    'CSVParser', 
    'JSONParser',
    'NFLComParser',
    'ETRParser',
    'RotogrindersJSONParser',
    'ESPNParser',
    'FantasyLifeParser'
]