# tests/test_etr.py
# -*- coding: utf-8 -*-
# Copyright (C) 2025 Eric Truett
# Licensed under the MIT License

"""
Tests for ETR (Establish The Run) projection components
"""

import pytest
from unittest.mock import Mock, patch
from bs4 import BeautifulSoup

from nflprojections.fetch.etr_fetcher import ETRFetcher
from nflprojections.parse.etr_parser import ETRParser
from nflprojections.sources.etr import ETRProjections
from nflprojections.sources.etr_refactored import ETRProjectionsRefactored


class TestETRFetcher:
    """Test ETR fetcher functionality"""
    
    def test_fetcher_initialization(self):
        """Test that ETR fetcher initializes correctly"""
        fetcher = ETRFetcher(position="qb", scoring="ppr", week=1)
        
        assert fetcher.source_name == "etr"
        assert fetcher.position == "qb"
        assert fetcher.scoring == "ppr"
        assert fetcher.week == 1
        assert "establishtherun.com" in fetcher.base_url
    
    def test_build_url_season_projections(self):
        """Test URL building for season projections"""
        fetcher = ETRFetcher(position="rb", scoring="half-ppr")
        url = fetcher.build_url(season=2024)
        
        assert "establishtherun.com/projections" in url
        assert "rb" in url
        assert "scoring=half-ppr" in url
    
    def test_build_url_weekly_projections(self):
        """Test URL building for weekly projections"""
        fetcher = ETRFetcher(position="wr", scoring="standard", week=5)
        url = fetcher.build_url(season=2024)
        
        assert "week-5" in url
        assert "wr" in url
        assert "scoring=standard" in url


class TestETRParser:
    """Test ETR parser functionality"""
    
    def test_parser_initialization(self):
        """Test that ETR parser initializes correctly"""
        parser = ETRParser()
        
        assert parser.source_name == "etr"
        assert parser.table_selector == "table"
    
    def test_normalize_header(self):
        """Test header normalization"""
        parser = ETRParser()
        
        assert parser._normalize_header("Player") == "player"
        assert parser._normalize_header("Pos") == "position"
        assert parser._normalize_header("Team") == "team"
        assert parser._normalize_header("FPts") == "fantasy_points"
        assert parser._normalize_header("Fantasy Points") == "fantasy_points"
    
    def test_parse_player_info(self):
        """Test player info parsing"""
        parser = ETRParser()
        
        # Test pattern: "Player Name POS TEAM"
        result = parser._parse_player_info("Josh Allen QB BUF")
        expected = {
            'player': 'Josh Allen',
            'position': 'QB',
            'team': 'BUF'
        }
        assert result == expected
        
        # Test pattern: "Player Name - POS - TEAM"
        result = parser._parse_player_info("Christian McCaffrey - RB - SF")
        expected = {
            'player': 'Christian McCaffrey',
            'position': 'RB',
            'team': 'SF'
        }
        assert result == expected
    
    def test_convert_to_numeric(self):
        """Test numeric conversion"""
        parser = ETRParser()
        
        assert parser._convert_to_numeric("25.5") == 25.5
        assert parser._convert_to_numeric("100") == 100
        assert parser._convert_to_numeric("invalid") is None
        assert parser._convert_to_numeric("") is None
    
    @patch('requests.get')
    def test_parse_table_structure(self, mock_get):
        """Test parsing of table structure"""
        # Mock HTML with a simple table structure
        html_content = """
        <html>
            <table>
                <thead>
                    <tr>
                        <th>Player</th>
                        <th>Pos</th>
                        <th>Team</th>
                        <th>FPts</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Josh Allen QB BUF</td>
                        <td>QB</td>
                        <td>BUF</td>
                        <td>22.5</td>
                    </tr>
                </tbody>
            </table>
        </html>
        """
        
        soup = BeautifulSoup(html_content, 'html.parser')
        parser = ETRParser()
        
        result = parser.parse_raw_data(soup)
        
        assert len(result) > 0
        # The parser will extract player info from the first cell
        # Check that we have the expected data structure
        assert 'player' in result[0] or 'Josh Allen' in str(result[0])
        assert 'fantasy_points' in result[0]
        assert result[0]['fantasy_points'] == 22.5
    
    def test_validate_parsed_data(self):
        """Test data validation"""
        parser = ETRParser()
        
        # Valid data
        valid_data = [
            {'player': 'Josh Allen', 'position': 'QB', 'fantasy_points': 22.5}
        ]
        assert parser.validate_parsed_data(valid_data) is True
        
        # Empty data
        assert parser.validate_parsed_data([]) is False
        
        # Data without players
        invalid_data = [{'team': 'BUF', 'fantasy_points': 22.5}]
        assert parser.validate_parsed_data(invalid_data) is False


class TestETRProjections:
    """Test ETR legacy-style projections class"""
    
    def test_initialization(self):
        """Test that ETR projections initializes correctly"""
        etr = ETRProjections(season=2024, week=5, position="qb", scoring="ppr")
        
        assert etr.season == 2024
        assert etr.week == 5
        assert etr.position == "qb"
        assert etr.scoring == "ppr"
    
    def test_build_url(self):
        """Test URL building"""
        etr = ETRProjections(position="rb", scoring="half-ppr", week=3)
        url = etr._build_url(season=2024)
        
        assert "establishtherun.com/projections" in url
        assert "week-3" in url
        assert "rb" in url
        assert "scoring=half-ppr" in url
    
    def test_normalize_header(self):
        """Test header normalization in legacy class"""
        etr = ETRProjections()
        
        assert etr._normalize_header("Player") == "player"
        assert etr._normalize_header("FPts") == "fantasy_points"
        assert etr._normalize_header("Proj") == "fantasy_points"


class TestETRProjectionsRefactored:
    """Test ETR refactored projections class"""
    
    def test_initialization(self):
        """Test that refactored ETR projections initializes correctly"""
        etr = ETRProjectionsRefactored(
            season=2024,
            week=1,
            position="wr",
            scoring="standard"
        )
        
        assert etr.season == 2024
        assert etr.week == 1
        assert etr.position == "wr"
        assert etr.scoring == "standard"
        
        # Check components are initialized
        assert etr.fetcher is not None
        assert etr.parser is not None
        assert etr.standardizer is not None
        assert etr.fetcher.source_name == "etr"
        assert etr.parser.source_name == "etr"
    
    def test_get_pipeline_info(self):
        """Test pipeline information"""
        etr = ETRProjectionsRefactored(season=2024, week=2, position="te")
        
        info = etr.get_pipeline_info()
        
        assert 'fetcher' in info
        assert 'parser' in info
        assert 'standardizer' in info
        assert info['season'] == '2024'
        assert info['week'] == '2'
        assert info['position'] == 'te'
        assert 'ETRFetcher' in info['fetcher']
        assert 'ETRParser' in info['parser']
    
    def test_validate_data_pipeline_standardizer(self):
        """Test standardizer component validation"""
        etr = ETRProjectionsRefactored()
        
        # Test just the standardizer component with dummy data
        dummy_data = [{
            'player': 'Test Player',
            'position': 'QB',
            'team': 'KC',
            'fantasy_points': 20.5
        }]
        
        standardized = etr.standardizer.standardize(dummy_data)
        assert len(standardized) > 0
        assert 'plyr' in standardized[0]  # Should be mapped from 'player'
    
    def test_column_mapping(self):
        """Test column mapping configuration"""
        custom_mapping = {
            'player_name': 'plyr',
            'pos': 'pos',
            'team_abbr': 'team',
            'projected_points': 'proj',
            'season': 'season',
            'week': 'week'
        }
        
        etr = ETRProjectionsRefactored(column_mapping=custom_mapping)
        
        assert etr.standardizer.column_mapping == custom_mapping


# Integration test (mock-based since we can't access real ETR site)
class TestETRIntegration:
    """Integration tests for ETR components"""
    
    @patch('nflprojections.fetch.etr_fetcher.requests.get')
    def test_full_pipeline_with_mock_data(self, mock_get):
        """Test full pipeline with mocked data"""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.content = """
        <html>
            <table>
                <thead>
                    <tr>
                        <th>Player</th>
                        <th>Pos</th>
                        <th>Team</th>
                        <th>Fantasy Points</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Josh Allen</td>
                        <td>QB</td>
                        <td>BUF</td>
                        <td>24.5</td>
                    </tr>
                    <tr>
                        <td>Saquon Barkley</td>
                        <td>RB</td>
                        <td>PHI</td>
                        <td>18.2</td>
                    </tr>
                </tbody>
            </table>
        </html>
        """
        mock_get.return_value = mock_response
        
        # Test refactored version
        etr = ETRProjectionsRefactored(season=2024, week=1)
        
        # This would normally fetch real data, but we're mocking it
        raw_data = etr.fetch_raw_data()
        parsed_data = etr.parse_data(raw_data)
        standardized_data = etr.standardize_data(parsed_data)
        
        # Verify we got data
        assert len(standardized_data) > 0
        
        # Verify standardized format
        player = standardized_data[0]
        assert 'plyr' in player  # player -> plyr mapping
        assert 'pos' in player   # position -> pos mapping
        assert 'proj' in player  # fantasy_points -> proj mapping


if __name__ == '__main__':
    pytest.main([__file__])