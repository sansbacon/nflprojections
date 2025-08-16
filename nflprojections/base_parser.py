# nflprojections/base_parser.py
# -*- coding: utf-8 -*-
# Copyright (C) 2025 Eric Truett
# Licensed under the MIT License

"""
Base classes for parsing data from different sources
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List
import pandas as pd


class DataSourceParser(ABC):
    """Abstract base class for parsing data from different sources"""
    
    def __init__(self, source_name: str, **kwargs):
        """
        Initialize the data parser
        
        Args:
            source_name: Name identifier for the data source
            **kwargs: Additional parser-specific configuration
        """
        self.source_name = source_name
        self.config = kwargs
    
    @abstractmethod
    def parse_raw_data(self, raw_data: Any) -> pd.DataFrame:
        """
        Parse raw data into a standardized DataFrame structure
        
        Args:
            raw_data: Raw data from the fetcher
            
        Returns:
            DataFrame with parsed data in source-specific column format
        """
        pass
    
    @abstractmethod
    def validate_parsed_data(self, df: pd.DataFrame) -> bool:
        """
        Validate that parsed data meets expected format
        
        Args:
            df: Parsed DataFrame
            
        Returns:
            True if data is valid, False otherwise
        """
        pass


class HTMLTableParser(DataSourceParser):
    """Parser for HTML table data"""
    
    def __init__(self, source_name: str, table_selector: str = "table", **kwargs):
        """
        Initialize HTML table parser
        
        Args:
            source_name: Name identifier for the data source
            table_selector: CSS selector to find the data table
            **kwargs: Additional configuration
        """
        super().__init__(source_name, **kwargs)
        self.table_selector = table_selector
    
    def parse_raw_data(self, raw_data) -> pd.DataFrame:
        """Parse HTML data into DataFrame"""
        if hasattr(raw_data, 'find_all'):  # BeautifulSoup object
            soup = raw_data
        else:  # String HTML
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(raw_data, 'html.parser')
        
        table_data = self.extract_table_data(soup)
        return pd.DataFrame(table_data) if table_data else pd.DataFrame()
    
    def validate_parsed_data(self, df: pd.DataFrame) -> bool:
        """Validate HTML table data"""
        return not df.empty and len(df.columns) > 0
    
    def extract_table_data(self, soup) -> List[Dict]:
        """
        Extract data from HTML table
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            List of dictionaries with table data
        """
        # This is a base implementation that subclasses can override
        table = soup.select_one(self.table_selector)
        if not table:
            return []
        
        # Extract headers if present
        headers = []
        header_row = table.find('thead') or table.find('tr')
        if header_row:
            headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
        
        # Extract data rows
        data = []
        rows = table.find_all('tr')[1:] if headers else table.find_all('tr')
        
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if cells:
                if headers:
                    row_data = {headers[i]: cell.get_text(strip=True) 
                               for i, cell in enumerate(cells) if i < len(headers)}
                else:
                    row_data = {f'col_{i}': cell.get_text(strip=True) 
                               for i, cell in enumerate(cells)}
                if row_data:
                    data.append(row_data)
        
        return data


class CSVParser(DataSourceParser):
    """Parser for CSV data"""
    
    def parse_raw_data(self, raw_data: str) -> pd.DataFrame:
        """Parse CSV string data into DataFrame"""
        from io import StringIO
        return pd.read_csv(StringIO(raw_data))
    
    def validate_parsed_data(self, df: pd.DataFrame) -> bool:
        """Validate CSV data has expected structure"""
        return not df.empty and len(df.columns) > 0


class JSONParser(DataSourceParser):
    """Parser for JSON data"""
    
    def parse_raw_data(self, raw_data: str) -> pd.DataFrame:
        """Parse JSON string data into DataFrame"""
        import json
        data = json.loads(raw_data)
        
        if isinstance(data, list):
            return pd.DataFrame(data)
        elif isinstance(data, dict):
            # Handle different JSON structures
            if 'data' in data:
                return pd.DataFrame(data['data'])
            else:
                return pd.DataFrame([data])
        else:
            raise ValueError("Unsupported JSON structure")
    
    def validate_parsed_data(self, df: pd.DataFrame) -> bool:
        """Validate JSON data has expected structure"""
        return not df.empty