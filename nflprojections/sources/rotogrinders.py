# nflprojections/rotogrinders.py
# -*- coding: utf-8 -*-
# Copyright (C) 2025 Eric Truett
# Licensed under the MIT License

"""
Rotogrinders projections using functional components
"""

import logging
from typing import Dict, Optional, List, Any

from ..fetch.rotogrinders_fetcher import RotogrindersWebFetcher
from ..parse.rotogrinders_parser import RotogrindersJSONParser
from ..standardize.base_standardizer import ProjectionStandardizer


logger = logging.getLogger(__name__)


class RotogrindersProjections:
    """Rotogrinders projections using separate functional components"""
    
    # Default column mapping from Rotogrinders format to standard format
    DEFAULT_COLUMN_MAPPING = {
        'player': 'plyr',
        'fpts': 'proj',
        'team': 'team',
        'opp': 'opp',
        'ceil': 'ceil', 
        'floor': 'floor',
        'playerid': 'source_player_id',
        'salary': 'salary',
        'pos': 'pos',
        'season': 'season',
        'week': 'week'
    }
    
    def __init__(
        self,
        season: int = None,
        week: int = None,
        column_mapping: Dict[str, str] = None,
        use_schedule: bool = True,
        use_names: bool = True,
        **kwargs
    ):
        """
        Initialize Rotogrinders projections
        
        NOTE: Subscription is required. You must have firefox installed 
        and have logged in to rotogrinders in that browser profile.
        
        Args:
            season: NFL season year
            week: NFL week number
            column_mapping: Custom column mapping override
            use_schedule: Whether to use nflschedule for current season/week
            use_names: Whether to standardize player/team names
            **kwargs: Additional configuration for fetcher
        """
        # Initialize fetcher
        self.fetcher = RotogrindersWebFetcher(**kwargs)
        
        # Initialize parser
        self.parser = RotogrindersJSONParser()
        
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
    
    def fetch_raw_data(self, params: Optional[Dict[str, str]] = None, **fetch_params) -> str:
        """
        Fetch raw data from Rotogrinders LineupHQ.
        
        Args:
            params: URL parameters (site, slate, date, post, projections)
            **fetch_params: Additional parameters merged with params
            
        Returns:
            Raw HTML string containing projection data
            
        Example:
            params = {
                'site': 'draftkings', 
                'slate': '53019', 
                'date': '2021-09-12',
                'post': '2009661'    
            }
        """
        return self.fetcher.fetch_raw_data(params=params, **fetch_params)
    
    def parse_data(self, raw_data: str) -> List[Dict[str, Any]]:
        """
        Parse raw Rotogrinders HTML data into structured format.
        
        Args:
            raw_data: Raw HTML data to parse
            
        Returns:
            List of dictionaries with parsed projection data
        """
        return self.parser.parse_raw_data(raw_data)
    
    def standardize_data(self, parsed_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Standardize parsed Rotogrinders data to common format.
        
        Args:
            parsed_data: List of dictionaries with parsed data
            
        Returns:
            List of dictionaries with standardized data
        """
        return self.standardizer.standardize(parsed_data)
    
    def data_pipeline(self, params: Optional[Dict[str, str]] = None, **fetch_params) -> List[Dict[str, Any]]:
        """
        Execute the complete data pipeline: fetch -> parse -> standardize.
        
        Args:
            params: URL parameters for Rotogrinders request
            **fetch_params: Additional parameters merged with params
            
        Returns:
            List of dictionaries with standardized projections
            
        Example:
            params = {
                'site': 'draftkings', 
                'slate': '53019', 
                'date': '2021-09-12',
                'post': '2009661'    
            }
        """
        try:
            # Step 1: Fetch raw data
            raw_data = self.fetch_raw_data(params=params, **fetch_params)
            
            # Step 2: Parse raw data
            parsed_data = self.parse_data(raw_data)
            
            # Step 3: Standardize parsed data
            standardized_data = self.standardize_data(parsed_data)
            
            logger.info(f"Successfully processed {len(standardized_data)} Rotogrinders projections")
            return standardized_data
            
        except Exception as e:
            logger.error(f"Error processing Rotogrinders projections: {e}")
            return []

    def fetch_projections(self, params: Optional[Dict[str, str]] = None, **fetch_params) -> List[Dict[str, Any]]:
        """
        Fetch and parse Rotogrinders projections using functional components.
        
        This method is maintained for backward compatibility and delegates to data_pipeline.
        
        Args:
            params: URL parameters for Rotogrinders request
            **fetch_params: Additional parameters merged with params
            
        Returns:
            List of dictionaries with standardized projections
        """
        return self.data_pipeline(params=params, **fetch_params)
    
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
            logger.error(f"Fetcher validation failed: {e}")
            results['fetcher_connection'] = False
        
        # Test parser (with dummy data since we need params for real fetch)
        try:
            dummy_html = '''
            selectedExpertPackage: {"data":[{"Player":"Test Player","FPTS":"20.5","Team":"KC"}],"title":"test","product_id":"123"}, serviceURL
            '''
            parsed_data = self.parser.parse_raw_data(dummy_html)
            results['parser_valid'] = self.parser.validate_parsed_data(parsed_data)
        except Exception as e:
            logger.error(f"Parser validation failed: {e}")
            results['parser_valid'] = False
        
        # Test standardizer
        try:
            # Create dummy data to test standardizer
            dummy_data = [{
                'player': 'Test Player',
                'fpts': '20.5',
                'team': 'KC',
                'pos': 'QB'
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