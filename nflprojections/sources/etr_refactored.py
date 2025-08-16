# nflprojections/etr_refactored.py
# -*- coding: utf-8 -*-
# Copyright (C) 2025 Eric Truett
# Licensed under the MIT License

"""
Refactored ETR projections using functional components
"""

import logging
from typing import Dict, Optional, List, Any

from ..fetch.etr_fetcher import ETRFetcher
from ..parse.etr_parser import ETRParser
from ..standardize.base_standardizer import ProjectionStandardizer


logger = logging.getLogger(__name__)


class ETRProjectionsRefactored:
    """Refactored ETR projections using separate functional components"""
    
    # Default column mapping from ETR format to standard format
    DEFAULT_COLUMN_MAPPING = {
        'player': 'plyr',
        'position': 'pos', 
        'team': 'team',
        'fantasy_points': 'proj',
        'season': 'season',
        'week': 'week'
    }
    
    def __init__(
        self,
        season: int = None,
        week: int = None,
        position: str = "all",
        scoring: str = "ppr",
        column_mapping: Dict[str, str] = None,
        use_schedule: bool = True,
        use_names: bool = True,
        **kwargs
    ):
        """
        Initialize ETR projections using functional components
        
        Args:
            season: NFL season (defaults to current season)
            week: Week number for weekly projections (None for season totals)
            position: Position filter (all, qb, rb, wr, te, k, dst)
            scoring: Scoring format (ppr, half-ppr, standard)
            column_mapping: Custom column mapping dictionary
            use_schedule: Whether to add schedule information
            use_names: Whether to standardize player/team names
            **kwargs: Additional configuration for fetcher
        """
        # Initialize fetcher
        self.fetcher = ETRFetcher(
            position=position,
            scoring=scoring,
            week=week,
            **kwargs
        )
        
        # Initialize parser
        self.parser = ETRParser()
        
        # Initialize standardizer
        column_mapping = column_mapping or self.DEFAULT_COLUMN_MAPPING.copy()
        self.standardizer = ProjectionStandardizer(
            column_mapping=column_mapping,
            season=season,
            week=week
        )
        
        # Store additional configuration
        self.use_schedule = use_schedule
        self.use_names = use_names
        
        # Store configuration
        self.season = season
        self.week = week
        self.position = position
        self.scoring = scoring
    
    def fetch_raw_data(self, season: int = None) -> Any:
        """
        Fetch raw data from ETR
        
        Args:
            season: Season to fetch (uses configured season if not provided)
            
        Returns:
            Raw data from fetcher
        """
        return self.fetcher.fetch_raw_data(season=season)
    
    def parse_data(self, raw_data: Any) -> List[Dict[str, Any]]:
        """
        Parse raw data into structured format
        
        Args:
            raw_data: Raw data from fetcher
            
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
    
    def data_pipeline(self, season: int = None) -> List[Dict[str, Any]]:
        """
        Execute complete data pipeline: fetch -> parse -> standardize
        
        Args:
            season: Season to fetch
            
        Returns:
            Standardized projection data
        """
        # Fetch raw data
        raw_data = self.fetch_raw_data(season=season)
        
        # Parse data
        parsed_data = self.parse_data(raw_data)
        
        # Standardize data
        standardized_data = self.standardize_data(parsed_data)
        
        return standardized_data
    
    def fetch_projections(self, season: int = None) -> List[Dict[str, Any]]:
        """
        Fetch and process ETR projections
        
        Args:
            season: Season to fetch (uses configured season if not provided)
            
        Returns:
            List of dictionaries with standardized projection data
        """
        return self.data_pipeline(season=season)
    
    def validate_data_pipeline(self) -> Dict[str, bool]:
        """
        Validate that all components of the data pipeline are working
        
        Returns:
            Dictionary with validation results for each component
        """
        results = {}
        
        # Test fetcher
        try:
            results['fetcher_connection'] = self.fetcher.validate_connection()
        except Exception as e:
            logger.error(f"ETR fetcher validation failed: {e}")
            results['fetcher_connection'] = False
        
        # Test parser (with minimal fetch)
        try:
            raw_data = self.fetcher.fetch_raw_data()
            parsed_df = self.parser.parse_raw_data(raw_data)
            results['parser_valid'] = self.parser.validate_parsed_data(parsed_df)
        except Exception as e:
            logger.error(f"ETR parser validation failed: {e}")
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
            logger.error(f"ETR standardizer validation failed: {e}")
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