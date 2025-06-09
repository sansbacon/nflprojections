# nflprojections/nflprojections/__init__.py
# -*- coding: utf-8 -*-
# Copyright (C) 2020 Eric Truett
# Licensed under the MIT License
from .nflprojections import ProjectionCombiner, ProjectionSource, ScoringFormats

import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())
