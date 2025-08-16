# nflprojections/fantasylife.py
# -*- coding: utf-8 -*-
# Copyright (C) 2025 Eric Truett
# Licensed under the MIT License

"""
Module for parsing FantasyLife fantasy football projections using functional components

Example usage:
    from nflprojections import FantasyLifeProjections
    
    # Fetch projections from CSV file
    fl = FantasyLifeProjections(file_path="/path/to/fantasy_football_projections.csv")
    df = fl.fetch_projections()
    
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

from ..fetch.fantasylife_fetcher import FantasyLifeFetcher
from ..parse.fantasylife_parser import FantasyLifeParser
from ..standardize.base_standardizer import ProjectionStandardizer


logger = logging.getLogger(__name__)


class FantasyLifeProjections:
    """FantasyLife projections using functional components architecture"""
    
    # Default column mapping from FantasyLife CSV format to standard format
    DEFAULT_COLUMN_MAPPING = {
        'Player': 'plyr',
        'Position': 'pos', 
        'Team': 'team',
        'Fantasy Points': 'proj',
        'Season': 'season',
        'Week': 'week'
    }
    
    def __init__(
        self,
        file_path: str,
        season: int = None,
        week: int = None,
        column_mapping: Dict[str, str] = None,
        use_schedule: bool = True,
        use_names: bool = True,
        **kwargs
    ):
        """
        Initialize FantasyLife projections using functional components
        
        Args:
            file_path: Path to the FantasyLife CSV projection file
            season: NFL season year (will be inferred from file if not provided)
            week: NFL week number (will be inferred from file if not provided)
            column_mapping: Custom column mapping override
            use_schedule: Whether to use nflschedule for current season/week
            use_names: Whether to standardize player/team names
            **kwargs: Additional configuration
        """
        # Initialize fetcher
        self.fetcher = FantasyLifeFetcher(
            file_path=file_path,
            **kwargs
        )
        
        # Initialize parser
        self.parser = FantasyLifeParser()
        
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
        
        # Store file path for reference
        self.file_path = file_path
    
    @property
    def column_mapping(self):
        """Backward compatibility property for accessing column mapping"""
        return self.standardizer.column_mapping
    
    def fetch_raw_data(self) -> str:
        """
        Fetch raw CSV data using the fetcher component
        
        Returns:
            Raw CSV data from FantasyLife file
        """
        if self.fetcher is None:
            raise ValueError("Fetcher is required for fetch_raw_data")
        return self.fetcher.fetch_raw_data()
    
    def parse_data(self, raw_data: str) -> List[Dict[str, Any]]:
        """
        Parse raw CSV data using the parser component
        
        Args:
            raw_data: Raw CSV data from FantasyLife fetcher
            
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
    
    def data_pipeline(self) -> List[Dict[str, Any]]:
        """
        Execute the complete data pipeline: fetch -> parse -> standardize
        
        Returns:
            List of standardized player projections
        """
        logger.info(f"Running FantasyLife data pipeline for file: {self.file_path}")
        
        # Fetch raw data
        raw_data = self.fetch_raw_data()
        
        # Parse raw data
        parsed_data = self.parse_data(raw_data)
        logger.debug(f"Parsed {len(parsed_data)} player records")
        
        # Standardize data
        standardized_data = self.standardize_data(parsed_data)
        logger.debug(f"Standardized {len(standardized_data)} player projections")
        
        return standardized_data

    def fetch_projections(self) -> List[Dict[str, Any]]:
        """
        Fetch and return standardized FantasyLife projections
        
        Returns:
            List of standardized player projections
        """
        return self.data_pipeline()
    
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
        
        # Test parser with sample data if file is accessible
        if results.get('fetcher_connection', False):
            try:
                raw_data = self.fetch_raw_data()
                parsed_data = self.parse_data(raw_data)
                results['parser_valid'] = len(parsed_data) > 0
            except Exception as e:
                logger.error(f"Parser validation failed: {e}")
                results['parser_valid'] = False
        else:
            results['parser_valid'] = False
        
        # Test standardizer
        if results.get('parser_valid', False):
            try:
                sample_data = [{'Player': 'Test Player', 'Position': 'QB', 'Team': 'TST', 'Fantasy Points': 10.0, 'Season': 2024, 'Week': 1}]
                standardized = self.standardizer.standardize(sample_data)
                results['standardizer_valid'] = len(standardized) > 0 and 'plyr' in standardized[0]
            except Exception as e:
                logger.error(f"Standardizer validation failed: {e}")
                results['standardizer_valid'] = False
        else:
            results['standardizer_valid'] = False
        
        return results
    
    def get_pipeline_info(self) -> Dict[str, str]:
        """
        Get information about the data pipeline components
        
        Returns:
            Dictionary with component information
        """
        return {
            'fetcher': f"{type(self.fetcher).__name__} (file: {getattr(self.fetcher, 'file_path', 'unknown')})",
            'parser': type(self.parser).__name__,
            'standardizer': type(self.standardizer).__name__,
            'season': str(self.season),
            'week': str(self.week),
            'source': 'fantasylife'
        }