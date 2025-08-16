# nflprojections/etr_fetcher.py
# -*- coding: utf-8 -*-
# Copyright (C) 2025 Eric Truett
# Licensed under the MIT License

"""
ETR (Establish The Run) specific fetcher implementation
"""

import logging
import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional

from .base_fetcher import WebDataFetcher


logger = logging.getLogger(__name__)


class ETRFetcher(WebDataFetcher):
    """Fetcher specifically for ETR (Establish The Run) fantasy projections"""
    
    BASE_URL = "https://establishtherun.com/projections"
    DEFAULT_HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    def __init__(
        self,
        position: str = "all",
        scoring: str = "ppr",
        week: int = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 30,
        **kwargs
    ):
        """
        Initialize ETR fetcher
        
        Args:
            position: Position filter (all, qb, rb, wr, te, k, dst)
            scoring: Scoring format (ppr, half-ppr, standard)
            week: Week number for weekly projections (None for season)
            headers: Custom HTTP headers
            timeout: Request timeout in seconds
            **kwargs: Additional configuration
        """
        headers = headers or self.DEFAULT_HEADERS.copy()
        super().__init__(
            source_name="etr",
            base_url=self.BASE_URL,
            headers=headers,
            **kwargs
        )
        
        self.position = position.lower()
        self.scoring = scoring.lower()
        self.week = week
        self.timeout = timeout
    
    def build_url(self, season: int = None, **url_params) -> str:
        """
        Build ETR projections URL with parameters
        
        Args:
            season: NFL season year
            **url_params: Additional URL parameters
            
        Returns:
            Complete URL for ETR projections
        """
        season = season or 2025
        
        # Build URL path based on common fantasy site patterns
        url_parts = [self.base_url]
        
        # Add season if different from current
        if season != 2025:
            url_parts.append(str(season))
        
        # Add week if specified (weekly projections)
        if self.week:
            url_parts.append(f"week-{self.week}")
        
        # Add position filter
        if self.position and self.position != "all":
            url_parts.append(self.position)
        
        # Join URL parts
        base_url = "/".join(url_parts)
        
        # Add query parameters
        params = {
            'scoring': self.scoring,
        }
        params.update(url_params)
        
        if params:
            param_str = '&'.join([f"{k}={v}" for k, v in params.items() if v is not None])
            return f"{base_url}?{param_str}"
        
        return base_url
    
    def fetch_raw_data(self, season: int = None, **fetch_params) -> BeautifulSoup:
        """
        Fetch raw HTML data from ETR projections page
        
        Args:
            season: Season to fetch (defaults to 2025)
            **fetch_params: Additional parameters for URL building
            
        Returns:
            BeautifulSoup object with parsed HTML
        """
        url = self.build_url(season=season, **fetch_params)
        logger.info(f"Fetching ETR projections from: {url}")
        
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
            
        except requests.RequestException as e:
            logger.error(f"Error fetching ETR page: {e}")
            raise
    
    def validate_connection(self) -> bool:
        """
        Validate that ETR is accessible
        
        Returns:
            True if connection is valid, False otherwise
        """
        try:
            url = self.build_url()
            response = requests.head(url, headers=self.headers, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"ETR connection validation failed: {e}")
            return False