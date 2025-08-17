# nflprojections/fantasypros.py
# -*- coding: utf-8 -*-
# Copyright (C) 2025 Eric Truett
# Licensed under the MIT License

"""
FantasyPros fantasy projections using refactored functional components
"""

import logging
from typing import Dict, Optional, List, Any, Union

from ..fetch.fantasypros_fetcher import FantasyProsFetcher
from ..parse.fantasypros_parser import FantasyProsParser
from ..standardize.base_standardizer import ProjectionStandardizer


logger = logging.getLogger(__name__)


class FantasyProsProjections:
    """FantasyPros projections using separate functional components"""
    
    # Default column mapping from FantasyPros format to standard format
    DEFAULT_COLUMN_MAPPING = {
        'player': 'plyr',
        'position': 'pos', 
        'team': 'team',
        'fantasy_points': 'proj',
        'season': 'season',
        'week': 'week',
        # QB-specific stats
        'pass_att': 'pass_att',
        'cmp': 'pass_cmp',
        'pass_yds': 'pass_yd', 
        'pass_td': 'pass_td',
        'int': 'pass_int',
        'rush_att': 'rush_att',
        'rush_yds': 'rush_yd',
        'rush_td': 'rush_td',
        'fum': 'fum_lost',
        # Skill position stats  
        'rec': 'rec',
        'rec_yds': 'rec_yd',
        'rec_td': 'rec_td',
        'att': 'rush_att',  # For non-QB positions, 'att' refers to rushing attempts
        'yds': 'rush_yd',   # For non-QB positions, 'yds' refers to rushing yards
        'td': 'rush_td',    # For non-QB positions, 'td' refers to rushing TDs
    }
    
    def __init__(
        self,
        position: str = "qb",
        scoring: str = "ppr",
        week: Union[str, int] = "draft",
        season: int = None,
        column_mapping: Dict[str, str] = None,
        use_schedule: bool = True,
        use_names: bool = True,
        timeout: int = 30,
        **kwargs
    ):
        """
        Initialize FantasyPros projections using functional components
        
        Args:
            position: Position to fetch (qb, rb, wr, te, k, dst, all)
            scoring: Scoring format (ppr, half, standard)
            week: Week number for weekly projections (draft for season totals)
            season: NFL season (defaults to current season)
            column_mapping: Custom column mapping dictionary
            use_schedule: Whether to add schedule information
            use_names: Whether to standardize player/team names
            timeout: Request timeout in seconds
            **kwargs: Additional configuration for fetcher
        """
        # Initialize fetcher
        self.fetcher = FantasyProsFetcher(
            position=position,
            scoring=scoring,
            week=week,
            timeout=timeout,
            **kwargs
        )
        
        # Initialize parser with position context
        self.parser = FantasyProsParser(position=position)
        
        # Initialize standardizer
        column_mapping = column_mapping or self.DEFAULT_COLUMN_MAPPING.copy()
        self.standardizer = ProjectionStandardizer(
            column_mapping=column_mapping,
            season=season,
            week=week if isinstance(week, int) else None
        )
        
        # Store additional configuration
        self.use_schedule = use_schedule
        self.use_names = use_names
        
        # Store configuration
        self.season = season
        self.week = week
        self.position = position
        self.scoring = scoring
        self.timeout = timeout
        
        logger.info(f"Initialized FantasyPros projections for {position.upper()}, {scoring.upper()} scoring, week {week}")
    
    def fetch_raw_data(self, position: str = None, scoring: str = None, week: Union[str, int] = None) -> Any:
        """
        Fetch raw data from FantasyPros
        
        Args:
            position: Position to fetch (overrides configured position)
            scoring: Scoring format (overrides configured scoring)
            week: Week to fetch (overrides configured week)
            
        Returns:
            Raw BeautifulSoup data from fetcher
        """
        return self.fetcher.fetch_raw_data(position=position, scoring=scoring, week=week)
    
    def parse_data(self, raw_data: Any) -> List[Dict[str, Any]]:
        """
        Parse raw data into structured format
        
        Args:
            raw_data: Raw BeautifulSoup data from fetcher
            
        Returns:
            Parsed list of dictionaries
        """
        return self.parser.parse_raw_data(raw_data)
    
    def standardize_data(self, parsed_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Standardize parsed data to common format
        
        Args:
            parsed_data: Parsed data from parser
            
        Returns:
            Standardized list of dictionaries
        """
        return self.standardizer.standardize(parsed_data)
    
    def data_pipeline(self, position: str = None, scoring: str = None, week: Union[str, int] = None) -> List[Dict[str, Any]]:
        """
        Execute complete data pipeline: fetch -> parse -> standardize
        
        Args:
            position: Position to fetch (overrides configured position)
            scoring: Scoring format (overrides configured scoring)  
            week: Week to fetch (overrides configured week)
            
        Returns:
            Standardized projection data
        """
        logger.info(f"Running FantasyPros data pipeline for {position or self.position}, week {week or self.week}")
        
        # Fetch raw data
        raw_data = self.fetch_raw_data(position=position, scoring=scoring, week=week)
        logger.debug(f"Fetched raw HTML data from FantasyPros")
        
        # Parse data
        parsed_data = self.parse_data(raw_data)
        logger.debug(f"Parsed {len(parsed_data)} player records")
        
        # Standardize data
        standardized_data = self.standardize_data(parsed_data)
        logger.debug(f"Standardized {len(standardized_data)} player projections")
        
        return standardized_data
    
    def fetch_projections(self, position: str = None, scoring: str = None, week: Union[str, int] = None) -> List[Dict[str, Any]]:
        """
        Fetch and process FantasyPros projections
        
        Args:
            position: Position to fetch (overrides configured position)
            scoring: Scoring format (overrides configured scoring)
            week: Week to fetch (overrides configured week)
            
        Returns:
            List of dictionaries with standardized projection data
        """
        return self.data_pipeline(position=position, scoring=scoring, week=week)
    
    def validate_data_pipeline(self) -> Dict[str, bool]:
        """
        Validate that all components of the data pipeline are working
        
        Returns:
            Dictionary with validation results for each component
        """
        results = {}
        
        # Test fetcher connection
        try:
            results['fetcher_connection'] = self.fetcher.validate_connection()
        except Exception as e:
            logger.error(f"FantasyPros fetcher validation failed: {e}")
            results['fetcher_connection'] = False
        
        # Test parser (with minimal fetch)
        try:
            raw_data = self.fetcher.fetch_raw_data()
            parsed_data = self.parser.parse_raw_data(raw_data)
            results['parser_valid'] = self.parser.validate_parsed_data(parsed_data)
        except Exception as e:
            logger.error(f"FantasyPros parser validation failed: {e}")
            results['parser_valid'] = False
        
        # Test standardizer
        try:
            # Create dummy data to test standardizer
            dummy_data = [{
                'player': 'Test Player',
                'position': 'QB',
                'team': 'KC',
                'fantasy_points': 20.5
            }]
            standardized = self.standardizer.standardize(dummy_data)
            results['standardizer_valid'] = len(standardized) > 0 and 'plyr' in standardized[0]
        except Exception as e:
            logger.error(f"FantasyPros standardizer validation failed: {e}")
            results['standardizer_valid'] = False
        
        return results
    
    def get_pipeline_info(self) -> Dict[str, str]:
        """
        Get information about the configured pipeline components
        
        Returns:
            Dictionary with component information
        """
        return {
            'fetcher': f"{self.fetcher.__class__.__name__} - {self.fetcher.source_name}",
            'parser': f"{self.parser.__class__.__name__} - {self.parser.source_name}",
            'standardizer': f"{self.standardizer.__class__.__name__}",
            'season': str(self.season),
            'week': str(self.week),
            'position': str(self.position),
            'scoring': str(self.scoring),
            'column_mapping': str(self.standardizer.column_mapping)
        }