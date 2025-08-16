# nflprojections/sources/__init__.py
# -*- coding: utf-8 -*-
# Copyright (C) 2020 Eric Truett
# Licensed under the MIT License

"""Complete projection source implementations."""

from .projectionsource import ProjectionSource
from .nflcom import NFLComProjections
from .nflcom_refactored import NFLComProjectionsRefactored
from .etr import ETRProjections
from .etr_refactored import ETRProjectionsRefactored

__all__ = [
    'ProjectionSource',
    'NFLComProjections',
    'NFLComProjectionsRefactored',
    'ETRProjections',
    'ETRProjectionsRefactored'
]