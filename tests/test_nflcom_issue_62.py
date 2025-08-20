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
    assert player_data['pass_yds'] == 3619
    assert player_data['pass_td'] == 30
    assert player_data['pass_int'] == 9
    assert player_data['rush_yds'] == 832
    assert player_data['rush_td'] == 4
    assert player_data['fumb_lost'] == 4
    assert player_data['fumb_td'] == 1
    
    # Verify it does NOT produce the incorrect output from issue
    # Should not have these incorrect mappings:
    assert 'passing' not in player_data  # Should be pass_yds instead
    assert 'rushing' not in player_data  # Should be pass_td instead  
    assert 'receiving' not in player_data  # Should be pass_int instead
    assert 'ret' not in player_data  # Should be rush_yds instead
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
    assert result['pass_yds'] == 3619
    assert result['team'] == 'BAL'


def test_exact_issue_62_html_structure():
    """Test parsing the exact HTML structure from issue #62 description"""
    
    # This is the exact HTML structure from the issue description with player name added
    sample_html = """
    <html>
    <body>
        <div>
            Lamar Jackson QB BAL @BUF<span class="playerStat statId-1 playerId-2560757">16</span><span class="playerStat statId-5 playerId-2560757">3619</span><span class="playerStat statId-6 playerId-2560757">30</span><span class="playerStat statId-7 playerId-2560757">9</span><span class="playerStat statId-14 playerId-2560757">832</span><span class="playerStat statId-15 playerId-2560757">4</span><span class="playerStat statId-20 playerId-2560757"></span><span class="playerStat statId-21 playerId-2560757"></span><span class="playerStat statId-22 playerId-2560757"></span><span class="playerStat statId-28 playerId-2560757"></span><span class="playerStat statId-29 playerId-2560757">1</span><span class="playerStat statId-32 playerId-2560757"></span><span class="playerStat statId-30 playerId-2560757">4</span>351.96
        </div>
    </body>
    </html>
    """
    
    # Expected output dictionary from the issue description
    expected_output = {
        'player': 'Lamar Jackson',
        'position': 'QB',
        'team': 'BAL',
        'opp': 'BUF',
        'gp': 16,
        'pass_yds': 3619,
        'pass_td': 30,
        'pass_int': 9,
        'rush_yds': 832,
        'rush_td': 4,
        'rec': 0,
        'rec_yds': 0,
        'rec_td': 0,
        'ret_td': 0,
        'fumb_td': 1,
        'two_pt': 0,
        'fumb_lost': 4,
        'fantasy_points': 351.96
    }
    
    # Test the parser
    parser = NFLComParser()
    soup = BeautifulSoup(sample_html, 'html.parser')
    parsed_data = parser.parse_raw_data(soup)
    
    # Should have exactly one player record
    assert len(parsed_data) == 1
    
    player_data = parsed_data[0]
    
    # Verify all expected fields match exactly
    for key, expected_value in expected_output.items():
        assert key in player_data, f"Missing field: {key}"
        assert player_data[key] == expected_value, f"Field {key}: got {player_data[key]}, expected {expected_value}"