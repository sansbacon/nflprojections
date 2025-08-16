# nflprojections/nflprojections/__init__.py
# -*- coding: utf-8 -*-
# Copyright (C) 2020 Eric Truett
# Licensed under the MIT License

from .projectionsource import ProjectionSource
from .projectioncombiner import ProjectionCombiner, CombinationMethod
from .nflcom import NFLComProjections
from .nflcom_refactored import NFLComProjectionsRefactored
from .scoring_formats import (
    ScoringFormat, StandardScoring, HalfPPRScoring, PPRScoring,
    DraftKingsScoring, FanDuelScoring, YahooScoring, HomeAuctionScoring
)

# Base functional components
from .base_fetcher import DataSourceFetcher, WebDataFetcher, FileDataFetcher
from .base_parser import DataSourceParser, HTMLTableParser, CSVParser, JSONParser
from .base_standardizer import DataStandardizer, ProjectionStandardizer, StatStandardizer

# Specific implementations
from .nflcom_fetcher import NFLComFetcher
from .nflcom_parser import NFLComParser


import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())
