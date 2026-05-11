import pandas as pd

def get_tournaments() -> pd.DataFrame:
    df = pd.read_csv('data/all_ids/all_tournaments_stages_match_types_ids.csv')
    df = df[['Tournament ID', 'Tournament', 'Year']].drop_duplicates()
    df.rename(columns={'Tournament ID':'id', 'Tournament':'name', 'Year':'year'}, inplace=True)
    return df

def match_abbreviation(team:str, abb:pd.DataFrame) -> str|None:
    match = abb[abb['Full Name']==team]['Abbreviated']
    if len(match) == 1:
        # print(match)
        return list(match)[0]
    else:
        return None

def get_teams() -> pd.DataFrame:
    df = pd.read_csv('data/all_ids/all_teams_ids.csv')
    df = df[['Team ID','Team']]
    df = df[df.duplicated(subset=['Team ID'], keep="last")==False]
    abb = pd.read_csv('data/all_ids/all_teams_mapping.csv')
    df['Short Name'] = df['Team'].apply(match_abbreviation, abb=abb)
    # print(df[df.duplicated(subset=['Team ID'], keep=False)==True].sort_values('Team ID'))
    df.rename(columns={'Team ID':'id', 'Team':'name', 'Short Name':'short_name'}, inplace=True)
    return df

def get_players() -> pd.DataFrame:
    df = pd.read_csv('data/all_ids/all_players_ids.csv')
    df.dropna(inplace=True)
    df = df[df.duplicated(subset=['Player ID'], keep="last")==False]
    df = df[['Player ID', 'Player']]
    df['Player ID'] = pd.to_numeric(df['Player ID'], downcast="integer")
    df.rename(columns={'Player ID':'id', 'Player':'name'}, inplace=True)
    return df

def get_match_ids(year_from = None, tournament = None) -> pd.Series:
    df = pd.read_csv('data/all_ids/all_matches_games_ids.csv')
    if year_from != None:
        df = df[df['Year'] >= year_from]
    if tournament != None:
        df = df[df['Tournament ID'] == tournament]
    return df['Match ID'].unique()


if __name__ == '__main__':
    tournaments = get_tournaments()
    teams = get_teams()
    players = get_players()
    matches = get_match_ids()
    champs_25_matches = get_match_ids(tournament=2283)
    print(champs_25_matches)