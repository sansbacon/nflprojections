# nflprojections/rotogrinders_fetcher.py
# -*- coding: utf-8 -*-
# Copyright (C) 2025 Eric Truett
# Licensed under the MIT License

"""
Rotogrinders-specific fetcher implementation
"""

import logging
from typing import Dict, Optional, Any

from .base_fetcher import WebDataFetcher

try:
    import browser_cookie3
    import requests
    _HAS_ROTOGRINDERS_DEPS = True
except ImportError:
    browser_cookie3 = None
    requests = None
    _HAS_ROTOGRINDERS_DEPS = False

logger = logging.getLogger(__name__)


class RotogrindersWebFetcher(WebDataFetcher):
    """Fetcher for Rotogrinders LineupHQ projections using browser authentication"""
    
    def __init__(self, **kwargs):
        """
        Initialize Rotogrinders fetcher with browser cookie authentication
        
        NOTE: Subscription is required. You must have firefox installed 
        and have logged in to rotogrinders in that browser profile.
        This library does not access anything 'extra' that user didn't buy.
        It automates projections download for an authorized user (via browser_cookie3).
        
        Args:
            **kwargs: Additional configuration
        
        Raises:
            ImportError: If required dependencies (browser_cookie3) are not installed
        """
        if not _HAS_ROTOGRINDERS_DEPS:
            raise ImportError(
                "browser_cookie3 is required for RotogrindersWebFetcher. "
                "Install with: pip install browser_cookie3"
            )
        super().__init__(
            source_name="rotogrinders",
            base_url="https://rotogrinders.com/lineuphq/nfl",
            **kwargs
        )
        
        # Initialize session with browser cookies for authentication
        self._session = requests.Session()
        try:
            self._session.cookies.update(browser_cookie3.firefox())
        except Exception as e:
            logger.warning(f"Failed to load Firefox cookies: {e}")
    
    def construct_url(self, params: Dict[str, str]) -> str:
        """
        Constructs URL given params following rotogrinders format
        
        Args:
            params: Dictionary containing site, slate, date, post parameters
                   Expected keys: 'site', 'slate', 'projections', 'date', 'post'
                   
        Returns:
            Formatted URL string
            
        Example:
            params = {
                'site': 'draftkings', 
                'slate': '53019', 
                'projections': 'grid', 
                'date': '2021-09-12',
                'post': '2009661'    
            }
        """
        url_template = 'https://rotogrinders.com/lineuphq/nfl?site={site}&slate={slate}&projections=grid&date={date}&post={post}'
        return url_template.format(**params)
    
    def fetch_raw_data(self, params: Optional[Dict[str, str]] = None, **fetch_params) -> str:
        """
        Fetch raw HTML data from Rotogrinders LineupHQ
        
        Args:
            params: URL parameters for the rotogrinders request
            **fetch_params: Additional parameters merged with params
            
        Returns:
            Raw HTML string containing the projection data
            
        Raises:
            ValueError: If required parameters are missing
            requests.RequestException: If request fails
        """
        # Merge params and fetch_params
        request_params = {}
        if params:
            request_params.update(params)
        request_params.update(fetch_params)
        
        # Validate required parameters
        required_params = {'site', 'slate', 'date', 'post'}
        missing_params = required_params - set(request_params.keys())
        if missing_params:
            raise ValueError(f"Missing required parameters: {missing_params}")
        
        # Default projections to 'grid' if not specified
        if 'projections' not in request_params:
            request_params['projections'] = 'grid'
        
        # Construct URL and fetch data
        url = self.construct_url(request_params)
        
        logger.info(f"Fetching Rotogrinders data from: {url}")
        
        try:
            response = self._session.get(url, headers=self.headers)
            response.raise_for_status()
            
            logger.info(f"Successfully fetched {len(response.text)} characters from Rotogrinders")
            return response.text
            
        except requests.RequestException as e:
            logger.error(f"Failed to fetch Rotogrinders data: {e}")
            raise
    
    def validate_connection(self) -> bool:
        """
        Validate connection to Rotogrinders (basic connectivity check)
        
        Returns:
            True if base connection is valid, False otherwise
        """
        try:
            response = self._session.head("https://rotogrinders.com", timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Connection validation failed: {e}")
            return False