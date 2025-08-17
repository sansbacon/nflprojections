# nflprojections/tests/test_fantasylife.py
# -*- coding: utf-8 -*-
# Copyright (C) 2025 Eric Truett
# Licensed under the MIT License

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch

from nflprojections import FantasyLifeProjections
from nflprojections.fetch.fantasylife_fetcher import FantasyLifeFetcher
from nflprojections.parse.fantasylife_parser import FantasyLifeParser


@pytest.fixture
def sample_csv_content():
    """Sample CSV content for testing"""
    return """Player,Position,Team,Fantasy Points,Season,Week
Josh Allen,QB,BUF,24.5,2024,1
Christian McCaffrey,RB,SF,18.2,2024,1
Cooper Kupp,WR,LAR,16.8,2024,1
Travis Kelce,TE,KC,14.1,2024,1
Justin Tucker,K,BAL,9.5,2024,1
San Francisco,DST,SF,8.2,2024,1
"""


@pytest.fixture
def temp_csv_file(sample_csv_content):
    """Create temporary CSV file for testing"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(sample_csv_content)
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    os.unlink(temp_path)


@pytest.fixture 
def fantasylife_projections(temp_csv_file):
    """Create FantasyLifeProjections instance for testing"""
    return FantasyLifeProjections(
        file_path=temp_csv_file,
        season=2024,
        week=1,
        use_schedule=False,
        use_names=False
    )


class TestFantasyLifeFetcher:
    """Test FantasyLifeFetcher functionality"""
    
    def test_init(self, temp_csv_file):
        """Test FantasyLifeFetcher initialization"""
        fetcher = FantasyLifeFetcher(file_path=temp_csv_file)
        assert fetcher.source_name == "fantasylife"
        assert fetcher.file_path == temp_csv_file
    
    def test_fetch_raw_data(self, temp_csv_file, sample_csv_content):
        """Test fetching raw CSV data"""
        fetcher = FantasyLifeFetcher(file_path=temp_csv_file)
        raw_data = fetcher.fetch_raw_data()
        assert raw_data == sample_csv_content
    
    def test_validate_connection(self, temp_csv_file):
        """Test connection validation"""
        fetcher = FantasyLifeFetcher(file_path=temp_csv_file)
        assert fetcher.validate_connection() == True
    
    def test_validate_connection_nonexistent_file(self):
        """Test connection validation with nonexistent file"""
        fetcher = FantasyLifeFetcher(file_path="/nonexistent/file.csv")
        assert fetcher.validate_connection() == False


class TestFantasyLifeParser:
    """Test FantasyLifeParser functionality"""
    
    def test_init(self):
        """Test FantasyLifeParser initialization"""
        parser = FantasyLifeParser()
        assert parser.source_name == "fantasylife"
    
    def test_parse_raw_data(self, sample_csv_content):
        """Test parsing CSV data"""
        parser = FantasyLifeParser()
        parsed_data = parser.parse_raw_data(sample_csv_content)
        
        assert len(parsed_data) == 6
        assert isinstance(parsed_data, list)
        assert isinstance(parsed_data[0], dict)
        
        # Check first record
        first_record = parsed_data[0]
        assert first_record['Player'] == 'Josh Allen'
        assert first_record['Position'] == 'QB'
        assert first_record['Team'] == 'BUF'
        assert first_record['Fantasy Points'] == 24.5
        assert first_record['Season'] == 2024
        assert first_record['Week'] == 1
    
    def test_parse_empty_data(self):
        """Test parsing empty CSV data"""
        parser = FantasyLifeParser()
        parsed_data = parser.parse_raw_data("")
        assert parsed_data == []
    
    def test_validate_parsed_data(self, sample_csv_content):
        """Test validation of parsed data"""
        parser = FantasyLifeParser()
        parsed_data = parser.parse_raw_data(sample_csv_content)
        assert parser.validate_parsed_data(parsed_data) == True
    
    def test_validate_parsed_data_empty(self):
        """Test validation of empty data"""
        parser = FantasyLifeParser()
        assert parser.validate_parsed_data([]) == False
    
    def test_validate_parsed_data_invalid(self):
        """Test validation of invalid data"""
        parser = FantasyLifeParser()
        assert parser.validate_parsed_data("not a list") == False
        assert parser.validate_parsed_data([]) == False
        assert parser.validate_parsed_data([{"some": "data"}]) == True  # Basic structure is OK
    
    def test_fantasylife_transformations(self):
        """Test specific transformations required by issue #54"""
        parser = FantasyLifeParser()
        
        # Test data from the issue description
        csv_content = '''#,Player,Position,Team,P Att,Comp,Comp%,P Yds,TD,Int,R Att,Ru Yds,Ru TD,Proj
4,Jayden Daniels,QB,WAS,497.0,339.5,69%,"3,735.5",25.4,9.6,138.9,816.1,5.5,356.1'''
        
        parsed_data = parser.parse_raw_data(csv_content)
        assert len(parsed_data) == 1
        
        record = parsed_data[0]
        
        # Test transformation 1: '#' -> 'Jersey_Number'
        assert '#' not in record, "Original '#' column should be removed"
        assert 'Jersey_Number' in record, "Should have 'Jersey_Number' column"
        assert record['Jersey_Number'] == 4
        
        # Test transformation 2: 'Comp%' string to decimal
        assert record['Comp%'] == 0.69, f"Expected 0.69, got {record['Comp%']}"
        
        # Test transformation 3: 'P Yds' comma-separated string to numeric
        assert record['P Yds'] == 3735.5, f"Expected 3735.5, got {record['P Yds']}"
        
        # Verify other fields are unchanged
        assert record['Player'] == 'Jayden Daniels'
        assert record['Position'] == 'QB'
        assert record['Team'] == 'WAS'
        assert record['P Att'] == 497.0
        assert record['Comp'] == 339.5
        assert record['TD'] == 25.4
        assert record['Int'] == 9.6
        assert record['R Att'] == 138.9
        assert record['Ru Yds'] == 816.1
        assert record['Ru TD'] == 5.5
        assert record['Proj'] == 356.1
    
    def test_transformation_edge_cases(self):
        """Test edge cases for transformations"""
        parser = FantasyLifeParser()
        
        # Test with various edge cases
        csv_content = '''#,Player,Comp%,P Yds
1,Player1,50%,"1,000.0"
2,Player2,invalid%,"not,numeric"
3,Player3,100%,500.5'''
        
        parsed_data = parser.parse_raw_data(csv_content)
        assert len(parsed_data) == 3
        
        # Test normal case
        assert parsed_data[0]['Jersey_Number'] == 1
        assert parsed_data[0]['Comp%'] == 0.5
        assert parsed_data[0]['P Yds'] == 1000.0
        
        # Test invalid percentage (should remain unchanged)
        assert parsed_data[1]['Jersey_Number'] == 2
        assert parsed_data[1]['Comp%'] == 'invalid%'  # Should remain as string
        assert parsed_data[1]['P Yds'] == 'not,numeric'  # Should remain as string
        
        # Test without comma in P Yds
        assert parsed_data[2]['Jersey_Number'] == 3
        assert parsed_data[2]['Comp%'] == 1.0
        assert parsed_data[2]['P Yds'] == 500.5


class TestFantasyLifeProjections:
    """Test FantasyLifeProjections main class"""
    
    def test_init(self, temp_csv_file):
        """Test FantasyLifeProjections initialization"""
        fl = FantasyLifeProjections(
            file_path=temp_csv_file,
            season=2024,
            week=1
        )
        assert fl.file_path == temp_csv_file
        assert fl.season == 2024
        assert fl.week == 1
        assert fl.fetcher is not None
        assert fl.parser is not None
        assert fl.standardizer is not None
    
    def test_column_mapping(self, temp_csv_file):
        """Test default column mapping"""
        fl = FantasyLifeProjections(file_path=temp_csv_file)
        expected_mapping = {
            'Player': 'plyr',
            'Position': 'pos', 
            'Team': 'team',
            'Fantasy Points': 'proj',
            'Season': 'season',
            'Week': 'week'
        }
        assert fl.standardizer.column_mapping == expected_mapping
    
    def test_custom_column_mapping(self, temp_csv_file):
        """Test custom column mapping"""
        custom_mapping = {
            'Player': 'plyr',  # Must map to required 'plyr'
            'Position': 'pos',
            'Team': 'team',
            'Fantasy Points': 'proj',  # Must map to required 'proj'
            'Season': 'season',
            'Week': 'week'
        }
        fl = FantasyLifeProjections(
            file_path=temp_csv_file,
            column_mapping=custom_mapping
        )
        assert fl.standardizer.column_mapping == custom_mapping
    
    def test_fetch_raw_data(self, fantasylife_projections, sample_csv_content):
        """Test fetching raw data"""
        raw_data = fantasylife_projections.fetch_raw_data()
        assert raw_data == sample_csv_content
    
    def test_parse_data(self, fantasylife_projections, sample_csv_content):
        """Test parsing data"""
        parsed_data = fantasylife_projections.parse_data(sample_csv_content)
        assert len(parsed_data) == 6
        assert parsed_data[0]['Player'] == 'Josh Allen'
    
    def test_data_pipeline(self, fantasylife_projections):
        """Test complete data pipeline"""
        result = fantasylife_projections.data_pipeline()
        
        assert isinstance(result, list)
        assert len(result) == 6
        
        # Check standardized format
        first_record = result[0]
        assert 'plyr' in first_record
        assert 'pos' in first_record
        assert 'team' in first_record
        assert 'proj' in first_record
        assert 'season' in first_record
        assert 'week' in first_record
        
        # Check values
        assert first_record['plyr'] == 'Josh Allen'
        assert first_record['pos'] == 'QB'
        assert first_record['team'] == 'BUF'
        assert first_record['proj'] == 24.5
    
    def test_fetch_projections(self, fantasylife_projections):
        """Test fetch_projections method"""
        projections = fantasylife_projections.fetch_projections()
        assert isinstance(projections, list)
        assert len(projections) == 6
        assert 'plyr' in projections[0]
    
    def test_validate_data_pipeline(self, fantasylife_projections):
        """Test data pipeline validation"""
        validation = fantasylife_projections.validate_data_pipeline()
        
        assert isinstance(validation, dict)
        assert 'fetcher_connection' in validation
        assert 'parser_valid' in validation
        assert 'standardizer_valid' in validation
        
        # All should be True for valid setup
        assert validation['fetcher_connection'] == True
        assert validation['parser_valid'] == True
        assert validation['standardizer_valid'] == True
    
    def test_get_pipeline_info(self, fantasylife_projections):
        """Test getting pipeline information"""
        info = fantasylife_projections.get_pipeline_info()
        
        assert isinstance(info, dict)
        assert 'fetcher' in info
        assert 'parser' in info
        assert 'standardizer' in info
        assert 'season' in info
        assert 'week' in info
        assert 'source' in info
        
        assert 'FantasyLifeFetcher' in info['fetcher']
        assert info['parser'] == 'FantasyLifeParser'
        assert info['standardizer'] == 'ProjectionStandardizer'
        assert info['source'] == 'fantasylife'


def test_integration_with_real_csv():
    """Test integration with a manually created CSV file"""
    # Create a temporary CSV file with test data
    csv_content = """Player,Position,Team,Fantasy Points,Season,Week
Lamar Jackson,QB,BAL,22.3,2024,2
Saquon Barkley,RB,PHI,19.1,2024,2
Tyreek Hill,WR,MIA,17.5,2024,2
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(csv_content)
        temp_path = f.name
    
    try:
        # Test full integration
        fl = FantasyLifeProjections(file_path=temp_path)
        projections = fl.fetch_projections()
        
        assert len(projections) == 3
        assert projections[0]['plyr'] == 'Lamar Jackson'
        assert projections[0]['pos'] == 'QB'
        assert projections[0]['proj'] == 22.3
        
    finally:
        os.unlink(temp_path)


def test_error_handling_missing_file():
    """Test error handling with missing file"""
    fl = FantasyLifeProjections(file_path="/nonexistent/file.csv")
    
    # Validation should fail
    validation = fl.validate_data_pipeline()
    assert validation['fetcher_connection'] == False
    
    # Should raise an exception when trying to fetch
    with pytest.raises(FileNotFoundError):
        fl.fetch_projections()