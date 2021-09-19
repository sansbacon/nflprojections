"""
nf.py
classes for scraping, parsing numberfire projections

"""

import logging

import pandas as pd
from requests_html import HTMLSession


class Scraper:
    """
    Scrape numberfire for projections

    """

    def __init__(self):
        """Creates Scraper instance"""
        self._s = HTMLSession()

    @property
    def ros_url(self):
        return 'https://www.numberfire.com/nfl/fantasy/remaining-projections'
        
    def get(self, url, return_object=False):
        """Gets http response"""
        r = self._s.get(url)
        if return_object:
            return r
        return r.content

    def projections(self, week):
        """Gets all ESPN player projections """
        if week == 0:
            return self.get(self.ros_url)


class Parser:
    """
    Parse numberfire projections

    """

    def __init__(self):
        """Create object"""
        logging.getLogger(__name__).addHandler(logging.NullHandler())

    def projections(self, content):
        """Parses the seasonal projections
        
        Args:
            content(str): HTML

        Returns:
            DataFrame

        """
        t = pd.read_html(content)
        d = t[0].to_dict()
        vals = list(d.keys())
        vals += list(d[vals[0]].values())
        t[1].index = vals
        t[1].reset_index()
        t[1].columns = [b if a == '' else f'{a}_{b}' for a, b in t[1].columns]
        return t[1]


if __name__ == "__main__":
    pass
