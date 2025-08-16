# nflprojections/__init__.py
# -*- coding: utf-8 -*-
# Copyright (C) 2020 Eric Truett
# Licensed under the MIT License

# Main projection sources
from .sources.projectionsource import ProjectionSource
from .sources.nflcom import NFLComProjections
from .sources.nflcom_refactored import NFLComProjectionsRefactored

# Combination functionality
from .combine.projectioncombiner import ProjectionCombiner, CombinationMethod

# Scoring systems
from .scoring.scoring_formats import (
    ScoringFormat, StandardScoring, HalfPPRScoring, PPRScoring,
    DraftKingsScoring, FanDuelScoring, YahooScoring, HomeAuctionScoring
)

# Base functional components
from .fetch.base_fetcher import DataSourceFetcher, WebDataFetcher, FileDataFetcher
from .parse.base_parser import DataSourceParser, HTMLTableParser, CSVParser, JSONParser
from .standardize.base_standardizer import DataStandardizer, ProjectionStandardizer, StatStandardizer

# Specific implementations
from .fetch.nflcom_fetcher import NFLComFetcher
from .parse.nflcom_parser import NFLComParser

import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())
