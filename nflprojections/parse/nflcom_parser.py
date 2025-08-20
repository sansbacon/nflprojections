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
        data = []

        table = raw_data.find('table')

        # Get headers
        headers = ['player', 'opp', 'gp', 'pass_yds', 'pass_td', 'pass_int', 'rush_yds', 'rush_td', 'rec', 'rec_yds', 'rec_td', 'ret_td', 'fumb_td', 'two_pt', 'fumb_lost', 'fantasy_points']
        
        for row in table.find_all('tr')[1:]:
            # get start
            d = dict(zip(headers, [cell.get_text(strip=True) for cell in row.find_all('td')]))

            # fix the player
            """
            <td class="playerNameAndInfo first" id="yui_3_15_0_1_1755522743045_606">
            <div class="c c-nyg" id="yui_3_15_0_1_1755522743045_609">
            <b></b>
            <a onclick="return false" href="/players/card?leagueId=0&amp;playerId=2572342" class="playerCard playerName playerNameFull playerNameId-2572342 what-playerCard" id="yui_3_15_0_1_1755522743045_608">Malik Nabers</a> 
            <em>WR - NYG</em> 
            <strong class="status status-q" title="Questionable">Q</strong> 
            <a class="playerNote playerCard what-playerCard playerNote-breaking" title="View Breaking Player News" onclick="return false" href="/players/card?leagueId=0&amp;playerId=2572342">View News</a>  
            </div></td>"""

            d['player'] = row.find('a', class_='playerName').get_text(strip=True) if row.find('a', class_='playerName') else ''
            d['team'] = row.find('em').get_text(strip=True).split(' - ')[-1] if row.find('em') else ''
            d['position'] = row.find('em').get_text(strip=True).split(' - ')[0] if row.find('em') else ''
            data.append(self._fix_dtypes(d))

        return data
    
    def _fix_dtypes(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fix data types in the projection data dictionary

        Args:
            data: Dictionary with projection data

        Returns:
            Dictionary with fixed data types
        """
        plpatt = re.compile(r"^(.*?)(QB|WR|RB|TE|DST).*?([A-Z]{2,3})$")

        for key, value in data.items():
            if key in ['gp', 'pass_yds', 'pass_td', 'pass_int', 'rush_yds', 'rush_td', 'rec', 'rec_yds', 'rec_td', 'ret_td', 'fumb_td', 'two_pt', 'fumb_lost']:
                data[key] = int(value) if value.isdigit() else 0
            elif key == 'fantasy_points':
                data[key] = float(value) if value.replace('.', '', 1).isdigit() else 0.0
            elif key == 'opp':
                data[key] = value.strip().upper().replace('@', '') if value else ''

        return data