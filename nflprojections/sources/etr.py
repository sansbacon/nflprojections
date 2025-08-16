# nflprojections/etr.py
# -*- coding: utf-8 -*-
# Copyright (C) 2025 Eric Truett
# Licensed under the MIT License

"""
ETR (Establish The Run) fantasy football projections
Legacy-style implementation for backward compatibility
"""

import logging
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional

from .projectionsource import ProjectionSource


logger = logging.getLogger(__name__)


class ETRProjections(ProjectionSource):
    """Parser for ETR (Establish The Run) fantasy football projections"""
    
    # Column mapping from ETR format to standardized format
    DEFAULT_COLUMN_MAPPING = {
        'player': 'plyr',
        'position': 'pos', 
        'team': 'team',
        'fantasy_points': 'proj',
        'season': 'season',
        'week': 'week'
    }
    
    BASE_URL = "https://establishtherun.com/projections"
    
    def __init__(
        self,
        season: int = None,
        week: int = None,
        position: str = "all",
        scoring: str = "ppr",
        column_mapping: Dict[str, str] = None,
        use_schedule: bool = True,
        use_names: bool = True
    ):
        """
        Initialize ETR projections parser
        
        Args:
            season: NFL season year
            week: Week number for weekly projections (None for season)
            position: Position filter (all, qb, rb, wr, te, k, dst)
            scoring: Scoring format (ppr, half-ppr, standard)
            column_mapping: Column mapping dictionary
            use_schedule: Whether to add schedule information
            use_names: Whether to standardize player/team names
        """
        column_mapping = column_mapping or self.DEFAULT_COLUMN_MAPPING.copy()
        
        super().__init__(
            source_name="etr",
            column_mapping=column_mapping,
            season=season,
            week=week,
            use_schedule=use_schedule,
            use_names=use_names
        )
        
        self.position = position.lower()
        self.scoring = scoring.lower()
    
    def _build_url(self, season: int = None) -> str:
        """Build the URL for ETR projections"""
        season = season or self.season or 2025
        
        # Build URL path based on common fantasy site patterns
        url_parts = [self.BASE_URL]
        
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
        
        if params:
            param_str = '&'.join([f"{k}={v}" for k, v in params.items() if v is not None])
            return f"{base_url}?{param_str}"
        
        return base_url
    
    def _fetch_page(self, url: str) -> BeautifulSoup:
        """Fetch and parse the ETR projections page"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            logger.error(f"Error fetching ETR page: {e}")
            raise
    
    def _parse_projections_table(self, soup: BeautifulSoup) -> List[Dict]:
        """Parse the projections table from the HTML"""
        projections = []
        
        # Look for tables containing projection data
        tables = soup.find_all('table')
        
        for table in tables:
            # Get headers
            headers = []
            header_row = table.find('thead') or table.find('tr')
            if header_row:
                for th in header_row.find_all(['th', 'td']):
                    header_text = th.get_text(strip=True).lower()
                    headers.append(self._normalize_header(header_text))
            
            # Get data rows
            tbody = table.find('tbody')
            if tbody:
                rows = tbody.find_all('tr')
            else:
                rows = table.find_all('tr')[1:] if headers else table.find_all('tr')
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if not cells:
                    continue
                
                player_data = {}
                
                for i, cell in enumerate(cells):
                    text = cell.get_text(strip=True)
                    
                    if i == 0 and text:  # First column usually player info
                        player_info = self._parse_player_info(text)
                        player_data.update(player_info)
                    elif i < len(headers) and headers[i]:
                        # Map cell to normalized header
                        header = headers[i]
                        numeric_value = self._convert_to_numeric(text)
                        player_data[header] = numeric_value if numeric_value is not None else text
                
                if player_data.get('player'):
                    projections.append(player_data)
        
        return projections
    
    def _normalize_header(self, header: str) -> str:
        """Normalize header text to consistent format"""
        import re
        
        # Common header mappings for ETR
        header_mappings = {
            'player': 'player',
            'name': 'player',
            'pos': 'position',
            'position': 'position',
            'team': 'team',
            'tm': 'team',
            'fpts': 'fantasy_points',
            'fp': 'fantasy_points',
            'fantasy points': 'fantasy_points',
            'proj': 'fantasy_points',
            'projection': 'fantasy_points',
        }
        
        # Clean header
        cleaned = re.sub(r'[^a-z0-9\s]', '', header.lower().strip())
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return header_mappings.get(cleaned, cleaned)
    
    def _parse_player_info(self, text: str) -> Dict:
        """Parse player information from text"""
        import re
        
        player_data = {}
        
        # Pattern: "Player Name POS TEAM"
        pattern1 = r'^([A-Za-z\s\.\']+?)\s+([A-Z]{1,3})\s+([A-Z]{2,3})$'
        match = re.match(pattern1, text)
        if match:
            player_data['player'] = match.group(1).strip()
            player_data['position'] = match.group(2).strip()
            player_data['team'] = match.group(3).strip()
            return player_data
        
        # Pattern: "Player Name - POS - TEAM"
        pattern2 = r'^([A-Za-z\s\.\']+?)\s*-\s*([A-Z]{1,3})\s*-\s*([A-Z]{2,3})$'
        match = re.match(pattern2, text)
        if match:
            player_data['player'] = match.group(1).strip()
            player_data['position'] = match.group(2).strip()
            player_data['team'] = match.group(3).strip()
            return player_data
        
        # If no pattern matches, use as player name
        if text:
            player_data['player'] = text.strip()
        
        return player_data
    
    def _convert_to_numeric(self, value: str) -> Optional[float]:
        """Convert string value to numeric if possible"""
        import re
        
        if not value:
            return None
        
        # Remove common non-numeric characters
        cleaned = re.sub(r'[^\d\.\-]', '', value.strip())
        
        if not cleaned:
            return None
        
        try:
            if '.' in cleaned:
                return float(cleaned)
            else:
                return int(cleaned)
        except ValueError:
            return None
    
    def fetch_projections(self, season: int = None) -> List[Dict[str, Any]]:
        """
        Fetch ETR projections for the specified season
        
        Args:
            season: NFL season year
            
        Returns:
            List of dictionaries with player projections
        """
        url = self._build_url(season)
        logger.info(f"Fetching ETR projections from: {url}")
        
        soup = self._fetch_page(url)
        projections = self._parse_projections_table(soup)
        
        if not projections:
            logger.warning("No projections found on ETR page")
            return []
        
        # Apply column mapping and standardization
        standardized_projections = self._remap_columns(projections)
        
        return standardized_projections
    
    def _remap_columns(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remap columns from source format to standardized format"""
        remapped_data = []
        
        for row in data:
            remapped_row = {}
            
            for source_col, target_col in self.column_mapping.items():
                if source_col in row:
                    remapped_row[target_col] = row[source_col]
            
            # Add season and week if configured
            if self.season:
                remapped_row['season'] = self.season
            if self.week:
                remapped_row['week'] = self.week
            
            remapped_data.append(remapped_row)
        
        return remapped_data