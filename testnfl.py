from nflprojections import NFLComProjections

nfl = NFLComProjections(season=2025, week=0)
raw_data = nfl.fetch_raw_data(season=2025)
parsed = nfl.parse_data(raw_data)
print(parsed)