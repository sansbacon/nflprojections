"""
nflprojections.py
code for collecting / combining projection sources

"""
import json
import logging
from pathlib import Path
import re

import numpy as np
import pandas as pd

from . import espnapi, watson
from nflnames import standardize_team_code
from nflschedule import current_season, current_week


class ProjectionSource:

    DEFAULT_COLUMN_MAPPING = {}
    VALID_SITE_NAMES = ('dk', 'fd', 'all')
    VALID_SLATE_NAMES = ('main', 'all')

    def __init__(self, basedir, season, week, projections_name, site_name, slate_name):
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self.basedir = basedir
        self.season = season
        self.week = week
        self.projections_name = projections_name
        if site_name not in self.VALID_SITE_NAMES:
            raise ValueError(f'Invalid site name: {site_name}')
        self.site_name = site_name
        if slate_name not in self.VALID_SLATE_NAMES:
            raise ValueError(f'Invalid slate name: {slate_name}')
        self.slate_name = slate_name

    def load_raw(self):
        """Loads raw projections file"""
        return pd.read_csv(self.make_raw_fn())  
        
    def make_processed_fn(self):
        """Filename always has season/week/projections name and optional site/slate
        
        Examples:
            2020_w8_rg-core_dk_main
        """
        parts = [str(self.season), f'w{self.week}', self.projections_name, self.site_name, self.slate_name]
        return self.basedir / f'{"_".join([item for item in parts if item])}.csv'

    def make_raw_fn(self):
        """Filename always has season/week/projections name and optional site/slate
        
        Examples:
            2020_w8_rg-core_dk_main
        """
        parts = [str(self.season), f'w{self.week}', self.projections_name, self.site_name, self.slate_name]
        return self.basedir / f'raw/{"_".join([item for item in parts if item])}.csv'

    def process_raw(self):
        raise NotImplementedError

    def remap_columns(self, df, column_remap=None):
        mapper = column_remap if isinstance(column_remap, dict) else self.DEFAULT_COLUMN_MAPPING
        return [mapper.get(c, c) for c in df.columns]                        

    def standardize_teams(self, col):
        return col.apply(standardize_team_code)
                

class Dk(ProjectionSource):
    """Not a typical projection source, but is useful here
    
    NOTE: numeric IDs are not stable - just for slate
    """

    DEFAULT_COLUMN_MAPPING = {
        'ID': 'dk_slate_id',
        'Name': 'player',
        'Position': 'pos',
        'TeamAbbrev': 'team',
        'Salary': 'salary',
        'AvgPointsPerGame': 'fpts',
    }

    def __init__(self, **kwargs):
        if not kwargs.get('projections_name'):
            kwargs['projections_name'] = 'DKSalaries'
        if not kwargs.get('slate_name'):
            kwargs['slate_name'] = 'main'
        super().__init__(**kwargs)

    def process_raw(self, df, column_remap=None, column_prefix=None):
        """Processes raw dataframe
        
        Args:
            df (DataFrame): the raw dataframe
            column_remap (dict): remaps columns, if 'default', then use DEFAULT_COLUMN_MAPPING
            column_prefix (str): adds prefix to column names

        Returns:
            DataFrame
        """
        # convert column datatypes / fix names
        try:
            df['ID'] = df['ID'].astype(int)
            df['Salary'] = df['Salary'].astype(int)
            df.loc[df['Position'] == 'DST', 'Name'] = df.loc[df['Position'] == 'DST', 'Name'] + ' Defense'
            df.columns = self.remap_columns(df)
        except KeyError:
            pass

        if column_prefix:
            df.columns = [f'{column_prefix}_{c}' for c in df.columns]  

        return df


class Espn(ProjectionSource):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.projections_name = 'espn'
        self._s = espnapi.Scraper(kwargs.get('season'))
        self._p = espnapi.Parser(kwargs.get('season'))

    def load_raw(self):
        """Loads raw projections from ESPN"""
        data = self._s.playerstats()
        return self._p.weekly_projections(data, self.week)


class EstablishTheRun(ProjectionSource):
    """Collects/parses projections from establishtherun.com
    NOTE: subscription required, this is post-processing after valid download
    """

    DEFAULT_COLUMN_MAPPING = {
        'DK Position': 'pos',
        'DK Salary': 'salary',
        'DK Projection': 'fpts',
        'DK Value': 'value',
        'DK Ownership': 'ownership',
        'DKSlateID': 'dk_slate_id',
        'Opponent': 'opp',
        'Team': 'team',
        'Player': 'player'
    }

    def __init__(self, **kwargs):
        if not kwargs.get('projections_name'):
            kwargs['projections_name'] = 'etr'
        if not kwargs.get('site_name'):
            kwargs['site_name'] = 'dk'
        if not kwargs.get('slate_name'):
            kwargs['slate_name'] = 'main'
        super().__init__(**kwargs)
       
    def process_raw(self, df, column_remap=None):
        """Processes raw dataframe"""
        df.columns = self.remap_columns(df, column_remap)
        if df['ownership'].dtype == str:
            df['ownership'] = df['ownership'].str.replace('%', '').astype(int)
        if df['salary'].dtype == str:
            df['salary'] = pd.to_numeric(df['salary'].str.replace('$', ''), errors='coerce').fillna(0).astype(int)
        df = df.dropna(thresh=7)
        df.loc[:, 'dk_slate_id'] = df.loc[:, 'dk_slate_id'].astype(int)
        return df


class Ffa(ProjectionSource):
    """Collects/parses consensus projections from ffanalytics R library"""

    DEFAULT_COLUMN_MAPPING = {
        'id': 'mfl_id',
        'points': 'fpts'
    }

    def add_salaries(self, saldf, xref):
        """Adds salaries to Ffa projections
        
        Args:
            saldf (DataFrame): salaries dataframe
            xref (dict): key is ffa player id, value is saldf player id
        TODO: Need salaries dataframe and id cross-reference
        """
        pass

    def process_raw(self, df, column_remap=None, column_prefix=None):
        """Processes raw dataframe
        
        Args:
            df (DataFrame): the raw dataframe
            column_remap (dict): remaps columns, if 'default', then use DEFAULT_COLUMN_MAPPING
            column_prefix (str): adds prefix to column names

        Returns:
            DataFrame
        """
        mapper = column_remap if isinstance(column_remap, dict) else self.DEFAULT_COLUMN_MAPPING
        df.columns = [mapper.get(c, c) for c in df.columns]                        
        
        if column_prefix:
            df.columns = [f'{column_prefix}_{c}' for c in df.columns]  
        return df


class Rotogrinders(ProjectionSource):
    """Collects/parses projections from rotogrinders.com
       NOTE: subscription required, this is post-processing after valid download
    """

    def parse_rg_page(self, save_file=False):
        """Parses HTML source of rotogrinders page
        
        NOTE: Must have appropriate RG subscription (Core, Blitz, etc.) for HTML to parse properly
        """
        parts = (str(self.season), f'w{self.week}', self.projections_name, self.site_name, self.slate_name)
        htmlfn = self.basedir / 'raw' / f'{"_".join(parts)}.html'
        html = htmlfn.read_text()
        patt = r'selectedExpertPackage: ({.*?],"title":.*?"product_id".*?}),\s+serviceURL'
        match = re.search(patt, html, re.MULTILINE | re.DOTALL)
        proj = json.loads(match.group(1))
        df = pd.DataFrame(proj['data'])

        # fix columns
        df = df.drop(columns=['SCHEDULE_ID', 'FPTS/$'])
        df.columns = [c.lower() for c in df.columns]

        # get rid of incomplete records
        df = df.dropna(thresh=7) 

        # convert types
        df['fpts'] = pd.to_numeric(df['fpts'], errors='coerce')
        df['floor'] = pd.to_numeric(df['floor'], errors='coerce')
        df['ceil'] = pd.to_numeric(df['ceil'], errors='coerce')
        df['salary'] = pd.to_numeric(df['salary'], errors='coerce', downcast='integer') 

        # fix missing values
        df.loc[:, 'floor'] = np.where(df['floor'] >= 0, df['floor'], (df['fpts'] - 1) / 4)
        df.loc[:, 'ceil'] = np.where(df['ceil'] >= 0, df['ceil'], (df['fpts'] * 1.5))

        # save results
        if save_file:
            outfn = self.basedir / f'{"_".join(parts)}.csv'
            df.to_csv(outfn, index=False)

        return df

    def process_raw(self, df, fix_dst_names=True, column_prefix=None, remove_kickers=True):
        """Processes raw dataframe. Note some processing already in scraping HTML
        
        Args:
            df (DataFrame): the raw dataframe
            fix_dst_name (bool): changes San Francisco 49ers to 49ers Defense
            column_prefix (str): adds prefix to column names
            remove_kickers (bool): removes K from projections
        """
        if fix_dst_names:
            dst_names = df.loc[df.pos == 'DST', 'player'].str.split().str[-1] + ' Defense' 
            df.loc[df.pos == 'DST', 'player'] = dst_names
        if remove_kickers:
            df = df.loc[df.pos != 'K', :]
        if column_prefix:
            df.columns = [f'{column_prefix}_{c}' for c in df.columns]  
        return df


class Watson(ProjectionSource):
    """ESPN Watson projections"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.projections_name = 'watson'
        self._s = watson.Scraper(kwargs.get('season'))
        self._p = watson.Parser()

    def _clean_watson_names(self, df):
        """Fixes Watson names
        
        TODO: adapt to existing framework
        """
        # need to fix DST names
        # remove D/ST from ESPN names before adding to index
        return (
            df
            .loc[df['pos'] == 'DST', 'plyr'] 
            .str.split().str[0]
        )

    def load_raw(self):
        """Loads raw Watson projections"""
        # STEP ONE: get Watson players
        players = self._s.players().json()

        # STEP TWO: get Watson projections
        projections = []
        for player in players:
            data = self._s.projection(player['PLAYERID'])
            projections.append = self._p.projection(data[-1])          
        return pd.DataFrame(projections)

    def process_raw(self):
        """Processes raw projections"""
        pass


if __name__ == '__pass__':
    pass
    
