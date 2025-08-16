# nflprojections/nflprojections/__init__.py
# -*- coding: utf-8 -*-
# Copyright (C) 2020 Eric Truett
# Licensed under the MIT License

from .projectionsource import ProjectionSource
from .projectioncombiner import ProjectionCombiner
from .scoring_formats import (
    ScoringFormat, StandardScoring, HalfPPRScoring, PPRScoring,
    DraftKingsScoring, FanDuelScoring, YahooScoring, HomeAuctionScoring
)


import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())
