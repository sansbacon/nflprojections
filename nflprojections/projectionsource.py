# nflprojections/nflprojections/nflprojections.py
# -*- coding: utf-8 -*-
# Copyright (C) 2020 Eric Truett
# Licensed under the MIT License

import logging
from pathlib import Path
from typing import Dict, List, Optional, Union

import pandas as pd

# Optional imports
try:
    import nflnames
except ImportError:
    nflnames = None

try:
    import nflschedule
except ImportError:
    nflschedule = None

from .scoring import Scorer


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

    def fetch_projections(self, **kwargs) -> pd.DataFrame:
        """
        Fetch projections using the composed functional pipeline.
        
        Args:
            **kwargs: Parameters to pass to the fetcher
            
        Returns:
            DataFrame with standardized projections
            
        Raises:
            NotImplementedError: If not in composed mode (legacy compatibility)
        """
        if not self.composed_mode:
            raise NotImplementedError(
                "fetch_projections requires composed mode with fetcher, parser, and standardizer. "
                "For legacy mode, this method should be implemented by subclasses."
            )
        
        if not all([self.fetcher, self.parser, self.standardizer]):
            raise ValueError("Fetcher, parser, and standardizer are all required for fetch_projections")
        
        try:
            # Step 1: Fetch raw data
            raw_data = self.fetcher.fetch_raw_data(**kwargs)
            
            # Step 2: Parse raw data
            if hasattr(self.parser, 'parse_raw_data'):
                parsed_data = self.parser.parse_raw_data(raw_data)
            else:
                # Handle case where parser returns DataFrame directly
                parsed_data = self.parser.parse(raw_data)
            
            # Convert list of dicts to DataFrame if needed
            if isinstance(parsed_data, list):
                parsed_df = pd.DataFrame(parsed_data)
            else:
                parsed_df = parsed_data
            
            # Step 3: Standardize parsed data
            if self.use_names and nflnames:
                standardized_df = self.standardizer.standardize(
                    parsed_df,
                    standardize_player_name=nflnames.standardize_player_name,
                    standardize_position=nflnames.standardize_positions,
                    standardize_team_code=nflnames.standardize_team_code
                )
            else:
                standardized_df = self.standardizer.standardize(parsed_df)
            
            return standardized_df
            
        except Exception as e:
            logging.error(f"Error in projection pipeline: {e}")
            return pd.DataFrame()
    
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
                dummy_data = pd.DataFrame([{
                    'player': 'Test Player',
                    'position': 'QB',
                    'team': 'KC',
                    'fantasy_points': 20.5
                }])
                standardized = self.standardizer.standardize(dummy_data)
                results['standardizer_valid'] = not standardized.empty
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

    def standardize_players(self, names: Union[List[str], 'pd.Series']) -> Union[List[str], 'pd.Series']:
        if not self.use_names:
            return names
        if isinstance(names, (list, tuple, set)):
            return [nflnames.standardize_player_name(n) for n in names]
        return names.apply(nflnames.standardize_player_name)

    def standardize_positions(self, positions: Union[List[str], 'pd.Series']) -> Union[List[str], 'pd.Series']:
        if not self.use_names:
            return positions
        if isinstance(positions, (list, tuple, set)):
            return [nflnames.standardize_positions(pos) for pos in positions]
        return positions.apply(nflnames.standardize_positions)

    def standardize_teams(self, teams: Union[List[str], 'pd.Series']) -> Union[List[str], 'pd.Series']:
        if not self.use_names:
            return teams
        if isinstance(teams, (list, tuple, set)):
            return [nflnames.standardize_team_code(t) for t in teams]
        return teams.apply(nflnames.standardize_team_code)