# nflprojections/espn_fetcher.py
# -*- coding: utf-8 -*-
# Copyright (C) 2025 Eric Truett
# Licensed under the MIT License

"""
ESPN API specific fetcher implementation
"""

import json
import logging
import requests
from typing import Dict, Optional, Any

from .base_fetcher import DataSourceFetcher


logger = logging.getLogger(__name__)


class ESPNFetcher(DataSourceFetcher):
    """Fetcher specifically for ESPN fantasy projections API"""
    
    def __init__(
        self,
        season: int = 2025,
        timeout: int = 30,
        **kwargs
    ):
        """
        Initialize ESPN fetcher
        
        Args:
            season: NFL season year
            timeout: Request timeout in seconds
            **kwargs: Additional configuration
        """
        super().__init__(source_name="espn", **kwargs)
        
        self.season = season
        self.timeout = timeout
        self._session = requests.Session()
    
    @property
    def api_url(self) -> str:
        """Build ESPN API URL for the season"""
        return f"https://fantasy.espn.com/apis/v3/games/ffl/seasons/{self.season}/segments/0/leaguedefaults/3"
    
    @property
    def default_headers(self) -> dict:
        """Default headers for ESPN API requests"""
        return {
            "authority": "fantasy.espn.com",
            "accept": "application/json",
            "x-fantasy-source": "kona",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36",
            "x-fantasy-platform": "kona-PROD-a9859dd5e813fa08e6946514bbb0c3f795a4ea23",
            "dnt": "1",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://fantasy.espn.com/football/players/projections",
            "accept-language": "en-US,en;q=0.9,ar;q=0.8",
            "if-none-match": "W/^\\^008956866aeb5b199ec8612a9e7576ed7^\\^",
            "x-fantasy-filter": json.dumps(self.xff)
        }
    
    @property
    def default_params(self) -> dict:
        """Default parameters for ESPN API requests"""
        return {"view": "kona_player_info"}
    
    @property
    def xff(self) -> dict:
        """Default x-fantasy-filter for ESPN API"""
        return {
            "players": {
                "limit": 1500,
                "sortDraftRanks": {
                    "sortPriority": 100,
                    "sortAsc": True,
                    "value": "PPR",
                }
            }
        }
    
    def fetch_raw_data(self, season: int = None, **fetch_params) -> Dict[str, Any]:
        """
        Fetch raw JSON data from ESPN API
        
        Args:
            season: Season to fetch (uses instance season if not provided)
            **fetch_params: Additional parameters (currently unused)
            
        Returns:
            Dict containing ESPN API JSON response
        """
        if season is not None:
            # Create temporary fetcher for different season
            temp_fetcher = ESPNFetcher(season=season, timeout=self.timeout)
            url = temp_fetcher.api_url
            headers = temp_fetcher.default_headers
        else:
            url = self.api_url
            headers = self.default_headers
            
        logger.info(f"Fetching ESPN projections from: {url}")
        
        try:
            response = self._session.get(
                url, 
                headers=headers, 
                params=self.default_params,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            # Check if response has content
            if not response.content:
                logger.error("ESPN API returned empty response")
                raise ValueError("ESPN API returned empty response")
            
            # Try to parse JSON with better error handling
            try:
                return response.json()
            except ValueError as json_error:
                # Log the actual response content for debugging (truncated to avoid too much noise)
                content_preview = response.text[:500] if response.text else "No content"
                logger.error(
                    f"ESPN API returned invalid JSON. Status: {response.status_code}, "
                    f"Content-Type: {response.headers.get('content-type', 'unknown')}, "
                    f"Content preview: {content_preview}"
                )
                raise ValueError(
                    f"ESPN API returned invalid JSON response. "
                    f"Status: {response.status_code}, Content-Type: {response.headers.get('content-type', 'unknown')}"
                ) from json_error
            
        except requests.RequestException as e:
            logger.error(f"Error fetching ESPN API data: {e}")
            raise
    
    def validate_connection(self) -> bool:
        """
        Validate that ESPN API is accessible
        
        Returns:
            True if connection is valid, False otherwise
        """
        try:
            response = self._session.head(self.api_url, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"ESPN API connection validation failed: {e}")
            return False