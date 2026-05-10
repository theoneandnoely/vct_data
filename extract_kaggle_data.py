import pandas as pd

def get_tournaments():
    df = pd.read_csv('data/all_ids/all_tournaments_stages_match_types_ids.csv')
    return df[['Tournament ID', 'Tournament', 'Year']].drop_duplicates()

def get_teams():
    df = pd.read_csv('data/all_ids/all_teams_ids.csv')
    df = df[['Team ID','Team']]
    abb = pd.read_csv('data/all_ids/all_teams_mapping.csv')
    abb.rename(columns={'Full Name':'Team', 'Abbreviated':'Short Name'}, inplace=True)
    df = df.join(abb.set_index('Team'), on='Team', validate='m:m')
    return df

def get_players():
    df = pd.read_csv('data/all_ids/all_players_ids.csv')
    return df[['Player ID', 'Player']]

def get_match_ids(year_from = None):
    df = pd.read_csv('data/all_ids/all_matches_games_ids.csv')
    if year_from != None:
        df = df[df['Year'] >= year_from]
    return df['Match ID'].unique()


if __name__ == '__main__':
    tournaments = get_tournaments()
    teams = get_teams()
    players = get_players()
    matches = get_match_ids()
    print(len(matches))
    matches_partnership = get_match_ids(2023)
    print(len(matches_partnership))