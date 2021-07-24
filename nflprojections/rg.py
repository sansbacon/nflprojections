"""
rg.py    

Library to scrape Rotogrinders projections

NOTE: Subscription is required
This library does not access to anything 'extra' that user didn't buy
It automates projections download for an authorized user (via browser_cookie3)

"""

import logging

from requests_html import HTMLSession
import browser_cookie3
import pandas as pd


class Scraper:
    """Scrape RG projections"""

    BASE_URL = 'https://establishtherun.com'

    def __init__(self, urls=None, browser_name='chrome'):
        """Creates Scraper instance"""
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self._s = HTMLSession()
        if browser_name == 'chrome':
            self._s.cookies.update(browser_cookie3.chrome())
        elif browser_name == 'firefox':
            self._s.cookies.update(browser_cookie3.firefox())
        else:
            raise ValueError(f'Invalid browser_name: {browser_name}')
        if not urls:
            self.urls = {
                'all_all': f'{self.BASE_URL}/fantasy-point-projections/',
                'dk_main': f'{self.BASE_URL}/draftkings-projections/',
                'fd_main': f'{self.BASE_URL}/fanduel-projections/'
            }
        else:
            self.urls = urls

    def get(self, url, headers=None, params=None, return_object=False):
        """Gets HTML response"""
        r = self._s.get(url, headers=headers, params=params)
        if return_object:
            return r
        return r.text

    def get_projections(self, site_name='all', slate_name='all'):
        """Gets projections"""
        key = f'{site_name}_{slate_name}'
        url = self.URLS.get(key)
        if not url:
            raise ValueError(f'Invalid site or slate: {site_name}, {slate_name}')
        return self.get(url)


class Parser:
    """Parse ETR Projections table"""

    def __init__(self):
        """
            """
        logging.getLogger(__name__).addHandler(logging.NullHandler())

    def projections(self, html):
        """Parses projections HTML"""
        tbl = pd.read_html(html)
        return tbl[1]


if __name__ == '__main__':
    pass