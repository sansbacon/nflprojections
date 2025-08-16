# nflprojections/fantasylife_fetcher.py
# -*- coding: utf-8 -*-
# Copyright (C) 2025 Eric Truett
# Licensed under the MIT License

"""
FantasyLife specific fetcher implementation for CSV files
"""

import logging
from pathlib import Path
from typing import Optional

from .base_fetcher import FileDataFetcher


logger = logging.getLogger(__name__)


class FantasyLifeFetcher(FileDataFetcher):
    """Fetcher specifically for FantasyLife CSV projection files"""
    
    def __init__(
        self,
        file_path: str,
        **kwargs
    ):
        """
        Initialize FantasyLife CSV fetcher
        
        Args:
            file_path: Path to the FantasyLife CSV projection file
            **kwargs: Additional configuration
        """
        super().__init__(
            source_name="fantasylife",
            file_path=file_path,
            **kwargs
        )
    
    def fetch_raw_data(self, **fetch_params) -> str:
        """
        Fetch raw CSV data from FantasyLife file
        
        Args:
            **fetch_params: Additional parameters (unused for file sources)
            
        Returns:
            Raw CSV content as string
        """
        logger.info(f"Fetching FantasyLife projections from: {self.file_path}")
        
        try:
            return super().fetch_raw_data(**fetch_params)
        except FileNotFoundError as e:
            logger.error(f"FantasyLife CSV file not found: {e}")
            raise
        except Exception as e:
            logger.error(f"Error reading FantasyLife CSV file: {e}")
            raise
    
    def validate_connection(self) -> bool:
        """
        Validate that the CSV file exists and is readable
        
        Returns:
            True if file is accessible, False otherwise
        """
        result = super().validate_connection()
        if result:
            # Additional validation to ensure it's a CSV file
            path = Path(self.file_path)
            if not path.suffix.lower() in ['.csv', '.txt']:
                logger.warning(f"File {self.file_path} may not be a CSV file (extension: {path.suffix})")
        return result