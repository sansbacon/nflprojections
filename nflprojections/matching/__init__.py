# nflprojections/matching/__init__.py
# -*- coding: utf-8 -*-
# Copyright (C) 2025 Eric Truett
# Licensed under the MIT License

"""Player matching components for NFL projections."""

from .player_matcher import PlayerMatcher, MatchResult

__all__ = [
    'PlayerMatcher',
    'MatchResult'
]