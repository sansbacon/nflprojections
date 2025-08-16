# nflprojections/nflcom_refactored.py
# -*- coding: utf-8 -*-
# Copyright (C) 2025 Eric Truett
# Licensed under the MIT License

"""
Refactored NFL.com projections using functional components
"""

import logging
from typing import Dict, Optional, List, Any

from ..fetch.nflcom_fetcher import NFLComFetcher
from ..parse.nflcom_parser import NFLComParser
from ..standardize.base_standardizer import ProjectionStandardizer


logger = logging.getLogger(__name__)


class NFLComProjectionsRefactored:
    """Refactored NFL.com projections using separate functional components"""
    
    # Default column mapping from NFL.com format to standard format
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
        position: str = "0",
        stat_category: str = "projectedStats",
        stat_type: str = "seasonProjectedStats",
        column_mapping: Dict[str, str] = None,
        use_schedule: bool = True,
        use_names: bool = True,
        **kwargs
    ):
        """
        Initialize refactored NFL.com projections
        
        Args:
            season: NFL season year
            week: NFL week number
            position: Position filter (0=all, 1=QB, 2=RB, 3=WR, 4=TE, 5=K, 6=DST)
            stat_category: Category of stats to retrieve
            stat_type: Type of stats (season vs weekly)
            column_mapping: Custom column mapping override
            use_schedule: Whether to use nflschedule for current season/week
            use_names: Whether to standardize player/team names
            **kwargs: Additional configuration for fetcher
        """
        # Initialize fetcher
        self.fetcher = NFLComFetcher(
            position=position,
            stat_category=stat_category,
            stat_type=stat_type,
            **kwargs
        )
        
        # Initialize parser
        self.parser = NFLComParser()
        
        # Initialize standardizer
        column_mapping = column_mapping or self.DEFAULT_COLUMN_MAPPING.copy()
        self.standardizer = ProjectionStandardizer(
            column_mapping=column_mapping,
            season=season,
            week=week
        )
        
        self.season = self.standardizer.season
        self.week = self.standardizer.week
        # Store the use_names flag for later use in standardization
        self.use_names = use_names
    
    def fetch_raw_data(self, season: int = None) -> Any:
        """
        Fetch raw data from NFL.com.
        
        Args:
            season: Season to fetch (defaults to instance season)
            
        Returns:
            Raw data from the fetcher
        """
        return self.fetcher.fetch_raw_data(season=season)
    
    def parse_data(self, raw_data: Any) -> List[Dict[str, Any]]:
        """
        Parse raw NFL.com data into structured format.
        
        Args:
            raw_data: Raw data to parse
            
        Returns:
            List of dictionaries with parsed data
        """
        return self.parser.parse_raw_data(raw_data)
    
    def standardize_data(self, parsed_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Standardize parsed NFL.com data to common format.
        
        Args:
            parsed_data: List of dictionaries with parsed data
            
        Returns:
            List of dictionaries with standardized data
        """
        return self.standardizer.standardize(parsed_data)
    
    def data_pipeline(self, season: int = None) -> List[Dict[str, Any]]:
        """
        Execute the complete data pipeline: fetch -> parse -> standardize.
        
        Args:
            season: Season to fetch (defaults to instance season)
            
        Returns:
            List of dictionaries with standardized projections
        """
        try:
            # Step 1: Fetch raw data
            raw_data = self.fetch_raw_data(season=season)
            
            # Step 2: Parse raw data
            parsed_data = self.parse_data(raw_data)
            
            # Step 3: Standardize parsed data
            standardized_data = self.standardize_data(parsed_data)
            
            logger.info(f"Successfully processed {len(standardized_data)} projections")
            return standardized_data
            
        except Exception as e:
            logger.error(f"Error processing NFL.com projections: {e}")
            return []

    def fetch_projections(self, season: int = None) -> List[Dict[str, Any]]:
        """
        Fetch and parse NFL.com projections using functional components.
        
        This method is maintained for backward compatibility and delegates to data_pipeline.
        
        Args:
            season: Season to fetch (defaults to instance season)
            
        Returns:
            List of dictionaries with standardized projections
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
            logger.error(f"Fetcher validation failed: {e}")
            results['fetcher_connection'] = False
        
        # Test parser (with minimal fetch)
        try:
            raw_data = self.fetcher.fetch_raw_data()
            parsed_df = self.parser.parse_raw_data(raw_data)
            results['parser_valid'] = self.parser.validate_parsed_data(parsed_df)
        except Exception as e:
            logger.error(f"Parser validation failed: {e}")
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
            logger.error(f"Standardizer validation failed: {e}")
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
            'column_mapping': str(self.standardizer.column_mapping)
        }