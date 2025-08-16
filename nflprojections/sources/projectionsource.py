# nflprojections/nflprojections/nflprojections.py
# -*- coding: utf-8 -*-
# Copyright (C) 2020 Eric Truett
# Licensed under the MIT License

import logging
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

# Optional imports
try:
    import nflnames
except ImportError:
    nflnames = None

try:
    import nflschedule
except ImportError:
    nflschedule = None

from ..scoring.scoring import Scorer


class ProjectionSource:
    """
    Composed class for projections that combines fetcher, parser, and standardizer components.
    
    This class follows the functional architecture pattern by composing separate
    components for fetching, parsing, and standardizing projection data.
    """
    REQUIRED_MAPPED_COLUMNS = {'season', 'week', 'plyr', 'pos', 'team', 'proj'}
    VALID_SLATE_NAMES = {'main', 'early', 'late', 'all', 'tsd', 'ssd', 'msd', 'season', 'playoffs', 'bestball'}
    VALID_FORMATS = {'csv', 'json', 'pkl', 'parquet'}

    def __init__(
        self,
        fetcher=None,
        parser=None,
        standardizer=None,
        source_name: str = None,
        column_mapping: Dict[str, str] = None,
        slate_name: str = None,
        season: int = None,
        week: int = None,
        use_schedule: bool = True,
        use_names: bool = True
    ):
        """
        Initialize ProjectionSource with functional components or legacy parameters.
        
        Args:
            fetcher: DataSourceFetcher instance for retrieving raw data
            parser: DataSourceParser instance for parsing raw data  
            standardizer: DataStandardizer instance for standardizing data
            source_name: Name of the projection source (legacy compatibility)
            column_mapping: Column mapping dict (legacy compatibility)
            slate_name: Slate name (legacy compatibility)
            season: Season number
            week: Week number
            use_schedule: Whether to use nflschedule for current season/week
            use_names: Whether to standardize player/team names
        """
        # New functional composition approach
        if fetcher is not None or parser is not None or standardizer is not None:
            self.fetcher = fetcher
            self.parser = parser
            self.standardizer = standardizer
            self.composed_mode = True
            
            # Set source name from fetcher if available
            self.projections_source = source_name or (fetcher.source_name if fetcher else "unknown")
            self.slate_name = slate_name
            
            # Set season/week from standardizer if available, otherwise use parameters
            if standardizer and hasattr(standardizer, 'season'):
                self.season = standardizer.season or season
                self.week = standardizer.week or week
            else:
                # Handle optional schedule
                if use_schedule and nflschedule:
                    self.season = season if season is not None else nflschedule.current_season()
                    self.week = week if week is not None else nflschedule.current_week()
                else:
                    self.season = season
                    self.week = week
        
        # Legacy compatibility mode
        else:
            self.composed_mode = False
            self.fetcher = None
            self.parser = None
            self.standardizer = None
            
            # Legacy initialization
            if source_name is None:
                raise ValueError("source_name is required when not using composed mode")
            if column_mapping is None:
                raise ValueError("column_mapping is required when not using composed mode")
                
            self.projections_source = source_name
            self.slate_name = slate_name

            # Validate column mappings for legacy mode
            assert self.REQUIRED_MAPPED_COLUMNS.issubset(set(column_mapping.values()))
            self.column_mapping = column_mapping

            # Handle optional schedule
            if use_schedule and nflschedule:
                self.season = season if season is not None else nflschedule.current_season()
                self.week = week if week is not None else nflschedule.current_week()
            else:
                self.season = season
                self.week = week

        # Handle optional name standardization
        self.use_names = use_names and nflnames is not None

    def fetch_raw_data(self, **kwargs) -> Any:
        """
        Fetch raw data from the data source.
        
        Args:
            **kwargs: Parameters to pass to the fetcher
            
        Returns:
            Raw data from the fetcher
            
        Raises:
            NotImplementedError: If not in composed mode
            ValueError: If fetcher is not available
        """
        if not self.composed_mode:
            raise NotImplementedError(
                "fetch_raw_data requires composed mode with fetcher component."
            )
        
        if not self.fetcher:
            raise ValueError("Fetcher is required for fetch_raw_data")
        
        return self.fetcher.fetch_raw_data(**kwargs)
    
    def parse_data(self, raw_data: Any) -> List[Dict[str, Any]]:
        """
        Parse raw data into structured format.
        
        Args:
            raw_data: Raw data to parse
            
        Returns:
            List of dictionaries with parsed data
            
        Raises:
            NotImplementedError: If not in composed mode
            ValueError: If parser is not available
        """
        if not self.composed_mode:
            raise NotImplementedError(
                "parse_data requires composed mode with parser component."
            )
        
        if not self.parser:
            raise ValueError("Parser is required for parse_data")
        
        # Parse raw data
        if hasattr(self.parser, 'parse_raw_data'):
            parsed_data = self.parser.parse_raw_data(raw_data)
        else:
            # Handle case where parser returns data directly
            parsed_data = self.parser.parse(raw_data)
        
        # Ensure parsed data is a list of dictionaries
        if not isinstance(parsed_data, list):
            # Assume it's a single record if not a list
            parsed_data = [parsed_data] if parsed_data else []
        
        return parsed_data
    
    def standardize_data(self, parsed_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Standardize parsed data to common format.
        
        Args:
            parsed_data: List of dictionaries with parsed data
            
        Returns:
            List of dictionaries with standardized data
            
        Raises:
            NotImplementedError: If not in composed mode
            ValueError: If standardizer is not available
        """
        if not self.composed_mode:
            raise NotImplementedError(
                "standardize_data requires composed mode with standardizer component."
            )
        
        if not self.standardizer:
            raise ValueError("Standardizer is required for standardize_data")
        
        # Standardize parsed data
        if self.use_names and nflnames:
            standardized_data = self.standardizer.standardize(
                parsed_data,
                standardize_player_name=nflnames.standardize_player_name,
                standardize_position=nflnames.standardize_positions,
                standardize_team_code=nflnames.standardize_team_code
            )
        else:
            standardized_data = self.standardizer.standardize(parsed_data)
        
        return standardized_data
    
    def data_pipeline(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Execute the complete data pipeline: fetch -> parse -> standardize.
        
        Args:
            **kwargs: Parameters to pass to the fetcher
            
        Returns:
            List of dictionaries with standardized projections
            
        Raises:
            NotImplementedError: If not in composed mode (legacy compatibility)
        """
        if not self.composed_mode:
            raise NotImplementedError(
                "data_pipeline requires composed mode with fetcher, parser, and standardizer. "
                "For legacy mode, this method should be implemented by subclasses."
            )
        
        if not all([self.fetcher, self.parser, self.standardizer]):
            raise ValueError("Fetcher, parser, and standardizer are all required for data_pipeline")
        
        try:
            # Step 1: Fetch raw data
            raw_data = self.fetch_raw_data(**kwargs)
            
            # Step 2: Parse raw data
            parsed_data = self.parse_data(raw_data)
            
            # Step 3: Standardize parsed data
            standardized_data = self.standardize_data(parsed_data)
            
            return standardized_data
            
        except Exception as e:
            logging.error(f"Error in projection pipeline: {e}")
            return []

    def fetch_projections(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Fetch projections using the composed functional pipeline.
        
        This method is maintained for backward compatibility and delegates to data_pipeline.
        
        Args:
            **kwargs: Parameters to pass to the fetcher
            
        Returns:
            List of dictionaries with standardized projections
            
        Raises:
            NotImplementedError: If not in composed mode (legacy compatibility)
        """
        return self.data_pipeline(**kwargs)
    
    def validate_data_pipeline(self) -> Dict[str, bool]:
        """
        Validate that all components of the data pipeline are working.
        
        Returns:
            Dictionary with validation results for each component
            
        Raises:
            NotImplementedError: If not in composed mode
        """
        if not self.composed_mode:
            raise NotImplementedError("Pipeline validation requires composed mode")
        
        results = {}
        
        # Test fetcher
        if self.fetcher:
            try:
                results['fetcher_connection'] = self.fetcher.validate_connection()
            except Exception as e:
                logging.error(f"Fetcher validation failed: {e}")
                results['fetcher_connection'] = False
        else:
            results['fetcher_connection'] = False
        
        # Test parser
        if self.parser and self.fetcher:
            try:
                # Use a minimal fetch to test parsing
                raw_data = self.fetcher.fetch_raw_data()
                if hasattr(self.parser, 'parse_raw_data'):
                    parsed_data = self.parser.parse_raw_data(raw_data)
                    results['parser_valid'] = self.parser.validate_parsed_data(parsed_data) if hasattr(self.parser, 'validate_parsed_data') else True
                else:
                    parsed_data = self.parser.parse(raw_data)
                    results['parser_valid'] = not (parsed_data is None or (hasattr(parsed_data, 'empty') and parsed_data.empty))
            except Exception as e:
                logging.error(f"Parser validation failed: {e}")
                results['parser_valid'] = False
        else:
            results['parser_valid'] = False
        
        # Test standardizer
        if self.standardizer:
            try:
                # Create dummy data to test standardizer
                dummy_data = [{
                    'player': 'Test Player',
                    'position': 'QB',
                    'team': 'KC',
                    'fantasy_points': 20.5
                }]
                standardized = self.standardizer.standardize(dummy_data)
                results['standardizer_valid'] = len(standardized) > 0
            except Exception as e:
                logging.error(f"Standardizer validation failed: {e}")
                results['standardizer_valid'] = False
        else:
            results['standardizer_valid'] = False
        
        return results
    
    def get_pipeline_info(self) -> Dict[str, str]:
        """
        Get information about the configured pipeline components.
        
        Returns:
            Dictionary with component information
            
        Raises:
            NotImplementedError: If not in composed mode
        """
        if not self.composed_mode:
            raise NotImplementedError("Pipeline info requires composed mode")
        
        info = {
            'source_name': self.projections_source,
            'season': str(self.season),
            'week': str(self.week),
            'composed_mode': 'True'
        }
        
        if self.fetcher:
            info['fetcher'] = f"{self.fetcher.__class__.__name__} - {getattr(self.fetcher, 'source_name', 'unknown')}"
        
        if self.parser:
            info['parser'] = f"{self.parser.__class__.__name__} - {getattr(self.parser, 'source_name', 'unknown')}"
        
        if self.standardizer:
            info['standardizer'] = f"{self.standardizer.__class__.__name__}"
            if hasattr(self.standardizer, 'column_mapping'):
                info['column_mapping'] = str(self.standardizer.column_mapping)
        
        return info

    def standardize_players(self, names: List[str]) -> List[str]:
        if not self.use_names:
            return names
        return [nflnames.standardize_player_name(n) for n in names]

    def standardize_positions(self, positions: List[str]) -> List[str]:
        if not self.use_names:
            return positions
        return [nflnames.standardize_positions(pos) for pos in positions]

    def standardize_teams(self, teams: List[str]) -> List[str]:
        if not self.use_names:
            return teams
        return [nflnames.standardize_team_code(t) for t in teams]