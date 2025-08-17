# nflprojections/fantasypros_fetcher.py
# -*- coding: utf-8 -*-
# Copyright (C) 2025 Eric Truett
# Licensed under the MIT License

"""
FantasyPros specific fetcher implementation
"""

import logging
import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional, Union

from .base_fetcher import WebDataFetcher


logger = logging.getLogger(__name__)


class FantasyProsFetcher(WebDataFetcher):
    """Fetcher specifically for FantasyPros fantasy projections"""
    
    BASE_URL = "https://www.fantasypros.com/nfl/projections"
    DEFAULT_HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    # Position mapping to FantasyPros position codes
    POSITION_MAP = {
        'qb': 'qb',
        'rb': 'rb', 
        'wr': 'wr',
        'te': 'te',
        'k': 'k',
        'dst': 'dst',
        'defense': 'dst',
        'all': 'all'
    }
    
    # Scoring format mapping
    SCORING_MAP = {
        'ppr': 'PPR',
        'half': 'HALF',
        'half-ppr': 'HALF',
        'standard': 'STD',
        'std': 'STD'
    }
    
    def __init__(
        self,
        position: str = "qb",
        scoring: str = "ppr", 
        week: Union[str, int] = "draft",
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 30,
        **kwargs
    ):
        """
        Initialize FantasyPros fetcher
        
        Args:
            position: Position to fetch (qb, rb, wr, te, k, dst)
            scoring: Scoring format (ppr, half, standard)
            week: Week to fetch (draft, 1, 2, etc.)
            headers: Custom HTTP headers
            timeout: Request timeout in seconds
            **kwargs: Additional configuration
        """
        headers = headers or self.DEFAULT_HEADERS.copy()
        super().__init__(
            source_name="fantasypros",
            base_url=self.BASE_URL,
            headers=headers,
            **kwargs
        )
        
        self.position = self._normalize_position(position)
        self.scoring = self._normalize_scoring(scoring)
        self.week = str(week)
        self.timeout = timeout
    
    def _normalize_position(self, position: str) -> str:
        """Normalize position to FantasyPros format"""
        return self.POSITION_MAP.get(position.lower(), 'qb')
    
    def _normalize_scoring(self, scoring: str) -> str:
        """Normalize scoring format to FantasyPros format"""
        return self.SCORING_MAP.get(scoring.lower(), 'PPR')
    
    def build_url(self, position: str = None, scoring: str = None, week: Union[str, int] = None, **url_params) -> str:
        """
        Build FantasyPros projections URL with parameters
        
        Args:
            position: Position to fetch (overrides instance position)
            scoring: Scoring format (overrides instance scoring)
            week: Week to fetch (overrides instance week)
            **url_params: Additional URL parameters
            
        Returns:
            Complete URL for FantasyPros projections
        """
        position = self._normalize_position(position or self.position)
        scoring = self._normalize_scoring(scoring or self.scoring)
        week = str(week or self.week)
        
        # Build base URL with position
        url = f"{self.base_url}/{position}.php"
        
        # Build query parameters
        params = {'week': week}
        
        # Add scoring parameter for non-QB positions if not standard/draft
        if position != 'qb' and scoring != 'STD' and week != 'draft':
            params['scoring'] = scoring
        
        # Add any additional parameters
        params.update(url_params)
        
        # Build final URL
        if params:
            param_str = '&'.join([f"{k}={v}" for k, v in params.items()])
            url = f"{url}?{param_str}"
        
        return url
    
    def fetch_raw_data(self, position: str = None, scoring: str = None, week: Union[str, int] = None, **fetch_params) -> BeautifulSoup:
        """
        Fetch raw HTML data from FantasyPros projections page
        
        Args:
            position: Position to fetch (overrides instance position)
            scoring: Scoring format (overrides instance scoring)  
            week: Week to fetch (overrides instance week)
            **fetch_params: Additional parameters for URL building
            
        Returns:
            BeautifulSoup object with parsed HTML
        """
        url = self.build_url(position=position, scoring=scoring, week=week, **fetch_params)
        logger.info(f"Fetching FantasyPros projections from: {url}")
        
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
            
        except requests.RequestException as e:
            logger.error(f"Error fetching FantasyPros page: {e}")
            raise
    
    def validate_connection(self) -> bool:
        """
        Validate that FantasyPros is accessible
        
        Returns:
            True if connection is valid, False otherwise
        """
        try:
            url = self.build_url()
            response = requests.head(url, headers=self.headers, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"FantasyPros connection validation failed: {e}")
            return False