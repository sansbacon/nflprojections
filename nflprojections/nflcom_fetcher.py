# nflprojections/nflcom_fetcher.py
# -*- coding: utf-8 -*-
# Copyright (C) 2025 Eric Truett
# Licensed under the MIT License

"""
NFL.com specific fetcher implementation
"""

import logging
import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional

from .base_fetcher import WebDataFetcher


logger = logging.getLogger(__name__)


class NFLComFetcher(WebDataFetcher):
    """Fetcher specifically for NFL.com fantasy projections"""
    
    BASE_URL = "https://fantasy.nfl.com/research/projections"
    DEFAULT_HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    def __init__(
        self,
        position: str = "0",
        stat_category: str = "projectedStats", 
        stat_type: str = "seasonProjectedStats",
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 30,
        **kwargs
    ):
        """
        Initialize NFL.com fetcher
        
        Args:
            position: Position filter (0=all, 1=QB, 2=RB, 3=WR, 4=TE, 5=K, 6=DST)
            stat_category: Category of stats to retrieve
            stat_type: Type of stats (season vs weekly)
            headers: Custom HTTP headers
            timeout: Request timeout in seconds
            **kwargs: Additional configuration
        """
        headers = headers or self.DEFAULT_HEADERS.copy()
        super().__init__(
            source_name="nfl.com",
            base_url=self.BASE_URL,
            headers=headers,
            **kwargs
        )
        
        self.position = position
        self.stat_category = stat_category
        self.stat_type = stat_type
        self.timeout = timeout
    
    def build_url(self, season: int = None, **url_params) -> str:
        """
        Build NFL.com projections URL with parameters
        
        Args:
            season: NFL season year
            **url_params: Additional URL parameters
            
        Returns:
            Complete URL for NFL.com projections
        """
        season = season or 2025
        
        params = {
            'position': self.position,
            'statCategory': self.stat_category,
            'statSeason': season,
            'statType': self.stat_type
        }
        params.update(url_params)
        
        return super().build_url(**params)
    
    def fetch_raw_data(self, season: int = None, **fetch_params) -> BeautifulSoup:
        """
        Fetch raw HTML data from NFL.com projections page
        
        Args:
            season: Season to fetch (defaults to 2025)
            **fetch_params: Additional parameters for URL building
            
        Returns:
            BeautifulSoup object with parsed HTML
        """
        url = self.build_url(season=season, **fetch_params)
        logger.info(f"Fetching projections from: {url}")
        
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
            
        except requests.RequestException as e:
            logger.error(f"Error fetching NFL.com page: {e}")
            raise
    
    def validate_connection(self) -> bool:
        """
        Validate that NFL.com is accessible
        
        Returns:
            True if connection is valid, False otherwise
        """
        try:
            url = self.build_url()
            response = requests.head(url, headers=self.headers, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Connection validation failed: {e}")
            return False