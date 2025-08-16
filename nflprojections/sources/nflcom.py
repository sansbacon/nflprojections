# nflprojections/nflprojections/nflcom.py
# -*- coding: utf-8 -*-
# Copyright (C) 2020 Eric Truett
# Licensed under the MIT License

"""
Module for parsing NFL.com fantasy football projections

Example usage:
    from nflprojections import NFLComProjections
    
    # Fetch all positions for 2025 season
    nfl = NFLComProjections(season=2025)
    df = nfl.fetch_projections()
    
    # Fetch only quarterbacks
    qb_nfl = NFLComProjections(season=2025, position="1")
    qb_df = qb_nfl.fetch_projections()
    
    # The returned DataFrame has standardized columns:
    # - plyr: Player name
    # - pos: Position  
    # - team: Team abbreviation
    # - proj: Fantasy points projection
    # - season: Season year
    # - week: Week number
"""

import logging
import re
from typing import Dict, List, Optional, Union, Any

import requests
from bs4 import BeautifulSoup

from .projectionsource import ProjectionSource


logger = logging.getLogger(__name__)


class NFLComProjections(ProjectionSource):
    """Parser for NFL.com fantasy football projections"""
    
    # Column mapping from NFL.com to standardized format
    DEFAULT_COLUMN_MAPPING = {
        'player': 'plyr',
        'position': 'pos', 
        'team': 'team',
        'fantasy_points': 'proj',
        'season': 'season',
        'week': 'week'
    }
    
    BASE_URL = "https://fantasy.nfl.com/research/projections"
    
    def __init__(
        self,
        season: int = None,
        week: int = None,
        position: str = "0",  # 0 = all positions
        stat_category: str = "projectedStats",
        stat_type: str = "seasonProjectedStats",
        column_mapping: Dict[str, str] = None,
        use_schedule: bool = True,
        use_names: bool = True
    ):
        """
        Initialize NFL.com projections parser
        
        Args:
            season: NFL season year
            week: NFL week number  
            position: Position filter (0=all, 1=QB, 2=RB, 3=WR, 4=TE, 5=K, 6=DST)
            stat_category: Category of stats to retrieve
            stat_type: Type of stats (season vs weekly)
            column_mapping: Custom column mapping override
            use_schedule: Whether to use nflschedule for current season/week
            use_names: Whether to standardize player/team names
        """
        self.position = position
        self.stat_category = stat_category
        self.stat_type = stat_type
        
        # Use default column mapping if none provided
        if column_mapping is None:
            column_mapping = self.DEFAULT_COLUMN_MAPPING.copy()
            
        super().__init__(
            source_name="nfl.com",
            column_mapping=column_mapping,
            slate_name="season",
            season=season,
            week=week,
            use_schedule=use_schedule,
            use_names=use_names
        )
    
    def _build_url(self, season: int = None) -> str:
        """Build the URL for NFL.com projections"""
        season = season or self.season or 2025
        
        params = {
            'position': self.position,
            'statCategory': self.stat_category,
            'statSeason': season,
            'statType': self.stat_type
        }
        
        param_str = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{self.BASE_URL}?{param_str}"
    
    def _fetch_page(self, url: str) -> BeautifulSoup:
        """Fetch and parse the NFL.com projections page"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            logger.error(f"Error fetching NFL.com page: {e}")
            raise
    
    def _parse_projections_table(self, soup: BeautifulSoup) -> List[Dict]:
        """Parse the projections table from the HTML"""
        projections = []
        
        # Look for the projections table
        # NFL.com typically uses specific classes or IDs for their tables
        table = soup.find('table', class_=re.compile(r'projections|stats|fantasy'))
        
        if not table:
            # Try alternative selectors
            table = soup.find('table')
            
        if not table:
            logger.warning("No projections table found on page")
            return projections
            
        # Parse table headers to understand column structure
        headers = []
        header_row = table.find('thead')
        if header_row:
            headers = [th.get_text(strip=True).lower() for th in header_row.find_all(['th', 'td'])]
        
        # Parse table body
        tbody = table.find('tbody') or table
        rows = tbody.find_all('tr')
        
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) < 3:  # Skip header rows or incomplete rows
                continue
                
            player_data = {}
            
            # Parse each cell based on position or content
            for i, cell in enumerate(cells):
                text = cell.get_text(strip=True)
                
                # Extract player name (usually first column or contains player info)
                if i == 0 or 'player' in headers[i] if i < len(headers) else False:
                    # Clean player name, removing extra info
                    player_name = re.sub(r'\s+', ' ', text)
                    player_name = re.sub(r'\([^)]*\)', '', player_name).strip()
                    player_data['player'] = player_name
                    
                    # Extract position and team from player cell if present
                    if '-' in text:
                        parts = text.split('-')
                        if len(parts) >= 2:
                            player_data['position'] = parts[-1].strip()
                            if len(parts) >= 3:
                                player_data['team'] = parts[-2].strip()
                
                # Look for numeric fantasy points projection
                elif re.match(r'^\d+\.?\d*$', text):
                    if 'fantasy_points' not in player_data:
                        player_data['fantasy_points'] = float(text)
                
                # Parse specific columns if headers available
                elif i < len(headers):
                    header = headers[i]
                    if 'team' in header and not player_data.get('team'):
                        player_data['team'] = text
                    elif 'pos' in header and not player_data.get('position'):
                        player_data['position'] = text
                    elif 'point' in header or 'proj' in header:
                        try:
                            player_data['fantasy_points'] = float(text)
                        except ValueError:
                            pass
            
            # Only add if we have minimum required data
            if player_data.get('player') and player_data.get('fantasy_points') is not None:
                # Add season and week info
                player_data['season'] = self.season
                player_data['week'] = self.week
                projections.append(player_data)
        
        logger.info(f"Parsed {len(projections)} player projections")
        return projections
    
    def fetch_projections(self, season: int = None) -> List[Dict[str, Any]]:
        """
        Fetch and parse NFL.com projections
        
        Args:
            season: Season to fetch (defaults to instance season)
            
        Returns:
            List of dictionaries with standardized projections
        """
        url = self._build_url(season)
        logger.info(f"Fetching projections from: {url}")
        
        soup = self._fetch_page(url)
        projections_data = self._parse_projections_table(soup)
        
        if not projections_data:
            logger.warning("No projection data found")
            return []
        
        # Standardize column names using mapping
        projections_data = self._remap_columns(projections_data)
        
        # Standardize data using base class methods
        for row in projections_data:
            if 'plyr' in row and row['plyr']:
                standardized_names = self.standardize_players([row['plyr']])
                row['plyr'] = standardized_names[0] if standardized_names else row['plyr']
            if 'pos' in row and row['pos']:
                standardized_positions = self.standardize_positions([row['pos']])
                row['pos'] = standardized_positions[0] if standardized_positions else row['pos']
            if 'team' in row and row['team']:
                standardized_teams = self.standardize_teams([row['team']])
                row['team'] = standardized_teams[0] if standardized_teams else row['team']
            
            # Ensure required columns exist
            for col in self.REQUIRED_MAPPED_COLUMNS:
                if col not in row:
                    if col == 'season':
                        row[col] = self.season
                    elif col == 'week':
                        row[col] = self.week
                    else:
                        row[col] = None
        
        return projections_data
    
    def _remap_columns(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remap columns from source format to standardized format"""
        result = []
        for row in data:
            new_row = {}
            for key, value in row.items():
                new_key = self.column_mapping.get(key, key)
                new_row[new_key] = value
            result.append(new_row)
        return result