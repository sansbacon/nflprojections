# nflprojections/rotogrinders_parser.py
# -*- coding: utf-8 -*-
# Copyright (C) 2025 Eric Truett
# Licensed under the MIT License

"""
Rotogrinders-specific parser implementation
"""

import json
import logging
import re
from typing import Dict, List, Any

from .base_parser import DataSourceParser


logger = logging.getLogger(__name__)


class RotogrindersJSONParser(DataSourceParser):
    """Parser for Rotogrinders HTML containing embedded JSON projections"""
    
    # Regex pattern to extract projections JSON from HTML
    PROJ_PATTERN = re.compile(
        r'selectedExpertPackage: ({.*?],"title":.*?"product_id".*?}),\s+serviceURL', 
        re.MULTILINE | re.DOTALL
    )
    
    def __init__(self, **kwargs):
        """
        Initialize Rotogrinders JSON parser
        
        Args:
            **kwargs: Additional configuration
        """
        super().__init__(source_name="rotogrinders", **kwargs)
    
    def parse_raw_data(self, raw_data: str) -> List[Dict[str, Any]]:
        """
        Parse HTML data to extract embedded JSON projections
        
        Args:
            raw_data: Raw HTML string from Rotogrinders
            
        Returns:
            List of dictionaries with projection data
            
        Raises:
            ValueError: If no projections data found in HTML
            json.JSONDecodeError: If JSON parsing fails
        """
        try:
            projections = self._extract_projections_json(raw_data)
            
            # Convert to list of dictionaries with lowercase column names
            if not projections:
                logger.warning("No projections found in HTML data")
                return []
            
            # Normalize column names to lowercase
            normalized_projections = []
            for proj in projections:
                if isinstance(proj, dict):
                    normalized_proj = {k.lower(): v for k, v in proj.items()}
                    normalized_projections.append(normalized_proj)
                else:
                    logger.warning(f"Unexpected projection format: {type(proj)}")
            
            logger.info(f"Successfully parsed {len(normalized_projections)} projections")
            return normalized_projections
            
        except Exception as e:
            logger.error(f"Error parsing Rotogrinders data: {e}")
            raise
    
    def _extract_projections_json(self, html: str, pattern: re.Pattern = None) -> List[Dict[str, Any]]:
        """
        Extract projections JSON from HTML using regex pattern
        
        Args:
            html: Raw HTML string
            pattern: Regex pattern to use (defaults to class PROJ_PATTERN)
            
        Returns:
            List of projection dictionaries
            
        Raises:
            ValueError: If no match found
            json.JSONDecodeError: If JSON parsing fails
        """
        if pattern is None:
            pattern = self.PROJ_PATTERN
        
        match = pattern.search(html)
        if not match:
            raise ValueError("No projections data found in HTML")
        
        json_str = match.group(1)
        try:
            data = json.loads(json_str)
            if isinstance(data, dict) and 'data' in data:
                return data['data']
            else:
                logger.warning("Unexpected JSON structure, returning raw data")
                return data if isinstance(data, list) else [data]
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            raise
    
    def validate_parsed_data(self, data: List[Dict[str, Any]]) -> bool:
        """
        Validate that parsed Rotogrinders data has expected structure
        
        Args:
            data: Parsed list of dictionaries
            
        Returns:
            True if data is valid, False otherwise
        """
        if not data:
            return False
        
        # Check that we have a list of dictionaries
        if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
            return False
        
        # Check for expected columns in at least one record
        expected_cols = {'player', 'fpts'}  # Core required columns
        for record in data:
            # Convert keys to lowercase for checking
            record_keys = {k.lower() for k in record.keys()}
            if expected_cols.issubset(record_keys):
                return True
        
        logger.warning("No records found with expected columns (player, fpts)")
        return False