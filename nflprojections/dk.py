"""
dk.py

draftkings salaries/data
"""

import json


with open('getcontests.json', 'r') as f:
    data = json.load(f)
gs = data['GameSets']
for gs in data['GameSets']:
    print(gs['GameSetKey'], gs['ContestStartTimeSuffix'])
for gs in data['GameSets']:
    print(gs['GameSetKey'], gs['ContestStartTimeSuffix'], gs['Tag'])
for gs in data['GameSets']:
    print(gs['GameSetKey'], gs['ContestStartTimeSuffix'], gs['Tag'], f'{len(gs['Competitions'])} games')
for gs in data['GameSets']:
    print(gs['GameSetKey'], gs['ContestStartTimeSuffix'], gs['Tag'], f'{len(gs["Competitions"])} games')
# exclude Madden from list
for gs in data['GameSets']:
    if 'Madden' in gs['ContestStartTimeSuffix']:
        continue
    print(gs['GameSetKey'], gs['ContestStartTimeSuffix'], gs['Tag'], f'{len(gs["Competitions"])} games')
for gset in data['GameSets']:
    if 'Madden' in gset['ContestStartTimeSuffix']:
        continue
    print(gset['GameSetKey'], gset['ContestStartTimeSuffix'], gset['Tag'], f'{len(gset["Competitions"])} games')
    print('\t', '; '.join([gstyle['Abbreviation'] for gstyle in gs['GameStyles']]))
for gset in data['GameSets']:
    if 'Madden' in gset['ContestStartTimeSuffix']:
        continue
    print(gset['GameSetKey'], gset['ContestStartTimeSuffix'], gset['Tag'], f'{len(gset["Competitions"])} games')
    print('', '; '.join([gstyle['Abbreviation'] for gstyle in gset['GameStyles']]))
# CLA, SHW, Tiers
# Can exclude PKM, BB
# https://api.draftkings.com/draftgroups/v1/draftgroups/41643/draftables?format=json
# can get draftables from above URL
# contests JSON has GameSetKey to link gamesets and draftgroups
url = 'https://api.draftkings.com/draftgroups/v1/draftgroups/41643/draftables?format=json'
import requests
r = requests.get(url)
r.json()
%history

