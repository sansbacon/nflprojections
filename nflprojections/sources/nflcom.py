# nflprojections/nflprojections/nflcom.py
# -*- coding: utf-8 -*-
# Copyright (C) 2020 Eric Truett
# Licensed under the MIT License

"""
Module for parsing NFL.com fantasy football projections using refactored functional components

Example usage:
    from nflprojections import NFLComProjections
    
    # Fetch all positions for 2025 season
    nfl = NFLComProjections(season=2025)
    df = nfl.fetch_projections()
    
    # Fetch only quarterbacks
    qb_nfl = NFLComProjections(season=2025, position="1")
    qb_df = qb_nfl.fetch_projections()
    
    # The returned DataFrame has standardized columns:
    # - plyr: Player name
    # - pos: Position  
    # - team: Team abbreviation
    # - proj: Fantasy points projection
    # - season: Season year
    # - week: Week number
"""

import logging
from typing import Dict, List, Optional, Any

from ..fetch.nflcom_fetcher import NFLComFetcher
from ..parse.nflcom_parser import NFLComParser
from ..standardize.base_standardizer import ProjectionStandardizer


logger = logging.getLogger(__name__)


class NFLComProjections:
    """NFL.com projections using functional components architecture"""
    
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
        Initialize NFL.com projections using functional components
        
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
        Fetch raw data using the fetcher component
        
        Args:
            season: Season to fetch (uses instance season if not provided)
            
        Returns:
            Raw data from NFL.com fetcher
        """
        if self.fetcher is None:
            raise ValueError("Fetcher is required for fetch_raw_data")
        return self.fetcher.fetch_raw_data(season=season)
    
    def parse_data(self, raw_data: Any) -> List[Dict[str, Any]]:
        """
        Parse raw data using the parser component
        
        Args:
            raw_data: Raw data from NFL.com fetcher
            
        Returns:
            List of dictionaries with parsed player data
        """
        if self.parser is None:
            raise ValueError("Parser is required for parse_data")
        
        # Try refactored method first, fallback to legacy if needed
        if hasattr(self.parser, 'parse_raw_data'):
            return self.parser.parse_raw_data(raw_data)
        else:
            return self.parser.parse(raw_data)
    
    def standardize_data(self, parsed_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Standardize parsed data using the standardizer component
        
        Args:
            parsed_data: Parsed data from parser
            
        Returns:
            List of dictionaries with standardized format
        """
        if self.standardizer is None:
            raise ValueError("Standardizer is required for standardize_data")
        return self.standardizer.standardize(parsed_data)
    
    def data_pipeline(self, season: int = None) -> List[Dict[str, Any]]:
        """
        Execute the complete data pipeline: fetch -> parse -> standardize
        
        Args:
            season: Season to process (uses instance season if not provided)
            
        Returns:
            List of standardized player projections
        """
        logger.info(f"Running NFL.com data pipeline for season {season or self.season}, week {self.week}")
        
        # Fetch raw data
        raw_data = self.fetch_raw_data(season=season)
        
        # Parse raw data
        parsed_data = self.parse_data(raw_data)
        logger.debug(f"Parsed {len(parsed_data)} player records")
        
        # Standardize data
        standardized_data = self.standardize_data(parsed_data)
        logger.debug(f"Standardized {len(standardized_data)} player projections")
        
        return standardized_data

    def fetch_projections(self, season: int = None) -> List[Dict[str, Any]]:
        """
        Fetch and return standardized NFL.com projections
        
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
        Get information about the data pipeline components
        
        Returns:
            Dictionary with component information
        """
        info = {}
        if hasattr(self, 'fetcher') and self.fetcher:
            info['fetcher'] = f"{self.fetcher.__class__.__name__}"
            
        if hasattr(self, 'parser') and self.parser:
            info['parser'] = f"{self.parser.__class__.__name__}"
            
        if hasattr(self, 'standardizer') and self.standardizer:
            info['standardizer'] = f"{self.standardizer.__class__.__name__}"
            if hasattr(self.standardizer, 'column_mapping'):
                info['column_mapping'] = str(self.standardizer.column_mapping)
        
        return info