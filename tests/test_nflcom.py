# nflprojections/tests/test_nflcom.py
# -*- coding: utf-8 -*-
# Copyright (C) 2020 Eric Truett
# Licensed under the MIT License

import pytest
from unittest.mock import Mock, patch
import pandas as pd

from nflprojections import NFLComProjections


@pytest.fixture
def nflcom_projections():
    """Create NFLComProjections instance for testing"""
    return NFLComProjections(season=2025, week=1, use_schedule=False, use_names=False)


def test_init():
    """Test NFLComProjections initialization"""
    nfl = NFLComProjections(season=2025, week=1)
    assert nfl.projections_source == "nfl.com"
    assert nfl.season == 2025
    assert nfl.week == 1
    assert nfl.slate_name == "season"
    assert nfl.position == "0"


def test_init_with_custom_params():
    """Test initialization with custom parameters"""
    nfl = NFLComProjections(
        season=2024, 
        week=5, 
        position="1",  # QB only
        stat_category="customStats",
        stat_type="weeklyStats"
    )
    assert nfl.season == 2024
    assert nfl.week == 5
    assert nfl.position == "1"
    assert nfl.stat_category == "customStats"
    assert nfl.stat_type == "weeklyStats"


def test_build_url(nflcom_projections):
    """Test URL building"""
    url = nflcom_projections._build_url(2025)
    expected = "https://fantasy.nfl.com/research/projections?position=0&statCategory=projectedStats&statSeason=2025&statType=seasonProjectedStats"
    assert url == expected


def test_build_url_custom_params():
    """Test URL building with custom parameters"""
    nfl = NFLComProjections(position="1", stat_category="custom", stat_type="weekly")
    url = nfl._build_url(2024)
    assert "position=1" in url
    assert "statCategory=custom" in url
    assert "statType=weekly" in url
    assert "statSeason=2024" in url


def test_column_mapping():
    """Test default column mapping"""
    nfl = NFLComProjections()
    expected_mapping = {
        'player': 'plyr',
        'position': 'pos', 
        'team': 'team',
        'fantasy_points': 'proj',
        'season': 'season',
        'week': 'week'
    }
    assert nfl.column_mapping == expected_mapping


def test_remap_columns(nflcom_projections):
    """Test column remapping functionality"""
    df = pd.DataFrame({
        'player': ['Player 1', 'Player 2'],
        'fantasy_points': [10.5, 8.2],
        'position': ['QB', 'RB'],
        'team': ['KC', 'DAL'],
        'extra_col': ['val1', 'val2']
    })
    
    remapped = nflcom_projections._remap_columns(df)
    
    # Check that mapped columns were renamed
    assert 'plyr' in remapped.columns
    assert 'proj' in remapped.columns  
    assert 'pos' in remapped.columns
    assert 'team' in remapped.columns  # team maps to team
    
    # Check that unmapped columns remain
    assert 'extra_col' in remapped.columns
    
    # Check that original columns were renamed away
    assert 'player' not in remapped.columns
    assert 'fantasy_points' not in remapped.columns


@patch('nflprojections.nflcom.requests.get')
def test_fetch_page_success(mock_get, nflcom_projections):
    """Test successful page fetching"""
    # Mock successful response
    mock_response = Mock()
    mock_response.content = b'<html><table></table></html>'
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response
    
    soup = nflcom_projections._fetch_page("http://test.com")
    
    assert soup is not None
    assert soup.find('table') is not None
    mock_get.assert_called_once()


@patch('nflprojections.nflcom.requests.get')
def test_fetch_page_error(mock_get, nflcom_projections):
    """Test page fetching with error"""
    # Mock request exception
    import requests
    mock_get.side_effect = requests.RequestException("Network error")
    
    with pytest.raises(requests.RequestException):
        nflcom_projections._fetch_page("http://test.com")


def test_parse_projections_table_empty(nflcom_projections):
    """Test parsing empty table"""
    from bs4 import BeautifulSoup
    
    # Empty HTML
    soup = BeautifulSoup("<html><body></body></html>", 'html.parser')
    result = nflcom_projections._parse_projections_table(soup)
    assert result == []


def test_parse_projections_table_with_data(nflcom_projections):
    """Test parsing table with sample data"""
    from bs4 import BeautifulSoup
    
    # Sample HTML table
    html = """
    <html>
        <body>
            <table class="projections">
                <thead>
                    <tr>
                        <th>Player</th>
                        <th>Team</th>
                        <th>Position</th>
                        <th>Fantasy Points</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Josh Allen</td>
                        <td>BUF</td>
                        <td>QB</td>
                        <td>24.5</td>
                    </tr>
                    <tr>
                        <td>Christian McCaffrey</td>
                        <td>SF</td>
                        <td>RB</td>
                        <td>18.2</td>
                    </tr>
                </tbody>
            </table>
        </body>
    </html>
    """
    
    soup = BeautifulSoup(html, 'html.parser')
    result = nflcom_projections._parse_projections_table(soup)
    
    assert len(result) == 2
    assert result[0]['player'] == 'Josh Allen'
    assert result[0]['fantasy_points'] == 24.5
    assert result[1]['player'] == 'Christian McCaffrey'
    assert result[1]['fantasy_points'] == 18.2


@patch.object(NFLComProjections, '_fetch_page')
@patch.object(NFLComProjections, '_parse_projections_table')
def test_fetch_projections(mock_parse, mock_fetch, nflcom_projections):
    """Test full fetch_projections workflow"""
    from bs4 import BeautifulSoup
    
    # Mock the page fetch and parse
    mock_fetch.return_value = BeautifulSoup("<html></html>", 'html.parser')
    mock_parse.return_value = [
        {
            'player': 'Test Player',
            'team': 'KC', 
            'position': 'QB',
            'fantasy_points': 20.0,
            'season': 2025,
            'week': 1
        }
    ]
    
    df = nflcom_projections.fetch_projections()
    
    assert not df.empty
    assert 'plyr' in df.columns
    assert 'team' in df.columns
    assert 'pos' in df.columns
    assert 'proj' in df.columns
    assert len(df) == 1


@patch.object(NFLComProjections, '_fetch_page')  
@patch.object(NFLComProjections, '_parse_projections_table')
def test_fetch_projections_empty(mock_parse, mock_fetch, nflcom_projections):
    """Test fetch_projections with no data"""
    from bs4 import BeautifulSoup
    
    mock_fetch.return_value = BeautifulSoup("<html></html>", 'html.parser')
    mock_parse.return_value = []
    
    df = nflcom_projections.fetch_projections()
    
    assert df.empty