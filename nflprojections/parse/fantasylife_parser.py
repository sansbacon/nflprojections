# nflprojections/fantasylife_parser.py
# -*- coding: utf-8 -*-
# Copyright (C) 2025 Eric Truett
# Licensed under the MIT License

"""
FantasyLife specific parser implementation for CSV data
"""

import logging
import pandas as pd
from typing import Dict, List, Any
from io import StringIO

from .base_parser import DataSourceParser


logger = logging.getLogger(__name__)


class FantasyLifeParser(DataSourceParser):
    """Parser specifically for FantasyLife CSV projection data"""
    
    def __init__(self, **kwargs):
        """
        Initialize FantasyLife parser
        
        Args:
            **kwargs: Additional configuration
        """
        super().__init__(
            source_name="fantasylife",
            **kwargs
        )
    
    def parse_raw_data(self, raw_data: str) -> List[Dict[str, Any]]:
        """
        Parse FantasyLife CSV data into list of dictionaries
        
        Args:
            raw_data: Raw CSV content as string
            
        Returns:
            List of dictionaries with parsed projection data
        """
        try:
            # Read CSV data using pandas
            df = pd.read_csv(StringIO(raw_data))
            
            # Convert to list of dictionaries
            projections_data = df.to_dict('records')
            
            # Apply transformations to each record
            for record in projections_data:
                self._transform_record(record)
            
            logger.info(f"Parsed {len(projections_data)} FantasyLife projections")
            
            # Validate the parsed data
            if not self.validate_parsed_data(projections_data):
                logger.error("FantasyLife data validation failed")
                return []
            
            return projections_data
            
        except pd.errors.EmptyDataError:
            logger.error("FantasyLife CSV file is empty")
            return []
        except pd.errors.ParserError as e:
            logger.error(f"Error parsing FantasyLife CSV: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error parsing FantasyLife data: {e}")
            return []
    
    def _transform_record(self, record: Dict[str, Any]) -> None:
        """
        Apply transformations to a single record in-place
        
        Args:
            record: Dictionary representing a single row of data
        """
        # 1. Rename '#' to 'Jersey_Number'
        if '#' in record:
            record['Jersey_Number'] = record.pop('#')
        
        # 2. Convert 'Comp%' from percentage string to decimal
        if 'Comp%' in record and isinstance(record['Comp%'], str):
            comp_pct = record['Comp%']
            if comp_pct.endswith('%'):
                try:
                    # Remove '%' and convert to decimal (e.g., '69%' -> 0.69)
                    record['Comp%'] = float(comp_pct[:-1]) / 100.0
                except (ValueError, TypeError):
                    logger.warning(f"Could not convert Comp% '{comp_pct}' to decimal")
        
        # 3. Convert 'P Yds' from comma-separated string to numeric
        if 'P Yds' in record and isinstance(record['P Yds'], str):
            p_yds = record['P Yds']
            try:
                # Remove commas and convert to float (e.g., '3,735.5' -> 3735.5)
                record['P Yds'] = float(p_yds.replace(',', ''))
            except (ValueError, TypeError):
                logger.warning(f"Could not convert P Yds '{p_yds}' to numeric")
    
    
    def validate_parsed_data(self, data: List[Dict[str, Any]]) -> bool:
        """
        Validate that parsed FantasyLife data meets expected format
        
        Args:
            data: List of dictionaries with parsed data
            
        Returns:
            True if data is valid, False otherwise
        """
        if not data or not isinstance(data, list):
            return False
        
        # Check that we have at least one record
        if len(data) == 0:
            return False
        
        # Check that each record is a dictionary
        for record in data:
            if not isinstance(record, dict):
                return False
        
        # Check for expected column names (case-insensitive)
        first_record = data[0]
        expected_columns = {'player', 'position', 'team', 'fantasy points', 'season', 'week'}
        actual_columns = {col.lower().strip() for col in first_record.keys()}
        
        # Allow for some flexibility in column names
        if not expected_columns.issubset(actual_columns):
            logger.warning(f"Expected columns {expected_columns} not all found in {actual_columns}")
            # Still return True for now, let standardizer handle column mapping
        
        return True