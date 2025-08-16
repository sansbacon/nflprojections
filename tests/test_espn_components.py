# tests/test_espn_components.py
# -*- coding: utf-8 -*-
# Copyright (C) 2025 Eric Truett
# Licensed under the MIT License

"""
Tests for the ESPN functional components
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock

from nflprojections.fetch import ESPNFetcher
from nflprojections.parse import ESPNParser
from nflprojections.sources import ESPNProjections


class TestESPNFetcher:
    """Test the ESPN fetcher component"""
    
    def test_espn_fetcher_initialization(self):
        """Test ESPN fetcher initialization"""
        fetcher = ESPNFetcher(season=2025)
        assert fetcher.source_name == "espn"
        assert fetcher.season == 2025
        assert fetcher.timeout == 30
    
    def test_espn_fetcher_api_url(self):
        """Test ESPN API URL generation"""
        fetcher = ESPNFetcher(season=2025)
        expected_url = "https://fantasy.espn.com/apis/v3/games/ffl/seasons/2025/segments/0/leaguedefaults/3"
        assert fetcher.api_url == expected_url
    
    def test_espn_fetcher_headers(self):
        """Test ESPN API headers"""
        fetcher = ESPNFetcher(season=2025)
        headers = fetcher.default_headers
        
        assert "fantasy.espn.com" in headers["authority"]
        assert "application/json" in headers["accept"]
        assert "x-fantasy-filter" in headers
        
        # Verify x-fantasy-filter is valid JSON
        xff = json.loads(headers["x-fantasy-filter"])
        assert "players" in xff
        assert xff["players"]["limit"] == 1500
    
    @patch('requests.Session.get')
    def test_espn_fetcher_fetch_raw_data(self, mock_get):
        """Test ESPN fetcher raw data retrieval"""
        fetcher = ESPNFetcher(season=2025)
        
        # Mock successful response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"players": [{"player": {"id": 1, "fullName": "Test Player"}}]}
        mock_get.return_value = mock_response
        
        result = fetcher.fetch_raw_data()
        
        assert result is not None
        assert "players" in result
        mock_get.assert_called_once()
    
    @patch('requests.Session.head')
    def test_espn_fetcher_validate_connection(self, mock_head):
        """Test connection validation"""
        fetcher = ESPNFetcher(season=2025)
        
        mock_head.return_value.status_code = 200
        assert fetcher.validate_connection() is True
        
        mock_head.side_effect = Exception("Network error")
        assert fetcher.validate_connection() is False


class TestESPNParser:
    """Test the ESPN parser component"""
    
    def test_espn_parser_initialization(self):
        """Test ESPN parser initialization"""
        parser = ESPNParser(season=2025, week=1)
        assert parser.source_name == "espn"
        assert parser.season == 2025
        assert parser.week == 1
    
    def test_espn_parser_seasonal_data(self):
        """Test parsing seasonal projection data"""
        parser = ESPNParser(season=2025, week=None)
        
        # Create mock ESPN API response
        mock_data = {
            "players": [
                {
                    "player": {
                        "id": 123,
                        "fullName": "Test Player",
                        "proTeamId": 12,  # KC
                        "defaultPositionId": 1,  # QB
                        "stats": [
                            {
                                "seasonId": 2025,
                                "scoringPeriodId": 0,
                                "statSourceId": 1,
                                "statSplitTypeId": 0,
                                "appliedTotal": 25.5,
                                "stats": {"4": 30, "3": 4200}  # pass_td, pass_yds
                            }
                        ]
                    }
                }
            ]
        }
        
        result = parser.parse_raw_data(mock_data)
        
        assert len(result) == 1
        player = result[0]
        assert player["source_player_id"] == 123
        assert player["source_player_name"] == "Test Player"
        assert player["source_team_code"] == "KC"
        assert player["source_player_position"] == "QB"
        assert player["source_player_projection"] == 25.5
        assert player["pass_td"] == 30.0
        assert player["pass_yds"] == 4200.0
    
    def test_espn_parser_weekly_data(self):
        """Test parsing weekly projection data"""
        parser = ESPNParser(season=2025, week=1)
        
        # Create mock ESPN API response
        mock_data = {
            "players": [
                {
                    "player": {
                        "id": 456,
                        "fullName": "Test RB",
                        "proTeamId": 2,  # BUF
                        "defaultPositionId": 2,  # RB
                        "stats": [
                            {
                                "seasonId": 2025,
                                "scoringPeriodId": 1,
                                "statSourceId": 1,
                                "statSplitTypeId": 0,
                                "appliedTotal": 15.3,
                                "stats": {"24": 120, "25": 1}  # rush_yds, rush_td
                            }
                        ]
                    }
                }
            ]
        }
        
        result = parser.parse_raw_data(mock_data)
        
        assert len(result) == 1
        player = result[0]
        assert player["source_player_id"] == 456
        assert player["source_player_name"] == "Test RB"
        assert player["source_team_code"] == "BUF"
        assert player["source_player_position"] == "RB"
        assert player["source_player_projection"] == 15.3
        assert player["rush_yds"] == 120.0
        assert player["rush_td"] == 1.0
    
    def test_espn_parser_validate_parsed_data(self):
        """Test parsed data validation"""
        parser = ESPNParser()
        
        # Valid data
        valid_data = [{
            "source_player_name": "Test Player",
            "source_player_position": "QB",
            "source_team_code": "KC"
        }]
        assert parser.validate_parsed_data(valid_data) is True
        
        # Invalid data
        assert parser.validate_parsed_data([]) is False
        assert parser.validate_parsed_data([{"invalid": "data"}]) is False
    
    def test_espn_parser_team_mapping(self):
        """Test ESPN team ID to code mapping"""
        parser = ESPNParser()
        
        # Test team_id to code
        assert parser._espn_team(team_id=12) == "KC"
        assert parser._espn_team(team_id=2) == "BUF"
        assert parser._espn_team(team_id=999) is None
        
        # Test team_code to id
        assert parser._espn_team(team_code="KC") == 12
        assert parser._espn_team(team_code="BUF") == 2
        assert parser._espn_team(team_code="INVALID") is None


class TestESPNProjections:
    """Test the refactored ESPN projections class"""
    
    def test_espn_projections_initialization(self):
        """Test ESPN projections refactored initialization"""
        espn = ESPNProjections(season=2025, week=1)
        assert espn.season == 2025
        assert espn.week == 1
        assert espn.fetcher.source_name == "espn"
        assert espn.parser.source_name == "espn"
    
    @patch('nflprojections.fetch.espn_fetcher.ESPNFetcher.fetch_raw_data')
    @patch('nflprojections.parse.espn_parser.ESPNParser.parse_raw_data')
    @patch('nflprojections.standardize.base_standardizer.ProjectionStandardizer.standardize')
    def test_espn_projections_data_pipeline(self, mock_standardize, mock_parse, mock_fetch):
        """Test complete data pipeline"""
        espn = ESPNProjections(season=2025, week=1)
        
        # Mock data flow
        mock_fetch.return_value = {"players": []}
        mock_parse.return_value = [{"source_player_name": "Test Player"}]
        mock_standardize.return_value = [{"plyr": "Test Player", "pos": "QB", "team": "KC", "proj": 20.0}]
        
        result = espn.data_pipeline()
        
        assert len(result) == 1
        assert result[0]["plyr"] == "Test Player"
        mock_fetch.assert_called_once()
        mock_parse.assert_called_once()
        mock_standardize.assert_called_once()
    
    def test_espn_projections_get_pipeline_info(self):
        """Test pipeline info retrieval"""
        espn = ESPNProjections(season=2025, week=5)
        info = espn.get_pipeline_info()
        
        assert "ESPN" in info['source']
        assert info['season'] == '2025'
        assert info['week'] == '5'
        assert 'ESPNFetcher' in info['fetcher']
        assert 'ESPNParser' in info['parser']


class TestESPNProjections:
    """Test the ESPN projections ProjectionSource integration"""
    
    def test_espn_projections_initialization(self):
        """Test ESPN projections initialization"""
        espn = ESPNProjections(season=2025, week=1)
        assert espn.season == 2025
        assert espn.week == 1
        assert espn.composed_mode is True
        assert espn.fetcher.source_name == "espn"
    
    @patch('nflprojections.fetch.espn_fetcher.ESPNFetcher.validate_connection')
    def test_espn_projections_validate_data_pipeline(self, mock_validate):
        """Test data pipeline validation"""
        espn = ESPNProjections(season=2025)
        
        mock_validate.return_value = True
        validation = espn.validate_data_pipeline()
        
        assert 'fetcher_connection' in validation
        mock_validate.assert_called_once()