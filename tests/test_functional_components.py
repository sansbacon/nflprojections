# tests/test_functional_components.py
# -*- coding: utf-8 -*-
# Copyright (C) 2025 Eric Truett
# Licensed under the MIT License

"""
Tests for the new functional component architecture
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from bs4 import BeautifulSoup

from nflprojections.fetch import DataSourceFetcher, WebDataFetcher, FileDataFetcher, NFLComFetcher
from nflprojections.parse import DataSourceParser, HTMLTableParser, CSVParser, JSONParser, NFLComParser
from nflprojections.standardize import DataStandardizer, ProjectionStandardizer, StatStandardizer
from nflprojections.combine import ProjectionCombiner, CombinationMethod
from nflprojections.sources import NFLComProjectionsRefactored


class TestDataSourceFetcher:
    """Test the base DataSourceFetcher class"""
    
    def test_abstract_class_cannot_be_instantiated(self):
        """Test that DataSourceFetcher cannot be instantiated directly"""
        with pytest.raises(TypeError):
            DataSourceFetcher("test_source")
    
    def test_web_data_fetcher_initialization(self):
        """Test WebDataFetcher initialization"""
        fetcher = WebDataFetcher("test_source", "https://example.com")
        assert fetcher.source_name == "test_source"
        assert fetcher.base_url == "https://example.com"
        assert fetcher.headers == {}
    
    def test_web_data_fetcher_with_headers(self):
        """Test WebDataFetcher with custom headers"""
        headers = {"User-Agent": "test"}
        fetcher = WebDataFetcher("test_source", "https://example.com", headers=headers)
        assert fetcher.headers == headers
    
    def test_web_data_fetcher_build_url(self):
        """Test URL building with parameters"""
        fetcher = WebDataFetcher("test_source", "https://example.com/api")
        
        # No parameters
        assert fetcher.build_url() == "https://example.com/api"
        
        # With parameters
        url = fetcher.build_url(param1="value1", param2="value2")
        assert "param1=value1" in url
        assert "param2=value2" in url
    
    def test_file_data_fetcher_initialization(self):
        """Test FileDataFetcher initialization"""
        fetcher = FileDataFetcher("test_source", "/path/to/file.csv")
        assert fetcher.source_name == "test_source"
        assert fetcher.file_path == "/path/to/file.csv"
    
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.is_file')
    def test_file_data_fetcher_validate_connection(self, mock_is_file, mock_exists):
        """Test file existence validation"""
        fetcher = FileDataFetcher("test_source", "/path/to/file.csv")
        
        # File exists and is a file
        mock_exists.return_value = True
        mock_is_file.return_value = True
        assert fetcher.validate_connection() is True
        
        # File doesn't exist
        mock_exists.return_value = False
        assert fetcher.validate_connection() is False


class TestDataSourceParser:
    """Test the base DataSourceParser class"""
    
    def test_abstract_class_cannot_be_instantiated(self):
        """Test that DataSourceParser cannot be instantiated directly"""
        with pytest.raises(TypeError):
            DataSourceParser("test_source")
    
    def test_html_table_parser_initialization(self):
        """Test HTMLTableParser initialization"""
        parser = HTMLTableParser("test_source")
        assert parser.source_name == "test_source"
        assert parser.table_selector == "table"
    
    def test_html_table_parser_extract_table_data(self):
        """Test HTML table data extraction"""
        html = """
        <table>
            <thead><tr><th>Name</th><th>Value</th></tr></thead>
            <tbody>
                <tr><td>Player 1</td><td>100</td></tr>
                <tr><td>Player 2</td><td>200</td></tr>
            </tbody>
        </table>
        """
        soup = BeautifulSoup(html, 'html.parser')
        parser = HTMLTableParser("test_source")
        data = parser.extract_table_data(soup)
        
        assert len(data) == 2
        assert data[0] == {"Name": "Player 1", "Value": "100"}
        assert data[1] == {"Name": "Player 2", "Value": "200"}
    
    def test_csv_parser(self):
        """Test CSV parser"""
        parser = CSVParser("test_source")
        csv_data = "name,value\nPlayer 1,100\nPlayer 2,200"
        data = parser.parse_raw_data(csv_data)
        
        assert len(data) == 2
        assert list(data[0].keys()) == ["name", "value"]
        assert parser.validate_parsed_data(data) is True
    
    def test_json_parser_list(self):
        """Test JSON parser with list data"""
        parser = JSONParser("test_source")
        json_data = '[{"name": "Player 1", "value": 100}, {"name": "Player 2", "value": 200}]'
        df = parser.parse_raw_data(json_data)
        
        assert len(df) == 2
        assert parser.validate_parsed_data(df) is True
    
    def test_json_parser_dict(self):
        """Test JSON parser with dictionary data"""
        parser = JSONParser("test_source")
        json_data = '{"data": [{"name": "Player 1", "value": 100}]}'
        df = parser.parse_raw_data(json_data)
        
        assert len(df) == 1
        assert parser.validate_parsed_data(df) is True


class TestDataStandardizer:
    """Test the base DataStandardizer class"""
    
    def test_projection_standardizer_initialization(self):
        """Test ProjectionStandardizer initialization"""
        mapping = {
            'player_name': 'plyr',
            'position': 'pos',
            'team_code': 'team',
            'fantasy_pts': 'proj',
            'season_year': 'season',
            'week_num': 'week'
        }
        
        standardizer = ProjectionStandardizer(mapping, season=2025, week=1)
        assert standardizer.column_mapping == mapping
        assert standardizer.season == 2025
        assert standardizer.week == 1
    
    def test_projection_standardizer_missing_columns(self):
        """Test that ProjectionStandardizer validates required columns"""
        mapping = {'player_name': 'plyr'}  # Missing required columns
        
        with pytest.raises(ValueError) as excinfo:
            ProjectionStandardizer(mapping)
        assert "missing required columns" in str(excinfo.value)
    
    def test_projection_standardizer_remap_columns(self):
        """Test column remapping"""
        mapping = {
            'player_name': 'plyr',
            'position': 'pos',
            'team_code': 'team',
            'fantasy_pts': 'proj',
            'season_year': 'season',
            'week_num': 'week'
        }
        
        standardizer = ProjectionStandardizer(mapping)
        
        data = [{
            'player_name': 'Test Player',
            'position': 'QB',
            'team_code': 'KC',
            'fantasy_pts': 25.5
        }]
        
        result = standardizer.remap_columns(data)
        expected_columns = {'plyr', 'pos', 'team', 'proj'}
        assert expected_columns.issubset(set(result[0].keys()))
    
    def test_projection_standardizer_standardize(self):
        """Test full standardization process"""
        mapping = {
            'player_name': 'plyr',
            'position': 'pos',
            'team_code': 'team',
            'fantasy_pts': 'proj',
            'season_year': 'season',
            'week_num': 'week'
        }
        
        standardizer = ProjectionStandardizer(mapping, season=2025, week=1)
        
        data = [{
            'player_name': 'Test Player',
            'position': 'QB',
            'team_code': 'KC',
            'fantasy_pts': 25.5
        }]
        
        result = standardizer.standardize(data)
        
        # Check all required columns are present
        for col in standardizer.REQUIRED_COLUMNS:
            assert col in result[0]
        
        # Check season and week were added
        assert result[0]['season'] == 2025
        assert result[0]['week'] == 1


class TestProjectionCombiner:
    """Test the ProjectionCombiner class"""
    
    def test_combiner_initialization(self):
        """Test ProjectionCombiner initialization"""
        combiner = ProjectionCombiner()
        assert combiner.method == CombinationMethod.AVERAGE
        
        combiner = ProjectionCombiner(CombinationMethod.MEDIAN)
        assert combiner.method == CombinationMethod.MEDIAN
    
    def test_simple_average_combination(self):
        """Test simple average combination"""
        combiner = ProjectionCombiner()
        
        # Create test projection DataFrames
        proj1 = pd.DataFrame([
            {'plyr': 'Player 1', 'proj': 20.0},
            {'plyr': 'Player 2', 'proj': 15.0}
        ])
        
        proj2 = pd.DataFrame([
            {'plyr': 'Player 1', 'proj': 22.0},
            {'plyr': 'Player 2', 'proj': 17.0}
        ])
        
        result = combiner.combine_projections([proj1, proj2])
        
        assert len(result) == 2
        assert result[result['plyr'] == 'Player 1']['combined_proj'].iloc[0] == 21.0
        assert result[result['plyr'] == 'Player 2']['combined_proj'].iloc[0] == 16.0
    
    def test_weighted_average_combination(self):
        """Test weighted average combination"""
        combiner = ProjectionCombiner()
        
        proj1 = pd.DataFrame([{'plyr': 'Player 1', 'proj': 20.0}])
        proj2 = pd.DataFrame([{'plyr': 'Player 1', 'proj': 30.0}])
        
        weights = {'source_0': 0.3, 'source_1': 0.7}
        result = combiner.combine_projections(
            [proj1, proj2], 
            method=CombinationMethod.WEIGHTED_AVERAGE,
            weights=weights
        )
        
        expected = 20.0 * 0.3 + 30.0 * 0.7  # 27.0
        assert abs(result.iloc[0]['combined_proj'] - expected) < 0.001
    
    def test_median_combination(self):
        """Test median combination"""
        combiner = ProjectionCombiner()
        
        proj1 = pd.DataFrame([{'plyr': 'Player 1', 'proj': 10.0}])
        proj2 = pd.DataFrame([{'plyr': 'Player 1', 'proj': 20.0}])
        proj3 = pd.DataFrame([{'plyr': 'Player 1', 'proj': 30.0}])
        
        result = combiner.combine_projections(
            [proj1, proj2, proj3],
            method=CombinationMethod.MEDIAN
        )
        
        assert result.iloc[0]['combined_proj'] == 20.0
    
    def test_drop_high_low_combination(self):
        """Test drop high/low combination"""
        combiner = ProjectionCombiner()
        
        proj1 = pd.DataFrame([{'plyr': 'Player 1', 'proj': 10.0}])  # Low (dropped)
        proj2 = pd.DataFrame([{'plyr': 'Player 1', 'proj': 20.0}])  # Keep
        proj3 = pd.DataFrame([{'plyr': 'Player 1', 'proj': 22.0}])  # Keep
        proj4 = pd.DataFrame([{'plyr': 'Player 1', 'proj': 40.0}])  # High (dropped)
        
        result = combiner.combine_projections(
            [proj1, proj2, proj3, proj4],
            method=CombinationMethod.DROP_HIGH_LOW
        )
        
        expected = (20.0 + 22.0) / 2  # 21.0
        assert result.iloc[0]['combined_proj'] == expected


class TestNFLComComponents:
    """Test NFL.com specific components"""
    
    def test_nflcom_fetcher_initialization(self):
        """Test NFLComFetcher initialization"""
        fetcher = NFLComFetcher()
        assert fetcher.source_name == "nfl.com"
        assert fetcher.position == "0"
        assert fetcher.stat_category == "projectedStats"
    
    def test_nflcom_fetcher_build_url(self):
        """Test NFL.com URL building"""
        fetcher = NFLComFetcher(position="1")
        url = fetcher.build_url(season=2025)
        
        assert "fantasy.nfl.com" in url
        assert "position=1" in url
        assert "statSeason=2025" in url
    
    def test_nflcom_parser_initialization(self):
        """Test NFLComParser initialization"""
        parser = NFLComParser()
        assert parser.source_name == "nfl.com"
    
    def test_nflcom_parser_parse_player_info(self):
        """Test player info parsing"""
        parser = NFLComParser()
        
        # Test standard format
        player_data = parser._parse_player_info("Patrick Mahomes - QB - KC")
        assert player_data['player'] == "Patrick Mahomes"
        assert player_data['position'] == "QB"
        assert player_data['team'] == "KC"
        
        # Test alternate format
        player_data = parser._parse_player_info("Josh Allen QB BUF")
        assert player_data['player'] == "Josh Allen"
        assert player_data['position'] == "QB"
        assert player_data['team'] == "BUF"
    
    def test_nflcom_parser_playerstat_structure(self):
        """Test parsing NFL.com structure with playerStat spans"""
        parser = NFLComParser()
        
        # Example HTML structure from the issue
        html_content = '''
        <div class="player-row">
            Brian Thomas Jr. WR JAX<span class="playerStat statId-1 playerId-2572162">16</span><span class="playerStat statId-5 playerId-2572162"></span><span class="playerStat statId-6 playerId-2572162"></span><span class="playerStat statId-7 playerId-2572162"></span><span class="playerStat statId-14 playerId-2572162">18</span><span class="playerStat statId-15 playerId-2572162"></span><span class="playerStat statId-20 playerId-2572162">96</span><span class="playerStat statId-21 playerId-2572162">1305</span><span class="playerStat statId-22 playerId-2572162">8</span><span class="playerStat statId-28 playerId-2572162"></span><span class="playerStat statId-29 playerId-2572162"></span><span class="playerStat statId-32 playerId-2572162"></span><span class="playerStat statId-30 playerId-2572162">1</span>274.30
        </div>
        '''
        
        soup = BeautifulSoup(html_content, 'html.parser')
        result = parser.parse_raw_data(soup)
        
        # Should return one player
        assert len(result) == 1
        player = result[0]
        
        # Check basic player info
        assert player['player'] == 'Brian Thomas Jr.'
        assert player['position'] == 'WR'
        assert player['team'] == 'JAX'
        assert player['player_id'] == 'player-2572162'
        assert player['fantasy_points'] == 274.30
        
        # Check mapped statistics (based on statId mapping)
        assert player['gp'] == 16            # statId-1
        assert player['pass_yd'] == 0        # Default value
        assert player['pass_td'] == 0        # Default value
        assert player['pass_int'] == 0       # statId-5 (empty)
        assert player['rush_yd'] == 18       # statId-14 (corrected from rush_td)
        assert player['rush_td'] == 0        # Default value
        assert player['rec'] == 96           # statId-20
        assert player['rec_yd'] == 1305      # statId-21 (singular to match scoring formats)
        assert player['rec_td'] == 8         # statId-22
        assert player['ret_td'] == 0         # Default value
        assert player['fum_td'] == 0         # Default value
        assert player['two_pt'] == 0         # Default value (corrected from statId-30)
        assert player['fum_lost'] == 1       # statId-30 (corrected mapping)
    
    @patch('requests.head')
    def test_nflcom_fetcher_validate_connection(self, mock_head):
        """Test connection validation"""
        fetcher = NFLComFetcher()
        
        mock_head.return_value.status_code = 200
        assert fetcher.validate_connection() is True
        
        mock_head.side_effect = Exception("Network error")
        assert fetcher.validate_connection() is False


class TestNFLComRefactored:
    """Test the refactored NFLComProjections"""
    
    @patch('nflprojections.sources.nflcom_refactored.NFLComFetcher')
    @patch('nflprojections.sources.nflcom_refactored.NFLComParser') 
    @patch('nflprojections.sources.nflcom_refactored.ProjectionStandardizer')
    def test_initialization(self, mock_standardizer, mock_parser, mock_fetcher):
        """Test initialization of refactored component"""
        nfl = NFLComProjectionsRefactored(season=2025, week=1)
        
        # Check that components were initialized
        mock_fetcher.assert_called_once()
        mock_parser.assert_called_once()
        mock_standardizer.assert_called_once()
    
    def test_get_pipeline_info(self):
        """Test pipeline information retrieval"""
        nfl = NFLComProjectionsRefactored(season=2025, week=1)
        info = nfl.get_pipeline_info()
        
        assert 'fetcher' in info
        assert 'parser' in info
        assert 'standardizer' in info
        assert info['season'] == '2025'
        assert info['week'] == '1'
    
    @patch('nflprojections.sources.nflcom_refactored.NFLComFetcher.fetch_raw_data')
    @patch('nflprojections.sources.nflcom_refactored.NFLComParser.parse_raw_data')
    @patch('nflprojections.sources.nflcom_refactored.ProjectionStandardizer.standardize')
    def test_fetch_projections_pipeline(self, mock_standardize, mock_parse, mock_fetch):
        """Test the full data pipeline"""
        # Setup mocks
        mock_fetch.return_value = "mock_html"
        mock_parse.return_value = [{'player': 'Test', 'proj': 20}]
        mock_standardize.return_value = [{'plyr': 'Test', 'proj': 20}]
        
        nfl = NFLComProjectionsRefactored()
        result = nfl.fetch_projections(season=2025)
        
        # Check that pipeline was called in order
        mock_fetch.assert_called_once_with(season=2025)
        mock_parse.assert_called_once_with("mock_html")
        mock_standardize.assert_called_once()
        
        assert len(result) == 1
        assert result[0]['plyr'] == 'Test'