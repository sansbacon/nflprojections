"""
rg.py    

Library to scrape Rotogrinders projections

NOTE: Subscription is required
You must have firefox installed and have logged in to rotogrinders in that browser + profile
This library does not access to anything 'extra' that user didn't buy
It automates projections download for an authorized user (via browser_cookie3)

"""
import json
import logging
import re
from typing import Any, Dict, List, Union

import requests
from requests.models import Response
import browser_cookie3


class Scraper:
    """Scrape RG projections
    
    
    Example:
        params = {
          'site': 'draftkings', 
          'slate': '53019', 
          'projections': 'grid', 
          'date': '2021-09-12',
          'post': '2009661'    
        }

        s = Scraper()
        url = self.construct_url(params)
        content = self.get(url)

    """

    def __init__(self):
        """Creates Scraper instance"""
        self._s = requests.Session()
        self._s.cookies.update(browser_cookie3.firefox())

    def construct_url(self, params: dict) -> str:
        """Constructs URL given params
        
        Args:
            params (Dict[str, str]): the url parameters

        Returns:
            str

        """
        url = 'https://rotogrinders.com/lineuphq/nfl?site={site}&slate={slate}&projections=grid&date={date}&post={post}'
        return url.format(**params)


    def get(self, url: str, headers: dict = None, params: dict = None, return_object: bool = False) -> Union[str, Response]:
        """Gets HTML response"""
        r = self._s.get(url, headers=headers, params=params)
        if return_object:
            return r
        return r.text

    def lineuphq_projections(self, params: dict) -> str:
        """Gets projections given aparms"""
        return self.get(self.construct_url(params))


class Parser:
    """Parse projections html
    
    Examples:
        from pathlib import Path
        from nflprojections.rg import Parser

        pth = Path('html_file.html')
        html = pth.read_text()
        p = Parser()
        proj = p.lineuphq_projections(html)

    """
    PROJ_PATT = re.compile(r'selectedExpertPackage: ({.*?],"title":.*?"product_id".*?}),\s+serviceURL') 

    def lineuphq_projections(self, html: str, patt: re.Pattern = PROJ_PATT) -> List[Dict[str, Any]]:
        """Parses projections HTML"""
        match = re.search(patt, html, re.MULTILINE | re.DOTALL)
        return json.loads(match.group(1))['data']


if __name__ == '__main__':
    pass
