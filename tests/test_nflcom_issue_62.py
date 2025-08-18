import pytest
from unittest.mock import Mock, patch
import pandas as pd
from bs4 import BeautifulSoup

from nflprojections.sources import NFLComProjections
from nflprojections.parse.nflcom_parser import NFLComParser


def test_parse_issue_62_fix():
    """Test that issue #62 is fixed - NFL Parser should produce correct output format"""
    
    # Mock HTML that represents the problematic structure from issue #62
    problematic_html = """
    <html>
    <body>
        <table>
            <thead>
                <tr>
                    <th>Player</th>
                    <th>Passing</th>
                    <th>Rushing</th>
                    <th>Receiving</th>
                    <th>Ret</th>
                    <th>Misc</th>
                    <th>Fum</th>
                    <th>Fantasy</th>
                    <th>Opp</th>
                    <th>GP</th>
                    <th>Yds</th>
                    <th>TD</th>
                    <th>Int</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Lamar Jackson BAL</td>
                    <td>3619</td>
                    <td>30</td>
                    <td>9</td>
                    <td>832</td>
                    <td>4</td>
                    <td>4</td>
                    <td>-</td>
                    <td>BUF</td>
                    <td>16</td>
                    <td>-</td>
                    <td>1</td>
                    <td>351.96</td>
                </tr>
            </tbody>
        </table>
    </body>
    </html>
    """
    
    # Test the parser directly
    parser = NFLComParser()
    soup = BeautifulSoup(problematic_html, 'html.parser')
    parsed_data = parser.parse_raw_data(soup)
    
    # Should have one player record
    assert len(parsed_data) == 1
    
    player_data = parsed_data[0]
    
    # Verify correct output format (from issue description expected output)
    assert player_data['player'] == 'Lamar Jackson'
    assert player_data['team'] == 'BAL'
    assert player_data['opp'] == 'BUF'
    assert player_data['gp'] == 16
    assert player_data['fantasy_points'] == 351.96
    assert player_data['pass_yd'] == 3619
    assert player_data['pass_td'] == 30
    assert player_data['pass_int'] == 9
    assert player_data['rush_yd'] == 832
    assert player_data['rush_td'] == 4
    assert player_data['fumb_lost'] == 4
    assert player_data['fumb_td'] == 1
    
    # Verify it does NOT produce the incorrect output from issue
    # Should not have these incorrect mappings:
    assert 'passing' not in player_data  # Should be pass_yd instead
    assert 'rushing' not in player_data  # Should be pass_td instead  
    assert 'receiving' not in player_data  # Should be pass_int instead
    assert 'ret' not in player_data  # Should be rush_yd instead
    assert 'misc' not in player_data  # Should be rush_td instead
    
    # Fantasy points should not be 16.0 (incorrect) but 351.96 (correct)
    assert player_data['fantasy_points'] != 16.0
    assert player_data['fantasy_points'] == 351.96
    
    # Player name should not be "-" (incorrect) but "Lamar Jackson" (correct)
    assert player_data['player'] != '-'
    assert player_data['player'] == 'Lamar Jackson'


def test_full_integration_issue_62():
    """Test the full NFLComProjections integration with the parser fix"""
    
    # Create NFLComProjections instance
    nfl = NFLComProjections(season=2025, week=0)
    
    # Mock HTML structure
    html_content = """
    <html>
    <body>
        <table>
            <thead>
                <tr>
                    <th>Player</th>
                    <th>Passing</th>
                    <th>Rushing</th>
                    <th>Receiving</th>
                    <th>Ret</th>
                    <th>Misc</th>
                    <th>Fum</th>
                    <th>Fantasy</th>
                    <th>Opp</th>
                    <th>GP</th>
                    <th>Yds</th>
                    <th>TD</th>
                    <th>Int</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Lamar Jackson BAL</td>
                    <td>3619</td>
                    <td>30</td>
                    <td>9</td>
                    <td>832</td>
                    <td>4</td>
                    <td>4</td>
                    <td>-</td>
                    <td>BUF</td>
                    <td>16</td>
                    <td>-</td>
                    <td>1</td>
                    <td>351.96</td>
                </tr>
            </tbody>
        </table>
    </body>
    </html>
    """
    
    # Parse with the NFLComProjections interface
    soup = BeautifulSoup(html_content, 'html.parser')
    parsed = nfl.parse_data(soup)
    
    # Should get the correct structure
    assert len(parsed) == 1
    result = parsed[0]
    
    # Verify key fields are correct
    assert result['player'] == 'Lamar Jackson'
    assert result['fantasy_points'] == 351.96
    assert result['pass_yd'] == 3619
    assert result['team'] == 'BAL'