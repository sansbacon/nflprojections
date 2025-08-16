# nflprojections/__init__.py
# -*- coding: utf-8 -*-
# Copyright (C) 2020 Eric Truett
# Licensed under the MIT License

# Main high-level APIs - users import specific components from submodules
from .sources.projectionsource import ProjectionSource
from .sources.nflcom import NFLComProjections
from .sources.etr import ETRProjections
from .sources.espn import ESPNProjections

from .sources.rotogrinders_refactored import RotogrindersProjections
from .sources.fantasylife import FantasyLifeProjections

from .combine.projectioncombiner import ProjectionCombiner, CombinationMethod

import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())
