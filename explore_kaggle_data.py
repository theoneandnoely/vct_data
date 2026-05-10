import pandas as pd
import numpy as np
from bs4 import BeautifulSoup

teams = pd.read_csv('data/all_ids/all_teams_ids.csv')
team_mappings = pd.read_csv('data/all_ids/all_teams_mapping.csv')
# tournament_stages = pd.read_csv('data/all_ids/all_tournaments_stages_match_types_ids.csv')
players = pd.read_csv('data/all_ids/all_players_ids.csv')
# matches = pd.read_csv('data/all_ids/all_matches_games_ids.csv')

# print('\nTEAMS\n--------------\n')
# print(teams.columns)

# print('\nMAPPINGS\n----------------\n')
# print(team_mappings.columns)

# print('\nTOURNAMENTS\n--------------\n')
# print(tournament_stages.columns)

# print('\nPLAYERS\n----------------\n')
# print(players.columns)

# print('\nMATCHES\n-----------------\n')
# print(matches.columns)

# matches = matches[matches['Tournament ID'] == 449]
# match_ids = matches['Match ID'].unique()
# print(match_ids[0])

# with requests.get(f'https://www.vlr.gg/{match_ids[0]}') as page:
#     if page.status_code == 200:
#         soup = BeautifulSoup(page.text, 'html.parser')
#     else:
#         print(page.status_code)

# match_header = soup.find_all('div', {'class':'match-header-date'})[0]

# print(match_header.div['data-utc-ts'])
# print(match_header.find_all('div',{'style':'font-style: italic;'})[0].text.strip())

# print(f'Shape: {team_mappings.shape}\nUnique Teams: {team_mappings['Full Name'].unique().shape}')

# team_mappings_dupes = team_mappings[team_mappings.duplicated(subset=['Full Name'], keep=False) == True].sort_values('Full Name')
# for i, r in team_mappings_dupes.iterrows():
#     print(f'{r['Full Name']}\t{r['Abbreviated']} ({i})')
# print(team_mappings_dupes)

# team_dupes = teams[teams.duplicated(subset=['Team'], keep=False) == True].sort_values('Team')
# print(team_dupes)

# print(players[players['Player ID'] <= 0])

print(teams[teams.duplicated(subset=['Team ID'], keep=False)==True])

teams_clean = teams[teams.duplicated(subset=['Team ID'], keep="last")==False]
print(teams_clean[teams_clean.duplicated(subset=['Team'], keep=False)==True])