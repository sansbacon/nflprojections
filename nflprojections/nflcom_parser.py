# nflprojections/nflcom_parser.py
# -*- coding: utf-8 -*-
# Copyright (C) 2025 Eric Truett
# Licensed under the MIT License

"""
NFL.com specific parser implementation
"""

import logging
import re
from typing import Dict, List
import pandas as pd
from bs4 import BeautifulSoup

from .base_parser import HTMLTableParser


logger = logging.getLogger(__name__)


class NFLComParser(HTMLTableParser):
    """Parser specifically for NFL.com fantasy projections HTML"""
    
    def __init__(self, **kwargs):
        """
        Initialize NFL.com parser
        
        Args:
            **kwargs: Additional configuration
        """
        super().__init__(
            source_name="nfl.com",
            table_selector="table",
            **kwargs
        )
    
    def parse_raw_data(self, raw_data: BeautifulSoup) -> pd.DataFrame:
        """
        Parse NFL.com HTML data into DataFrame
        
        Args:
            raw_data: BeautifulSoup object with NFL.com HTML
            
        Returns:
            DataFrame with parsed projection data
        """
        projections_data = self._parse_projections_table(raw_data)
        
        if not projections_data:
            logger.warning("No projection data found")
            return pd.DataFrame()
        
        return pd.DataFrame(projections_data)
    
    def _parse_projections_table(self, soup: BeautifulSoup) -> List[Dict]:
        """
        Parse the projections table from NFL.com HTML
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            List of dictionaries with player projection data
        """
        projections = []
        
        # Look for different possible table structures
        tables = soup.find_all('table')
        for table in tables:
            data = self._extract_table_from_nfl_structure(table)
            if data:
                projections.extend(data)
        
        # If no tables found, try alternative parsing methods
        if not projections:
            projections = self._extract_from_alternative_structure(soup)
        
        return projections
    
    def _extract_table_from_nfl_structure(self, table) -> List[Dict]:
        """Extract data from standard NFL.com table structure"""
        data = []
        
        # Get headers
        headers = []
        header_row = table.find('thead') or table.find('tr')
        if header_row:
            for th in header_row.find_all(['th', 'td']):
                header_text = th.get_text(strip=True)
                headers.append(header_text)
        
        # Get data rows
        rows = table.find_all('tr')[1:] if headers else table.find_all('tr')
        
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if not cells:
                continue
            
            player_data = {}
            
            for i, cell in enumerate(cells):
                text = cell.get_text(strip=True)
                
                if i == 0 and text:  # First column is usually player info
                    player_data.update(self._parse_player_info(text))
                elif i < len(headers) and headers[i]:
                    # Map cell to header
                    header = headers[i].lower()
                    player_data[header] = text
                elif i == 1 and not player_data.get('position'):
                    # Second column might be position/team
                    if re.match(r'^[A-Z]{2,3}$', text):  # Team code
                        player_data['team'] = text
                    elif text in ['QB', 'RB', 'WR', 'TE', 'K', 'DST']:
                        player_data['position'] = text
            
                # Extract fantasy points if present
                for cell in cells:
                    text = cell.get_text(strip=True)
                    if re.match(r'^\d+\.?\d*$', text) and 'fantasy_points' not in player_data:
                        try:
                            player_data['fantasy_points'] = float(text)
                            break
                        except ValueError:
                            continue
            
            if player_data.get('player'):
                data.append(player_data)
        
        return data
    
    def _extract_from_alternative_structure(self, soup: BeautifulSoup) -> List[Dict]:
        """Try alternative parsing methods for NFL.com data"""
        projections = []
        
        # Look for divs or other structures containing player data
        player_elements = soup.find_all(['div', 'tr'], class_=re.compile(r'player|row'))
        
        for element in player_elements:
            text_content = element.get_text(strip=True)
            
            # Skip if no meaningful content
            if not text_content or len(text_content) < 5:
                continue
            
            player_data = self._parse_player_info(text_content)
            
            # Look for numeric values that could be projections
            numbers = re.findall(r'\d+\.?\d*', text_content)
            if numbers and player_data.get('player'):
                try:
                    # Assume last number is fantasy points
                    player_data['fantasy_points'] = float(numbers[-1])
                except (ValueError, IndexError):
                    pass
            
            if player_data.get('player'):
                projections.append(player_data)
        
        return projections
    
    def _parse_player_info(self, text: str) -> Dict:
        """
        Parse player information from text
        
        Args:
            text: Text containing player information
            
        Returns:
            Dictionary with parsed player data
        """
        player_data = {}
        
        # Common patterns for player info
        # Pattern: "Player Name - POS - TEAM"
        pattern1 = r'^([A-Za-z\s\.]+?)\s*-\s*([A-Z]{1,3})\s*-\s*([A-Z]{2,3})$'
        match = re.match(pattern1, text)
        if match:
            player_data['player'] = match.group(1).strip()
            player_data['position'] = match.group(2).strip()
            player_data['team'] = match.group(3).strip()
            return player_data
        
        # Pattern: "Player Name POS TEAM"
        pattern2 = r'^([A-Za-z\s\.]+?)\s+([A-Z]{1,3})\s+([A-Z]{2,3})$'
        match = re.match(pattern2, text)
        if match:
            player_data['player'] = match.group(1).strip()
            player_data['position'] = match.group(2).strip() 
            player_data['team'] = match.group(3).strip()
            return player_data
        
        # Pattern: "Player Name - POS/TEAM" or similar variations
        parts = text.split('-')
        if len(parts) >= 2:
            player_data['player'] = parts[0].strip()
            
            # Parse position/team from remaining parts
            remaining = '-'.join(parts[1:]).strip()
            
            # Look for position codes
            pos_match = re.search(r'\b(QB|RB|WR|TE|K|DST|Defense)\b', remaining)
            if pos_match:
                player_data['position'] = pos_match.group(1)
            
            # Look for team codes
            team_match = re.search(r'\b([A-Z]{2,3})\b', remaining)
            if team_match:
                player_data['team'] = team_match.group(1)
        
        # If still no player name found, use the whole text as player name
        if not player_data.get('player') and text:
            # Clean up text for player name
            clean_name = re.sub(r'[^A-Za-z\s\.]', ' ', text).strip()
            if clean_name:
                player_data['player'] = clean_name
        
        return player_data
    
    def validate_parsed_data(self, df: pd.DataFrame) -> bool:
        """
        Validate that parsed NFL.com data has expected structure
        
        Args:
            df: Parsed DataFrame
            
        Returns:
            True if data is valid, False otherwise
        """
        if df.empty:
            return False
        
        # Should have player column at minimum
        has_players = 'player' in df.columns and not df['player'].isna().all()
        
        # Should have some numeric data (fantasy points or stats)
        numeric_cols = df.select_dtypes(include=['number']).columns
        has_numeric_data = len(numeric_cols) > 0 and not df[numeric_cols].isna().all().all()
        
        return has_players and has_numeric_data