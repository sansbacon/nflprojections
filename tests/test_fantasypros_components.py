# tests/test_fantasypros_components.py
# -*- coding: utf-8 -*-
# Copyright (C) 2025 Eric Truett
# Licensed under the MIT License

"""
Tests for the FantasyPros functional components
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from bs4 import BeautifulSoup

from nflprojections.fetch import FantasyProsFetcher
from nflprojections.parse import FantasyProsParser
from nflprojections.sources import FantasyProsProjections


class TestFantasyProsFetcher:
    """Test the FantasyPros fetcher component"""
    
    def test_fantasypros_fetcher_initialization(self):
        """Test FantasyPros fetcher initialization"""
        fetcher = FantasyProsFetcher(position="qb", scoring="ppr", week="draft")
        assert fetcher.source_name == "fantasypros"
        assert fetcher.position == "qb"
        assert fetcher.scoring == "PPR"
        assert fetcher.week == "draft"
        assert fetcher.timeout == 30
    
    def test_fantasypros_fetcher_url_building(self):
        """Test FantasyPros URL generation"""
        fetcher = FantasyProsFetcher(position="qb", scoring="ppr", week="draft")
        url = fetcher.build_url()
        expected_url = "https://www.fantasypros.com/nfl/projections/qb.php?week=draft"
        assert url == expected_url
        
        # Test with scoring parameter for skill positions
        fetcher = FantasyProsFetcher(position="rb", scoring="half", week="1")
        url = fetcher.build_url()
        expected_url = "https://www.fantasypros.com/nfl/projections/rb.php?week=1&scoring=HALF"
        assert url == expected_url
    
    def test_fantasypros_fetcher_position_normalization(self):
        """Test position normalization"""
        fetcher = FantasyProsFetcher(position="quarterback")
        assert fetcher.position == "qb"  # fallback to default
        
        fetcher = FantasyProsFetcher(position="RB")
        assert fetcher.position == "rb"
        
        fetcher = FantasyProsFetcher(position="defense")
        assert fetcher.position == "dst"
    
    def test_fantasypros_fetcher_scoring_normalization(self):
        """Test scoring format normalization"""
        fetcher = FantasyProsFetcher(scoring="PPR")
        assert fetcher.scoring == "PPR"
        
        fetcher = FantasyProsFetcher(scoring="half-ppr")
        assert fetcher.scoring == "HALF"
        
        fetcher = FantasyProsFetcher(scoring="standard")
        assert fetcher.scoring == "STD"


class TestFantasyProsParser:
    """Test the FantasyPros parser component"""
    
    def test_fantasypros_parser_initialization(self):
        """Test FantasyPros parser initialization"""
        parser = FantasyProsParser(position="qb")
        assert parser.source_name == "fantasypros"
        assert parser.position == "qb"
    
    def test_fantasypros_parser_player_cell_parsing(self):
        """Test parsing player information from table cell"""
        parser = FantasyProsParser(position="qb")
        
        # Create mock HTML cell
        html = '<td class="player-label"><a href="/nfl/projections/josh-allen-qb.php">Josh Allen</a> BUF</td>'
        soup = BeautifulSoup(html, 'html.parser')
        cell = soup.find('td')
        
        player_info = parser._parse_player_cell(cell)
        
        assert player_info['player'] == 'Josh Allen'
        assert player_info['team'] == 'BUF'
        assert player_info['position'] == 'QB'
    
    def test_fantasypros_parser_header_cleaning(self):
        """Test header text cleaning and normalization"""
        parser = FantasyProsParser()
        
        assert parser._clean_header_text("ATT") == "att"
        assert parser._clean_header_text("FPTS") == "fantasy_points"
        assert parser._clean_header_text("TDS") == "td"
        assert parser._clean_header_text("INTS") == "int"
    
    def test_fantasypros_parser_validate_data(self):
        """Test data validation"""
        parser = FantasyProsParser()
        
        # Valid data
        valid_data = [
            {'player': 'Josh Allen', 'team': 'BUF', 'position': 'QB', 'fantasy_points': 376.7}
        ]
        assert parser.validate_parsed_data(valid_data) == True
        
        # Invalid data - empty
        assert parser.validate_parsed_data([]) == False
        assert parser.validate_parsed_data(None) == False
        
        # Invalid data - missing player name
        invalid_data = [{'team': 'BUF', 'fantasy_points': 376.7}]
        assert parser.validate_parsed_data(invalid_data) == False


class TestFantasyProsProjections:
    """Test the main FantasyPros projections class"""
    
    def test_fantasypros_projections_initialization(self):
        """Test FantasyPros projections initialization"""
        fp = FantasyProsProjections(position="qb", scoring="ppr", week="draft")
        
        assert fp.position == "qb"
        assert fp.scoring == "ppr"
        assert fp.week == "draft"
        assert fp.fetcher is not None
        assert fp.parser is not None
        assert fp.standardizer is not None
    
    def test_fantasypros_projections_component_types(self):
        """Test that correct component types are created"""
        fp = FantasyProsProjections(position="rb", scoring="half", week=1)
        
        assert isinstance(fp.fetcher, FantasyProsFetcher)
        assert isinstance(fp.parser, FantasyProsParser)
        assert fp.fetcher.position == "rb"
        assert fp.fetcher.scoring == "HALF"
        assert fp.parser.position == "rb"
    
    def test_fantasypros_projections_pipeline_info(self):
        """Test getting pipeline information"""
        fp = FantasyProsProjections(position="wr", scoring="ppr", week=8)
        
        info = fp.get_pipeline_info()
        
        assert "FantasyProsFetcher" in info['fetcher']
        assert "FantasyProsParser" in info['parser']
        assert info['position'] == 'wr'
        assert info['scoring'] == 'ppr'
        assert info['week'] == '8'
    
    def test_fantasypros_projections_default_column_mapping(self):
        """Test default column mapping"""
        fp = FantasyProsProjections()
        
        mapping = fp.DEFAULT_COLUMN_MAPPING
        assert mapping['player'] == 'plyr'
        assert mapping['position'] == 'pos'
        assert mapping['team'] == 'team'
        assert mapping['fantasy_points'] == 'proj'
        
        # Check some QB-specific mappings
        assert mapping['att'] == 'pass_att'
        assert mapping['cmp'] == 'pass_cmp'
        assert mapping['int'] == 'pass_int'
        
        # Check skill position mappings
        assert mapping['rec'] == 'rec'
        assert mapping['rec_td'] == 'rec_td'


# Integration test (would need mocking for actual HTTP requests)
class TestFantasyProsIntegration:
    """Integration tests for FantasyPros components working together"""
    
    @patch('requests.get')
    def test_fantasypros_integration_mock(self, mock_get):
        """Test integration with mocked HTTP response"""
        # Mock HTML response with sample FantasyPros table
        sample_html = '''
        <table class="table">
            <thead>
                <tr><td>Player</td><td>ATT</td><td>CMP</td><td>YDS</td><td>TDS</td><td>INTS</td><td>FPTS</td></tr>
            </thead>
            <tbody>
                <tr>
                    <td class="player-label">
                        <a href="/nfl/projections/josh-allen-qb.php">Josh Allen</a> BUF
                    </td>
                    <td>522</td>
                    <td>334</td>
                    <td>3914</td>
                    <td>29</td>
                    <td>11</td>
                    <td>376.7</td>
                </tr>
            </tbody>
        </table>
        '''
        
        mock_response = Mock()
        mock_response.content = sample_html.encode()
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        fp = FantasyProsProjections(position="qb", scoring="ppr", week="draft")
        
        # Test that validation can run without errors
        validation = fp.validate_data_pipeline()
        
        # Should have results for all three components
        assert 'fetcher_connection' in validation
        assert 'parser_valid' in validation  
        assert 'standardizer_valid' in validation