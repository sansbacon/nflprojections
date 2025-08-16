# nflprojections/base_fetcher.py
# -*- coding: utf-8 -*-
# Copyright (C) 2025 Eric Truett
# Licensed under the MIT License

"""
Base classes for fetching data from different sources
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class DataSourceFetcher(ABC):
    """Abstract base class for fetching data from different sources"""
    
    def __init__(self, source_name: str, **kwargs):
        """
        Initialize the data fetcher
        
        Args:
            source_name: Name identifier for the data source
            **kwargs: Additional source-specific configuration
        """
        self.source_name = source_name
        self.config = kwargs
    
    @abstractmethod
    def fetch_raw_data(self, **fetch_params) -> Any:
        """
        Fetch raw data from the source
        
        Args:
            **fetch_params: Parameters specific to the fetch operation
            
        Returns:
            Raw data in source-specific format (HTML, JSON, CSV, etc.)
        """
        pass
    
    @abstractmethod
    def validate_connection(self) -> bool:
        """
        Validate that the data source is accessible
        
        Returns:
            True if connection is valid, False otherwise
        """
        pass


class WebDataFetcher(DataSourceFetcher):
    """Base class for fetching data from web sources"""
    
    def __init__(self, source_name: str, base_url: str, headers: Optional[Dict[str, str]] = None, **kwargs):
        """
        Initialize web data fetcher
        
        Args:
            source_name: Name identifier for the data source
            base_url: Base URL for the web source
            headers: HTTP headers to include in requests
            **kwargs: Additional configuration
        """
        super().__init__(source_name, **kwargs)
        self.base_url = base_url
        self.headers = headers or {}
        
    def build_url(self, **url_params) -> str:
        """
        Build URL with parameters
        
        Args:
            **url_params: Parameters to build into URL
            
        Returns:
            Complete URL string
        """
        if not url_params:
            return self.base_url
        
        param_str = '&'.join([f"{k}={v}" for k, v in url_params.items()])
        return f"{self.base_url}?{param_str}"
    
    def fetch_raw_data(self, **fetch_params) -> Any:
        """Default implementation for web fetching"""
        import requests
        url = self.build_url(**fetch_params)
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.text
    
    def validate_connection(self) -> bool:
        """Default implementation for web connection validation"""
        import requests
        try:
            response = requests.head(self.base_url, headers=self.headers, timeout=10)
            return response.status_code == 200
        except Exception:
            return False


class FileDataFetcher(DataSourceFetcher):
    """Base class for fetching data from file sources"""
    
    def __init__(self, source_name: str, file_path: str, **kwargs):
        """
        Initialize file data fetcher
        
        Args:
            source_name: Name identifier for the data source  
            file_path: Path to the data file
            **kwargs: Additional configuration
        """
        super().__init__(source_name, **kwargs)
        self.file_path = file_path
    
    def fetch_raw_data(self, **fetch_params) -> str:
        """Default implementation for file fetching"""
        with open(self.file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def validate_connection(self) -> bool:
        """Check if file exists and is readable"""
        from pathlib import Path
        path = Path(self.file_path)
        return path.exists() and path.is_file()