import pandas as pd

def get_tournaments() -> pd.DataFrame:
    df = pd.read_csv('data/all_ids/all_tournaments_stages_match_types_ids.csv')
    df = df[['Tournament ID', 'Tournament', 'Year']].drop_duplicates()
    df.rename(columns={'Tournament ID':'id', 'Tournament':'name', 'Year':'year'}, inplace=True)
    return df

def get_teams() -> pd.DataFrame:
    df = pd.read_csv('data/all_ids/all_teams_ids.csv')
    df = df[['Team ID','Team']]
    df = df[df.duplicated(subset=['Team ID'], keep="last")==False]
    abb = pd.read_csv('data/all_ids/all_teams_mapping.csv')
    abb.rename(columns={'Full Name':'Team', 'Abbreviated':'Short Name'}, inplace=True)
    print(df[df.duplicated(subset=['Team ID'], keep=False)==True].sort_values('Team ID'))
    df = df.join(abb.set_index('Team'), on='Team', validate='1:m')
    print(df[df.duplicated(subset=['Team ID'], keep=False)==True].sort_values('Team ID'))
    df.rename(columns={'Team ID':'id', 'Team':'name', 'Short Name':'short_name'}, inplace=True)
    return df

def get_players() -> pd.DataFrame:
    df = pd.read_csv('data/all_ids/all_players_ids.csv')
    df.dropna(inplace=True)
    df = df[['Player ID', 'Player']]
    df['Player ID'] = pd.to_numeric(df['Player ID'], downcast="integer")
    df.rename(columns={'Player ID':'id', 'Player':'name'}, inplace=True)
    return df

def get_match_ids(year_from = None) -> pd.Series:
    df = pd.read_csv('data/all_ids/all_matches_games_ids.csv')
    if year_from != None:
        df = df[df['Year'] >= year_from]
    return df['Match ID'].unique()


if __name__ == '__main__':
    tournaments = get_tournaments()
    teams = get_teams()
    players = get_players()
    matches = get_match_ids()