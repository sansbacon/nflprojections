# nflprojections/combine/__init__.py
# -*- coding: utf-8 -*-
# Copyright (C) 2020 Eric Truett
# Licensed under the MIT License

"""Projection combination components for NFL projections."""

from .projectioncombiner import ProjectionCombiner, CombinationMethod

__all__ = [
    'ProjectionCombiner',
    'CombinationMethod'
]