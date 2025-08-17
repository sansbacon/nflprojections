# nflprojections/fantasypros_parser.py
# -*- coding: utf-8 -*-
# Copyright (C) 2025 Eric Truett
# Licensed under the MIT License

"""
FantasyPros specific parser implementation for HTML table data
"""

import logging
import re
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup, Tag

from .base_parser import HTMLTableParser


logger = logging.getLogger(__name__)


class FantasyProsParser(HTMLTableParser):
    """Parser specifically for FantasyPros fantasy projections HTML"""
    
    def __init__(self, position: str = "qb", **kwargs):
        """
        Initialize FantasyPros parser
        
        Args:
            position: Position being parsed (affects column interpretation)
            **kwargs: Additional configuration
        """
        super().__init__(
            source_name="fantasypros",
            table_selector="table.table",
            **kwargs
        )
        self.position = position.lower()
    
    def parse_raw_data(self, raw_data: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Parse FantasyPros HTML data into structured format
        
        Args:
            raw_data: BeautifulSoup object with FantasyPros HTML
            
        Returns:
            List of dictionaries with parsed player data
        """
        if isinstance(raw_data, str):
            soup = BeautifulSoup(raw_data, 'html.parser')
        else:
            soup = raw_data
        
        # Find the main projections table
        table = self._find_projections_table(soup)
        if not table:
            logger.warning("No projections table found in FantasyPros HTML")
            return []
        
        # Extract table data based on position
        projections = self._extract_table_data(table)
        
        logger.info(f"Parsed {len(projections)} player projections from FantasyPros")
        return projections
    
    def _find_projections_table(self, soup: BeautifulSoup) -> Optional[Tag]:
        """Find the main projections table in the HTML"""
        
        # Try different selectors for the projections table
        selectors = [
            "table.table",
            "table",
            ".table",
            "[class*='table']"
        ]
        
        for selector in selectors:
            tables = soup.select(selector)
            for table in tables:
                # Look for tables with projection data
                if self._is_projections_table(table):
                    return table
        
        return None
    
    def _is_projections_table(self, table: Tag) -> bool:
        """Check if a table contains fantasy projections data"""
        
        # Look for characteristic column headers
        headers = table.find_all(['th', 'td'])
        header_text = ' '.join([h.get_text(strip=True).upper() for h in headers])
        
        # Check for fantasy football related headers
        ff_indicators = ['PLAYER', 'FPTS', 'ATT', 'CMP', 'YDS', 'TDS', 'REC', 'TD']
        return any(indicator in header_text for indicator in ff_indicators)
    
    def _extract_table_data(self, table: Tag) -> List[Dict[str, Any]]:
        """Extract data from the projections table"""
        
        projections = []
        
        # Get table headers
        headers = self._extract_headers(table)
        if not headers:
            logger.warning("No headers found in projections table")
            return []
        
        # Get data rows  
        tbody = table.find('tbody') or table
        rows = tbody.find_all('tr')
        
        for row in rows:
            # Skip header rows
            if row.find('th'):
                continue
                
            cells = row.find_all(['td', 'th'])
            if not cells:
                continue
            
            player_data = self._parse_row(cells, headers)
            if player_data:
                projections.append(player_data)
        
        return projections
    
    def _extract_headers(self, table: Tag) -> List[str]:
        """Extract column headers from the table"""
        
        headers = []
        
        # Look in thead first
        thead = table.find('thead')
        if thead:
            # FantasyPros has multi-row headers, get the bottom row with actual column names
            header_rows = thead.find_all('tr')
            if header_rows:
                # Use the last header row which has the actual column names
                last_header_row = header_rows[-1]
                header_cells = last_header_row.find_all(['th', 'td'])
                
                # Track position for QB tables with duplicate column names
                column_index = 0
                for cell in header_cells:
                    header_text = self._clean_header_text(cell.get_text(strip=True))
                    
                    # For QB tables, differentiate between passing and rushing stats
                    if self.position == 'qb' and column_index > 0:
                        if header_text in ['att', 'yds', 'td'] and column_index <= 5:
                            # These are passing stats (columns 1-5)
                            header_text = f'pass_{header_text}'
                        elif header_text in ['att', 'yds', 'td'] and column_index > 5:
                            # These are rushing stats (columns 6+)  
                            header_text = f'rush_{header_text}'
                    
                    headers.append(header_text)
                    column_index += 1
        
        # If no headers found in thead, look in first row
        if not headers:
            first_row = table.find('tr')
            if first_row:
                header_cells = first_row.find_all(['th', 'td'])
                headers = [self._clean_header_text(cell.get_text(strip=True)) for cell in header_cells]
        
        return headers
    
    def _clean_header_text(self, text: str) -> str:
        """Clean and normalize header text"""
        # Remove extra whitespace and convert to lowercase
        text = text.strip().lower()
        
        # Map common variations to standard names
        header_map = {
            'att': 'att',
            'cmp': 'cmp', 
            'yds': 'yds',
            'tds': 'td',
            'ints': 'int',
            'rec': 'rec',
            'fl': 'fum',
            'fpts': 'fantasy_points',
            'player': 'player'
        }
        
        return header_map.get(text, text)
    
    def _parse_row(self, cells: List[Tag], headers: List[str]) -> Optional[Dict[str, Any]]:
        """Parse a table row into player data"""
        
        if len(cells) != len(headers):
            # Handle cases where cells and headers don't match exactly
            logger.debug(f"Cell count ({len(cells)}) doesn't match header count ({len(headers)})")
        
        player_data = {}
        
        for i, cell in enumerate(cells):
            header = headers[i] if i < len(headers) else f'col_{i}'
            cell_text = cell.get_text(strip=True)
            
            if i == 0:
                # First column is usually player info
                player_info = self._parse_player_cell(cell)
                player_data.update(player_info)
            else:
                # Other columns are stats
                if header and cell_text:
                    # Try to convert numeric values
                    try:
                        # Handle decimal values  
                        if '.' in cell_text:
                            player_data[header] = float(cell_text)
                        else:
                            player_data[header] = int(cell_text)
                    except ValueError:
                        # Keep as string if not numeric
                        player_data[header] = cell_text
        
        # Only return if we have player name
        if player_data.get('player'):
            return player_data
        
        return None
    
    def _parse_player_cell(self, cell: Tag) -> Dict[str, str]:
        """Parse the player cell to extract name, position, and team"""
        
        player_data = {}
        
        # Look for player name in link
        link = cell.find('a')
        if link:
            player_name = link.get_text(strip=True)
            # Clean up player name (remove extra spaces, etc.)
            player_name = re.sub(r'\s+', ' ', player_name).strip()
            player_data['player'] = player_name
        
        # Get full cell text to extract team 
        full_text = cell.get_text(strip=True)
        
        # Extract team code (usually 2-3 letters at the end)
        # Handle cases where there might not be a space before the team code
        team_match = re.search(r'([A-Z]{2,3})\s*$', full_text)
        if team_match:
            player_data['team'] = team_match.group(1)
        
        # Extract position if present (QB, RB, WR, TE, K, DST)
        pos_match = re.search(r'\b(QB|RB|WR|TE|K|DST)\b', full_text)
        if pos_match:
            player_data['position'] = pos_match.group(1)
        elif self.position:
            # Use the position from parser initialization if not found in text
            player_data['position'] = self.position.upper()
        
        return player_data
    
    def validate_parsed_data(self, data: List[Dict[str, Any]]) -> bool:
        """
        Validate that parsed FantasyPros data meets expected format
        
        Args:
            data: List of dictionaries with parsed data
            
        Returns:
            True if data is valid, False otherwise
        """
        if not data or not isinstance(data, list):
            return False
        
        # Check that we have at least one record
        if len(data) == 0:
            return False
        
        # Check that each record is a dictionary with expected fields
        for record in data:
            if not isinstance(record, dict):
                return False
            
            # Should have at least player name and fantasy points
            if 'player' not in record:
                return False
            
            if 'fantasy_points' not in record:
                # Be flexible - some tables might use different column names
                fpts_fields = ['fpts', 'fantasy_points', 'points', 'proj']
                if not any(field in record for field in fpts_fields):
                    logger.warning(f"No fantasy points field found in record: {record.keys()}")
        
        return True