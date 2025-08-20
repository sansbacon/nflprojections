# nflprojections/nflcom_parser.py
# -*- coding: utf-8 -*-
# Copyright (C) 2025 Eric Truett
# Licensed under the MIT License

"""
NFL.com specific parser implementation
"""

import logging
import re
from typing import Dict, List, Any
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
    
    def parse_raw_data(self, raw_data: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Parse NFL.com HTML data into list of dictionaries
        
        Args:
            raw_data: BeautifulSoup object with NFL.com HTML
            
        Returns:
            List of dictionaries with parsed projection data
        """
        projections_data = self._parse_projections_table(raw_data)
        
        if not projections_data:
            logger.warning("No projection data found")
            return []
        
        return projections_data
    
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
        
        # Map generic table headers to proper statistical field names
        header_mapping = self._create_header_mapping(headers)
        
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if not cells:
                continue
            
            # Check if this row contains sub-headers (like "TD", "Yds", etc.) instead of player data
            cell_texts = [cell.get_text(strip=True) for cell in cells]
            if self._is_subheader_row(cell_texts):
                continue  # Skip sub-header rows
            
            # Skip rows where first cell is "-" or empty (these are often sub-data rows)
            if not cell_texts or cell_texts[0] in ['-', '']:
                continue
            
            player_data = {}
            cell_values = [cell.get_text(strip=True) for cell in cells]
            
            # Extract player info from first column
            if cell_values[0] and cell_values[0] != '-':
                player_data.update(self._parse_player_info(cell_values[0]))
            
            # Map remaining columns using header mapping
            for i, cell_value in enumerate(cell_values[1:], start=1):
                if i < len(headers) and headers[i] in header_mapping:
                    field_name = header_mapping[headers[i]]
                    if field_name and cell_value != '-':
                        # Try to convert numeric values
                        try:
                            if '.' in cell_value:
                                player_data[field_name] = float(cell_value)
                            elif cell_value.isdigit():
                                player_data[field_name] = int(cell_value)
                            else:
                                player_data[field_name] = cell_value
                        except ValueError:
                            player_data[field_name] = cell_value
            
            # Extract fantasy points - should be the rightmost decimal value
            fantasy_points = self._extract_fantasy_points_from_row(cell_values)
            if fantasy_points is not None:
                player_data['fantasy_points'] = fantasy_points
            
            # Only include rows with valid player data
            if player_data.get('player') and (player_data.get('fantasy_points') or len(player_data) > 3):
                data.append(player_data)
        
        return data
    
    def _is_subheader_row(self, cell_texts: List[str]) -> bool:
        """
        Check if a row contains sub-header information rather than player data
        
        Args:
            cell_texts: List of text content from table cells
            
        Returns:
            True if the row appears to contain sub-headers, False otherwise
        """
        if not cell_texts:
            return False
        
        # Sub-header rows typically contain generic stat abbreviations
        subheader_indicators = {
            'TD', 'Yds', 'Int', 'Rec', 'FumTD', '2PT', 'Lost', 'Points', 
            'Att', 'Cmp', 'Tgt', 'Long', 'Avg', 'YAC', 'Fum', 'FL'
        }
        
        # If most cells contain common stat abbreviations, it's likely a sub-header
        matching_indicators = sum(1 for cell in cell_texts if cell in subheader_indicators)
        
        # If more than half the cells are stat indicators, it's probably a sub-header
        return matching_indicators > len(cell_texts) / 2
    
    def _extract_from_alternative_structure(self, soup: BeautifulSoup) -> List[Dict]:
        """Try alternative parsing methods for NFL.com data"""
        projections = []
        
        # First try to parse the new NFL.com structure with playerStat spans
        playerstat_data = self._parse_playerstat_structure(soup)
        if playerstat_data:
            projections.extend(playerstat_data)
            # If we found playerstat data, return early to avoid duplication
            return projections
        
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
    
    def _create_header_mapping(self, headers: List[str]) -> Dict[str, str]:
        """
        Create mapping from table headers to proper statistical field names
        
        Args:
            headers: List of table headers from HTML
            
        Returns:
            Dictionary mapping table headers to statistical field names
        """
        # Mapping of common table headers to proper statistical field names
        # Based on expected NFL.com table structure 
        header_to_stat = {
            'Player': None,  # Handled separately in player parsing
            'Passing': 'pass_yds',    # Passing yards 
            'Rushing': 'pass_td',     # Passing TDs (in context of QB projections)
            'Receiving': 'pass_int',  # Passing interceptions
            'Ret': 'rush_yds',        # Rushing yards
            'Misc': 'rush_td',        # Rushing TDs
            'Fum': 'fumb_lost',       # Fumbles lost
            'Fantasy': None,          # Fantasy points handled separately
            'Opp': 'opp',             # Opponent
            'GP': 'gp',               # Games played
            'Yds': None,              # Generic yards - skip
            'TD': 'fumb_td',          # Fumble TDs or other TDs
            'Int': None,              # This column often contains fantasy points, not interceptions
        }
        
        # Create the actual mapping for this table
        mapping = {}
        for header in headers:
            if header in header_to_stat:
                mapping[header] = header_to_stat[header]
            else:
                # For unknown headers, use lowercase version
                mapping[header] = header.lower() if header else None
                
        return mapping
    
    def _extract_fantasy_points_from_row(self, cell_values: List[str]) -> float:
        """
        Extract fantasy points from a table row - should be the rightmost decimal value
        
        Args:
            cell_values: List of cell values from the table row
            
        Returns:
            Fantasy points value or None if not found
        """
        # Look for decimal numbers, fantasy points are typically the rightmost one
        decimal_values = []
        for value in cell_values:
            if value and re.match(r'^\d+\.\d+$', value):
                try:
                    decimal_values.append(float(value))
                except ValueError:
                    continue
        
        # Return the last (rightmost) decimal value found
        return decimal_values[-1] if decimal_values else None
    
    def _parse_playerstat_structure(self, soup: BeautifulSoup) -> List[Dict]:
        """
        Parse NFL.com structure with playerStat spans containing statId and playerId
        
        Args:
            soup: BeautifulSoup object containing HTML with playerStat spans
            
        Returns:
            List of dictionaries with parsed player data including player_id and mapped stats
        """
        projections = []
        
        # Find all elements that contain playerStat spans - avoid nested duplicates
        all_containers = soup.find_all(lambda tag: tag.find_all('span', class_=lambda x: x and 'playerStat' in x))
        
        # Filter out nested containers to avoid duplicates
        containers = []
        for container in all_containers:
            # Only include if this container isn't nested inside another container
            is_nested = False
            for other in all_containers:
                if other != container and container in other.find_all(True):
                    is_nested = True
                    break
            if not is_nested:
                containers.append(container)
        
        for container in containers:
            player_data = {}
            
            # Extract text content before any spans (contains player name, position, team)
            spans = container.find_all('span', class_=lambda x: x and 'playerStat' in x)
            if not spans:
                continue
                
            # Get all text content
            full_text = container.get_text(strip=True)
            
            # Extract player information from text (before stat values)
            # Remove all span content to get just the player info and fantasy points
            temp_container = BeautifulSoup(str(container), 'html.parser')
            for span in temp_container.find_all('span'):
                span.decompose()
            remaining_text = temp_container.get_text(strip=True)
            
            # Split on fantasy points (decimal numbers) to separate player info
            import re
            parts = re.split(r'\d+\.\d+', remaining_text)
            if parts:
                player_info_text = parts[0].strip()
            else:
                player_info_text = remaining_text
            
            # Parse player name, position, team from the remaining text
            player_info = self._parse_player_info_from_playerstat_text(player_info_text)
            player_data.update(player_info)
            
            # Try to extract opponent information if present
            opponent_info = self._extract_opponent_info(container, full_text)
            if opponent_info:
                player_data.update(opponent_info)
            
            # Extract player_id from first span's playerId class
            first_span = spans[0]
            player_id = self._extract_player_id_from_span(first_span)
            if player_id:
                player_data['player_id'] = f"player-{player_id}"
            
            # Extract statistics from all spans
            stats = self._extract_stats_from_playerstat_spans(spans)
            player_data.update(stats)
            
            # Add default values for missing stats
            default_stats = self._add_default_stats(player_data)
            player_data.update(default_stats)
            
            # Extract fantasy points (usually the last number in the text)
            fantasy_points = self._extract_fantasy_points_from_container(container)
            if fantasy_points is not None:
                player_data['fantasy_points'] = fantasy_points
            
            if player_data.get('player') or player_data.get('player_id'):
                projections.append(player_data)
        
        return projections
    
    def _parse_player_info_from_playerstat_text(self, text: str) -> Dict:
        """Parse player name, position, team from text before playerStat spans"""
        player_data = {}
        
        if not text:
            return player_data
            
        # Clean up the text - remove extra whitespace and periods
        cleaned_text = re.sub(r'\s+', ' ', text.strip())
        cleaned_text = re.sub(r'\.+$', '', cleaned_text)  # Remove trailing periods
        
        # Remove opponent information (vs TEAM, @TEAM, etc.) from the text
        cleaned_text = re.sub(r'\s+(?:vs\.?\s+|@\s*)([A-Z]{2,3}).*$', '', cleaned_text)
        
        # Try to match patterns like "Brian Thomas Jr. WR JAX" or "Player Name POS TEAM"
        # Pattern: Name ending with position and team
        pattern = r'^(.+?)\s+([A-Z]{1,3})\s+([A-Z]{2,3})$'
        match = re.match(pattern, cleaned_text)
        if match:
            player_data['player'] = match.group(1).strip()
            player_data['position'] = match.group(2).strip() 
            player_data['team'] = match.group(3).strip()
            return player_data
            
        # Fallback: use the existing player info parser
        return self._parse_player_info(cleaned_text)
    
    def _extract_player_id_from_span(self, span) -> str:
        """Extract player ID from playerId class in span"""
        classes = span.get('class', [])
        for cls in classes:
            if cls.startswith('playerId-'):
                return cls.split('playerId-')[1]
        return None
        
    def _extract_stats_from_playerstat_spans(self, spans) -> Dict:
        """Extract and map statistics from playerStat spans using statId"""
        stats = {}
        
        # Mapping of statId to stat names - corrected based on issue #62 analysis
        # Based on actual NFL.com playerStat structure
        stat_id_mapping = {
            '1': 'gp',             # Games played
            '2': 'pass_att',       # Passing attempts  
            '3': 'pass_yd',        # Passing yards (alternate)
            '4': 'pass_td',        # Passing touchdowns (alternate)
            '5': 'pass_yds',       # Passing yards (main)
            '6': 'pass_td',        # Passing touchdowns (main)
            '7': 'pass_int',       # Passing interceptions
            '14': 'rush_yds',      # Rushing yards (main)
            '15': 'rush_td',       # Rushing touchdowns
            '20': 'rec',           # Receptions
            '21': 'rec_yds',       # Receiving yards
            '22': 'rec_td',        # Receiving touchdowns
            '23': 'rec_lng',       # Receiving long
            '28': 'ret_td',        # Return touchdowns
            '29': 'fumb_td',       # Fumble touchdowns
            '30': 'fumb_lost',     # Fumbles lost
            '32': 'two_pt',        # Two point conversions
        }
        
        for span in spans:
            # Extract statId from classes
            stat_id = None
            classes = span.get('class', [])
            for cls in classes:
                if cls.startswith('statId-'):
                    stat_id = cls.split('statId-')[1]
                    break
                    
            if stat_id and stat_id in stat_id_mapping:
                stat_name = stat_id_mapping[stat_id]
                stat_value = span.get_text(strip=True)
                
                # Only add non-empty values
                if stat_value:
                    try:
                        # Try to convert to number if it looks like one
                        if re.match(r'^\d+\.?\d*$', stat_value):
                            stats[stat_name] = float(stat_value) if '.' in stat_value else int(stat_value)
                        else:
                            stats[stat_name] = stat_value
                    except ValueError:
                        stats[stat_name] = stat_value
                        
        return stats
    
    def _add_default_stats(self, player_data: Dict) -> Dict:
        """Add default values for common fantasy stats that may not be present"""
        defaults = {
            'pass_yds': 0,
            'pass_td': 0,
            'pass_int': 0,
            'rush_yds': 0,
            'rush_td': 0,
            'rec': 0,
            'rec_yds': 0,
            'rec_td': 0,
            'ret_td': 0,
            'fumb_td': 0,
            'two_pt': 0,
            'fumb_lost': 0,
        }
        
        # Only add defaults for stats that aren't already present
        result = {}
        for stat, default_value in defaults.items():
            if stat not in player_data:
                result[stat] = default_value
        
        return result
        
    def _extract_opponent_info(self, container, full_text: str) -> Dict:
        """Extract opponent information if present in container or nearby elements"""
        opponent_info = {}
        
        # Look for common opponent patterns in the text or nearby elements
        # Pattern: "vs TEAM", "@TEAM", "vs. TEAM", etc.
        opponent_patterns = [
            r'(?:vs\.?\s+|@\s*)([A-Z]{2,3})',  # vs JAX, @JAX, vs. JAX
            r'(?:against\s+)([A-Z]{2,3})',      # against JAX  
        ]
        
        for pattern in opponent_patterns:
            match = re.search(pattern, full_text)
            if match:
                opponent_info['opp'] = match.group(1)
                break
        
        # Also check parent/sibling elements for opponent info
        if not opponent_info.get('opp'):
            parent = container.parent if container.parent else container
            parent_text = parent.get_text()
            for pattern in opponent_patterns:
                match = re.search(pattern, parent_text)
                if match:
                    opponent_info['opp'] = match.group(1)
                    break
                    
        return opponent_info
        
    def _extract_fantasy_points_from_container(self, container) -> float:
        """Extract fantasy points from container, excluding span content"""
        # Create a copy and remove all spans to get just the fantasy points
        temp_container = BeautifulSoup(str(container), 'html.parser')
        for span in temp_container.find_all('span'):
            span.decompose()
        
        # Get the remaining text and look for decimal numbers
        remaining_text = temp_container.get_text().strip()
        
        # Find decimal numbers in the remaining text (more permissive pattern)
        numbers = re.findall(r'\d+\.\d+', remaining_text)
        if numbers:
            try:
                return float(numbers[-1])  # Take the last decimal number
            except ValueError:
                pass
                
        return None
    
    def _extract_fantasy_points_from_text(self, text: str) -> float:
        """Extract fantasy points from the end of text (after all spans)"""
        # Split the text and look for the last standalone decimal number
        # The fantasy points should be at the very end, not concatenated with other numbers
        
        # Remove all content that's inside spans to isolate the fantasy points
        temp_soup = BeautifulSoup(f"<div>{text}</div>", 'html.parser')
        # Get text parts that are not inside spans
        text_parts = []
        for node in temp_soup.find('div').contents:
            if hasattr(node, 'name') and node.name == 'span':
                continue  # Skip span content
            else:
                text_parts.append(str(node))
        
        remaining_text = ''.join(text_parts).strip()
        
        # Find numbers in the remaining text (should be just the fantasy points)
        numbers = re.findall(r'\b\d+\.\d+\b', remaining_text)
        if numbers:
            try:
                return float(numbers[-1])
            except ValueError:
                pass
                
        return None
    
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
        
        # Pattern: "Player Name TEAM" (without position)
        pattern3 = r'^([A-Za-z\s\.]+?)\s+([A-Z]{2,3})$'
        match = re.match(pattern3, text)
        if match:
            player_data['player'] = match.group(1).strip()
            player_data['team'] = match.group(2).strip()
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
        
        # If still no player name found, try to extract from space-separated components
        if not player_data.get('player') and text:
            parts = text.strip().split()
            if len(parts) >= 2:
                # Check if last part is a team code
                if re.match(r'^[A-Z]{2,3}$', parts[-1]):
                    team = parts[-1]
                    # Check if second to last is position
                    if len(parts) >= 3 and parts[-2] in ['QB', 'RB', 'WR', 'TE', 'K', 'DST']:
                        player_name = ' '.join(parts[:-2])
                        position = parts[-2]
                        player_data['player'] = player_name
                        player_data['position'] = position
                        player_data['team'] = team
                    else:
                        # Just player name and team
                        player_name = ' '.join(parts[:-1])
                        player_data['player'] = player_name
                        player_data['team'] = team
                else:
                    # No recognizable team code, use whole text as player name
                    clean_name = re.sub(r'[^A-Za-z\s\.]', ' ', text).strip()
                    if clean_name:
                        player_data['player'] = clean_name
        
        return player_data
        
        return player_data
    
    def validate_parsed_data(self, data: List[Dict[str, Any]]) -> bool:
        """
        Validate that parsed NFL.com data has expected structure
        
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