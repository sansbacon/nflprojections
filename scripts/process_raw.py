# nflprojections/scripts/process_raw.py
# -*- coding: utf-8 -*-
# Copyright (C) 2020 Eric Truett
# Licensed under the MIT License

import logging
from pathlib import Path

import click

from nflprojections import Rotogrinders



@click.command()
@click.option('-y', '--season', type=click.IntRange(2010, 2021), 
                 help='NFL season')
@click.option('-w', '--week', type=click.IntRange(1, 17), 
                 help='Week')
@click.option('-b', '--basedir', type=str, help='Base directory')
@click.option('-s', '--slate', type=str, default='main', help='Slate')
def run(season, week, basedir, slate):
    """Processes raw projections

    Args:
        season ([type]): [description]
        week ([type]): [description]
        basedir ([type]): [description]
        slate ([type]): [description]

    Raises:
        ValueError: [description]

    Returns:
        [type]: [description]
    """
    if not basedir:
        basedir = Path.home() / 'workspace' / 'nflprojections-data' / str(season) / str(week)

    rg = Rotogrinders(basedir, season, week, 'rg-core')
    df = rg.parse_rg_page()
    df = rg.process_raw(df)



if __name__ == '__run__':
    logging.basicConfig(level=logging.INFO)
    run()
