import json
import logging
import random

import numpy as np
import pandas as pd
from requests_html import HTMLSession


class Scraper:

    def __init__(self, season):
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self._s = HTMLSession()       
        self.season = season

    @property
    def base_url(self):
        return 'https://watsonfantasyfootball.espn.com/espnpartner/dallas/'

    def get(self, url):
        return self._s.get(url)
        
    def player(self, player_id):
        """Gets single Watson player"""
        url = f'players/players_{player_id}_ESPNFantasyFootball_{self.season}.json'
        return self.get(self.base_url + url)

    def players(self):
        """Gets list of all Watson players"""
        url = 'players/players_ESPNFantasyFootball_{self.season}.json'
        return self.get(self.base_url + url)
       
    def projection(self, player_id):
        """Gets Watson projection for single player"""
        url = f'projections/projections_{player_id}_ESPNFantasyFootball_{self.season}.json'
        return self.get(self.base_url + url)


class Parser:
    """Parse Watson projections"""

    def __init__(self):
        logging.getLogger(__name__).addHandler(logging.NullHandler())
    
    def projection(self, player):
        """Parses player JSON"""
        pass

    def projection_distribution(self, player):
        '''
        Returns distribution of scores for player

        Returns:
            list: of float

        '''
        try:
            return [s[0] for s in json.loads(player['SCORE_DISTRIBUTION'])]
        except:
            return None

    def randomize_watson(projections, percentiles=(25, 75)):
        """
        Uses range of projections to optimize

        """
        players = []
        for player in projections:
            # score_distribution is a list of lists
            # can use zip with * operator to unpack
            new_player = {k: v for k,v in player.items() if k != 'score_distribution'}  
            scores, probs = zip(*player['score_distribution'])
            pctfloor, pctceil = np.percentile(scores, percentiles)
            score_range = [score for score in scores if score >= pctfloor and score <= pctceil]
            new_player['dist'] = random.choice(score_range)
            players.append(new_player)
        return players


if __name__ == '__main__':
    pass
