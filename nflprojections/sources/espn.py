# nflprojections/espn.py
# -*- coding: utf-8 -*-
# Copyright (C) 2025 Eric Truett
# Licensed under the MIT License

"""
ESPN fantasy projections source implementation
"""

import logging
from typing import Dict, Optional, List, Any

from ..fetch.espn_fetcher import ESPNFetcher
from ..parse.espn_parser import ESPNParser
from ..standardize.base_standardizer import ProjectionStandardizer
from .projectionsource import ProjectionSource

logger = logging.getLogger(__name__)


class ESPNProjections(ProjectionSource):
    """ESPN fantasy projections using functional component architecture"""
    
    # Column mapping from ESPN to standardized format  
    DEFAULT_COLUMN_MAPPING = {
        'source_player_position': 'pos',
        'source_player_projection': 'proj',
        'source_team_code': 'team',
        'source_player_name': 'plyr',
        'season': 'season',  # Will be added by standardizer
        'week': 'week'       # Will be added by standardizer
    }
    
    def __init__(
        self,
        season: int = None,
        week: int = None,
        column_mapping: Dict[str, str] = None,
        use_schedule: bool = True,
        use_names: bool = True,
        timeout: int = 30,
        **kwargs
    ):
        """
        Initialize ESPN projections source
        
        Args:
            season: NFL season year
            week: NFL week (None for season projections)
            column_mapping: Custom column mapping 
            use_schedule: Whether to use schedule data for standardization
            use_names: Whether to standardize player/team names
            timeout: Request timeout in seconds
            **kwargs: Additional configuration
        """
        # Use default column mapping if none provided
        if column_mapping is None:
            column_mapping = self.DEFAULT_COLUMN_MAPPING.copy()
        
        # Create functional components
        fetcher = ESPNFetcher(season=season or 2025, timeout=timeout)
        parser = ESPNParser(season=season or 2025, week=week)
        standardizer = ProjectionStandardizer(
            column_mapping=column_mapping,
            season=season,
            week=week
        )
        
        # Initialize using composed mode of ProjectionSource
        super().__init__(
            fetcher=fetcher,
            parser=parser,
            standardizer=standardizer,
            source_name="espn",
            season=season,
            week=week,
            use_schedule=use_schedule,
            use_names=use_names,
            **kwargs
        )


class ESPNProjectionsRefactored:
    """Refactored ESPN projections using separate functional components"""
    
    # Default column mapping from ESPN to standardized format
    DEFAULT_COLUMN_MAPPING = {
        'source_player_position': 'pos',
        'source_player_projection': 'proj', 
        'source_team_code': 'team',
        'source_player_name': 'plyr',
        'season': 'season',  # Will be added by standardizer  
        'week': 'week'       # Will be added by standardizer
    }
    
    def __init__(
        self,
        season: int = None,
        week: int = None,
        column_mapping: Dict[str, str] = None,
        timeout: int = 30,
        **kwargs
    ):
        """
        Initialize ESPN projections with functional components
        
        Args:
            season: NFL season year (defaults to 2025)
            week: NFL week (None for season projections)
            column_mapping: Custom column mapping from ESPN to standard format
            timeout: Request timeout in seconds
            **kwargs: Additional configuration
        """
        self.season = season or 2025
        self.week = week
        self.timeout = timeout
        
        # Use default column mapping if none provided
        if column_mapping is None:
            column_mapping = self.DEFAULT_COLUMN_MAPPING.copy()
        
        # Create functional components
        self.fetcher = ESPNFetcher(season=self.season, timeout=timeout)
        self.parser = ESPNParser(season=self.season, week=week)
        self.standardizer = ProjectionStandardizer(
            column_mapping=column_mapping,
            season=season,
            week=week
        )
        
        logger.info(f"Initialized ESPN projections for season {self.season}, week {week}")

    def fetch_raw_data(self, season: int = None) -> Dict[str, Any]:
        """
        Fetch raw data using the fetcher component
        
        Args:
            season: Season to fetch (uses instance season if not provided)
            
        Returns:
            Raw ESPN API JSON data
        """
        return self.fetcher.fetch_raw_data(season=season)

    def parse_data(self, raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse raw data using the parser component
        
        Args:
            raw_data: Raw ESPN API JSON data
            
        Returns:
            List of dictionaries with parsed player data
        """
        return self.parser.parse_raw_data(raw_data)

    def standardize_data(self, parsed_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Standardize parsed data using the standardizer component
        
        Args:
            parsed_data: Parsed player data from ESPN
            
        Returns:
            List of dictionaries with standardized format
        """
        return self.standardizer.standardize(parsed_data)

    def data_pipeline(self, season: int = None) -> List[Dict[str, Any]]:
        """
        Execute the complete data pipeline: fetch -> parse -> standardize
        
        Args:
            season: Season to process (uses instance season if not provided)
            
        Returns:
            List of standardized player projections
        """
        logger.info(f"Running ESPN data pipeline for season {season or self.season}, week {self.week}")
        
        # Fetch raw data
        raw_data = self.fetch_raw_data(season=season)
        logger.debug(f"Fetched {len(raw_data.get('players', []))} players from ESPN API")
        
        # Parse raw data
        parsed_data = self.parse_data(raw_data)
        logger.debug(f"Parsed {len(parsed_data)} player records")
        
        # Standardize data
        standardized_data = self.standardize_data(parsed_data)
        logger.debug(f"Standardized {len(standardized_data)} player projections")
        
        return standardized_data

    def fetch_projections(self, season: int = None) -> List[Dict[str, Any]]:
        """
        Fetch and return standardized ESPN projections
        
        Args:
            season: Season to fetch (uses instance season if not provided)
            
        Returns:
            List of standardized player projections
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
        
        # Test parser with minimal fetch
        try:
            raw_data = self.fetcher.fetch_raw_data()
            parsed_data = self.parser.parse_raw_data(raw_data)
            results['parser_valid'] = self.parser.validate_parsed_data(parsed_data)
        except Exception as e:
            logger.error(f"Parser validation failed: {e}")
            results['parser_valid'] = False
        
        # Test standardizer
        try:
            # Create dummy data to test standardizer
            dummy_data = [{
                'source_player_name': 'Test Player',
                'source_player_position': 'QB',
                'source_team_code': 'KC',
                'source_player_projection': 20.5
            }]
            standardized = self.standardizer.standardize(dummy_data)
            results['standardizer_valid'] = len(standardized) > 0 and 'plyr' in standardized[0]
        except Exception as e:
            logger.error(f"Standardizer validation failed: {e}")
            results['standardizer_valid'] = False
        
        return results

    def get_pipeline_info(self) -> Dict[str, str]:
        """
        Get information about the data pipeline components
        
        Returns:
            Dictionary with component information
        """
        return {
            'fetcher': f"{self.fetcher.__class__.__name__} (ESPN API)",
            'parser': f"{self.parser.__class__.__name__} (season={self.season}, week={self.week})",
            'standardizer': f"{self.standardizer.__class__.__name__}",
            'source': 'ESPN Fantasy API',
            'season': str(self.season),
            'week': str(self.week) if self.week else 'Season'
        }