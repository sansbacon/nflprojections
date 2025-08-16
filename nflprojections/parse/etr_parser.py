# nflprojections/etr_parser.py
# -*- coding: utf-8 -*-
# Copyright (C) 2025 Eric Truett
# Licensed under the MIT License

"""
ETR (Establish The Run) specific parser implementation
"""

import logging
import re
from typing import Dict, List, Any
from bs4 import BeautifulSoup

from .base_parser import HTMLTableParser


logger = logging.getLogger(__name__)


class ETRParser(HTMLTableParser):
    """Parser specifically for ETR (Establish The Run) fantasy projections HTML"""
    
    def __init__(self, **kwargs):
        """
        Initialize ETR parser
        
        Args:
            **kwargs: Additional configuration
        """
        super().__init__(
            source_name="etr",
            table_selector="table",
            **kwargs
        )
    
    def parse_raw_data(self, raw_data: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Parse ETR HTML data into list of dictionaries
        
        Args:
            raw_data: BeautifulSoup object with ETR HTML
            
        Returns:
            List of dictionaries with parsed projection data
        """
        projections_data = self._parse_projections_table(raw_data)
        
        if not projections_data:
            logger.warning("No projection data found in ETR HTML")
            return []
        
        return projections_data
    
    def _parse_projections_table(self, soup: BeautifulSoup) -> List[Dict]:
        """
        Parse the projections table from ETR HTML
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            List of dictionaries with player projection data
        """
        projections = []
        
        # Look for different possible table structures
        tables = soup.find_all('table')
        for table in tables:
            data = self._extract_table_from_etr_structure(table)
            if data:
                projections.extend(data)
        
        # If no tables found, try alternative parsing methods
        if not projections:
            projections = self._extract_from_alternative_structure(soup)
        
        return projections
    
    def _extract_table_from_etr_structure(self, table) -> List[Dict]:
        """Extract data from standard ETR table structure"""
        data = []
        
        # Get headers - ETR commonly uses table headers for column identification
        headers = []
        header_row = table.find('thead') or table.find('tr')
        if header_row:
            for th in header_row.find_all(['th', 'td']):
                header_text = th.get_text(strip=True).lower()
                # Normalize common header variations
                header_text = self._normalize_header(header_text)
                headers.append(header_text)
        
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
                
                if i == 0 and text:  # First column is usually player info
                    player_info = self._parse_player_info(text)
                    player_data.update(player_info)
                elif i < len(headers) and headers[i]:
                    # Map cell to header
                    header = headers[i]
                    # Convert numeric values
                    numeric_value = self._convert_to_numeric(text)
                    player_data[header] = numeric_value if numeric_value is not None else text
            
            # Additional parsing for cells without clear headers
            if not headers:
                player_data.update(self._parse_headerless_row(cells))
            
            if player_data.get('player') or player_data.get('name'):
                # Ensure consistent player field naming
                if 'name' in player_data and 'player' not in player_data:
                    player_data['player'] = player_data['name']
                data.append(player_data)
        
        return data
    
    def _normalize_header(self, header: str) -> str:
        """Normalize header text to consistent format"""
        # Common header mappings for ETR
        header_mappings = {
            'player': 'player',
            'name': 'player',
            'pos': 'position',
            'position': 'position',
            'team': 'team',
            'tm': 'team',
            'opp': 'opponent',
            'opponent': 'opponent',
            'fpts': 'fantasy_points',
            'fp': 'fantasy_points',
            'fantasy points': 'fantasy_points',
            'proj': 'fantasy_points',
            'projection': 'fantasy_points',
            'att': 'attempts',
            'attempts': 'attempts',
            'yds': 'yards',
            'yards': 'yards',
            'td': 'touchdowns',
            'tds': 'touchdowns',
            'touchdowns': 'touchdowns',
            'rec': 'receptions',
            'receptions': 'receptions',
            'tgt': 'targets',
            'targets': 'targets',
            'int': 'interceptions',
            'interceptions': 'interceptions',
            'fum': 'fumbles',
            'fumbles': 'fumbles',
        }
        
        # Clean header
        cleaned = re.sub(r'[^a-z0-9\s]', '', header.lower().strip())
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return header_mappings.get(cleaned, cleaned)
    
    def _extract_from_alternative_structure(self, soup: BeautifulSoup) -> List[Dict]:
        """Try alternative parsing methods for ETR data"""
        projections = []
        
        # Look for divs or other structures containing player data
        # Common class patterns for fantasy sites
        player_selectors = [
            '.player-row',
            '.projection-row', 
            '[class*="player"]',
            '[class*="row"]',
            '.data-row'
        ]
        
        for selector in player_selectors:
            elements = soup.select(selector)
            if elements:
                for element in elements:
                    player_data = self._parse_element_for_player_data(element)
                    if player_data.get('player'):
                        projections.append(player_data)
                if projections:  # If we found data, don't try other selectors
                    break
        
        return projections
    
    def _parse_element_for_player_data(self, element) -> Dict:
        """Parse an element for player projection data"""
        player_data = {}
        
        text_content = element.get_text(strip=True)
        
        # Try to extract player info from text
        player_info = self._parse_player_info(text_content)
        player_data.update(player_info)
        
        # Look for numeric data in nested elements
        for child in element.find_all(['span', 'div', 'td']):
            child_text = child.get_text(strip=True)
            
            # Check if this looks like a fantasy points value
            if re.match(r'^\d+\.?\d*$', child_text):
                try:
                    value = float(child_text)
                    # Heuristic: values > 50 are likely total points, others might be per-game
                    if not player_data.get('fantasy_points'):
                        player_data['fantasy_points'] = value
                except ValueError:
                    continue
        
        return player_data
    
    def _parse_headerless_row(self, cells) -> Dict:
        """Parse a table row without headers"""
        player_data = {}
        
        # Common structure: Player, Position, Team, Stats..., Fantasy Points
        for i, cell in enumerate(cells):
            text = cell.get_text(strip=True)
            
            if i == 0:  # Player name
                player_info = self._parse_player_info(text)
                player_data.update(player_info)
            elif i == 1 and text in ['QB', 'RB', 'WR', 'TE', 'K', 'DST']:
                player_data['position'] = text
            elif i == 2 and re.match(r'^[A-Z]{2,3}$', text):
                player_data['team'] = text
            elif i == len(cells) - 1:  # Last column often fantasy points
                numeric_value = self._convert_to_numeric(text)
                if numeric_value is not None:
                    player_data['fantasy_points'] = numeric_value
        
        return player_data
    
    def _parse_player_info(self, text: str) -> Dict:
        """
        Parse player information from text
        
        Args:
            text: Text containing player information
            
        Returns:
            Dictionary with parsed player data
        """
        player_data = {}
        
        if not text:
            return player_data
        
        # Common patterns for ETR player info
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
        
        # Pattern: "Player Name, POS, TEAM"
        pattern3 = r'^([A-Za-z\s\.\']+?),\s*([A-Z]{1,3}),\s*([A-Z]{2,3})$'
        match = re.match(pattern3, text)
        if match:
            player_data['player'] = match.group(1).strip()
            player_data['position'] = match.group(2).strip()
            player_data['team'] = match.group(3).strip()
            return player_data
        
        # If no pattern matches, assume it's just the player name
        if text and not re.match(r'^[A-Z]{2,3}$', text):  # Not just a team code
            player_data['player'] = text.strip()
        
        return player_data
    
    def _convert_to_numeric(self, value: str) -> float:
        """Convert string value to numeric if possible"""
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
    
    def validate_parsed_data(self, data: List[Dict[str, Any]]) -> bool:
        """
        Validate that parsed ETR data has expected structure
        
        Args:
            data: Parsed list of dictionaries
            
        Returns:
            True if data is valid, False otherwise
        """
        if not data:
            return False
        
        # Should have player column at minimum in at least one record
        has_players = any('player' in row and row.get('player') for row in data)
        
        # Should have some numeric data (fantasy points or stats)
        has_numeric_data = any(
            any(isinstance(value, (int, float)) for value in row.values())
            for row in data
        )
        
        return has_players and has_numeric_data