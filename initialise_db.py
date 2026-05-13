import sqlite3
from os.path import exists
from extract_kaggle_data import get_tournaments, get_teams, get_players

def drop_tables(curs:sqlite3.Cursor) -> None:
    curs.executescript('''
                       DROP TABLE IF EXISTS tournaments;
                       DROP TABLE IF EXISTS regions;
                       DROP TABLE IF EXISTS teams;
                       DROP TABLE IF EXISTS players;
                       DROP TABLE IF EXISTS patches;
                       DROP TABLE IF EXISTS maps;
                       DROP TABLE IF EXISTS agents;
                       DROP TABLE IF EXISTS matches;
                       DROP TABLE IF EXISTS games;
                       DROP TABLE IF EXISTS player_game_history;
                        ''')
    curs.connection.commit()
    return None

def create_vct_tables(curs:sqlite3.Cursor) -> None:

    # Enable FOREIGN KEYS constraints
    curs.execute('PRAGMA foreign_keys = 1;')

    # Tournaments
    curs.execute('''
                CREATE TABLE tournaments (
                    id      INTEGER PRIMARY KEY, 
                    name    TEXT, 
                    year    INTEGER,
                    region  INTEGER REFERENCES regions(id)
                );
                ''')
    # Regions
    curs.execute('''
                CREATE TABLE regions (
                    id      INTEGER PRIMARY KEY,
                    name    TEXT
                );
                ''')
    # Teams
    curs.execute('''
                CREATE TABLE teams (
                    id          INTEGER PRIMARY KEY, 
                    name        TEXT, 
                    short_name  TEXT
                );
                ''')
    # Players
    curs.execute('''
                CREATE TABLE players (
                    id              INTEGER PRIMARY KEY, 
                    name            TEXT,
                    current_team    INTEGER REFERENCES teams(id)
                );
                ''')
    # Patches
    curs.execute('''
                CREATE TABLE patches (
                    id              INTEGER PRIMARY KEY,
                    patch_number    TEXT,
                    release_date    TEXT,
                    map_1           INTEGER REFERENCES maps(id),
                    map_2           INTEGER REFERENCES maps(id),
                    map_3           INTEGER REFERENCES maps(id),
                    map_4           INTEGER REFERENCES maps(id),
                    map_5           INTEGER REFERENCES maps(id),
                    map_6           INTEGER REFERENCES maps(id),
                    map_7           INTEGER REFERENCES maps(id)
                );
                ''')
    # Maps
    curs.execute('''
                CREATE TABLE maps (
                    id                  INTEGER PRIMARY KEY,
                    name                TEXT,
                    in_current_patch    INTEGER
                );
                ''')
    # Agents
    curs.execute('''
                CREATE TABLE agents (
                    id          INTEGER PRIMARY KEY,
                    name        TEXT,
                    class_id    INTEGER,
                    class       TEXT,
                    patch_added INTEGER REFERENCES patches(id)
                );
                ''')
    # Matches
    curs.execute('''
                CREATE TABLE matches (
                    id                  INTEGER PRIMARY KEY,
                    tournament          INTEGER REFERENCES tournaments(id),
                    match_date          TEXT,
                    team_a              INTEGER REFERENCES teams(id),
                    team_b              INTEGER REFERENCES teams(id),
                    patch               INTEGER REFERENCES patches(id),
                    best_of             INTEGER,
                    veto_order_a_first  INTEGER,
                    team_a_ban_1        INTEGER REFERENCES maps(id),
                    team_b_ban_1        INTEGER REFERENCES maps(id),
                    team_a_pick_1       INTEGER REFERENCES maps(id),
                    team_b_pick_1       INTEGER REFERENCES maps(id),
                    team_a_ban_2        INTEGER REFERENCES maps(id),
                    team_b_ban_2        INTEGER REFERENCES maps(id),
                    decider             INTEGER REFERENCES maps(id),
                    team_a_pick_2       INTEGER REFERENCES maps(id),
                    team_b_pick_2       INTEGER REFERENCES maps(id)
                );
                ''')
    # Games
    curs.execute('''
                CREATE TABLE games (
                    id                  INTEGER PRIMARY KEY,
                    match_id            INTEGER REFERENCES matches(id),
                    map                 INTEGER REFERENCES maps(id),
                    team_a_score        INTEGER,
                    team_a_att          INTEGER,
                    team_a_def          INTEGER,
                    team_a_ot           INTEGER,
                    team_b_score        INTEGER,
                    team_b_att          INTEGER,
                    team_b_def          INTEGER,
                    team_b_ot           INTEGER,
                    a_1_player          INTEGER REFERENCES players(id),
                    a_2_player          INTEGER REFERENCES players(id),
                    a_3_player          INTEGER REFERENCES players(id),
                    a_4_player          INTEGER REFERENCES players(id),
                    a_5_player          INTEGER REFERENCES players(id),
                    b_1_player          INTEGER REFERENCES players(id),
                    b_2_player          INTEGER REFERENCES players(id),
                    b_3_player          INTEGER REFERENCES players(id),
                    b_4_player          INTEGER REFERENCES players(id),
                    b_5_player          INTEGER REFERENCES players(id)
                );
                ''')
    # Player History
    curs.execute('''
                 CREATE TABLE player_game_history (
                    id              INTEGER PRIMARY KEY,
                    player_id       INTEGER REFERENCES players(id),
                    game_id         INTEGER REFERENCES games(id),
                    agent           INTEGER REFERENCES agents(id),
                    kills_tot       INTEGER,
                    kills_att       INTEGER,
                    kills_def       INTEGER,
                    deaths_tot      INTEGER,
                    deaths_att      INTEGER,
                    deaths_def      INTEGER,
                    assists_tot     INTEGER,
                    assists_att     INTEGER,
                    assists_def     INTEGER,
                    first_kills     INTEGER,
                    fk_att          INTEGER,
                    fk_def          INTEGER,
                    first_deaths    INTEGER,
                    fd_att          INTEGER,
                    fd_def          INTEGER,
                    vlr_rating_tot  REAL,
                    vlr_rating_att  REAL,
                    vlr_rating_def  REAL
                 );
                 ''')
    
    # Commit Changes to DB, print success message and return
    curs.connection.commit()
    print("Created tournaments, regions, teams, players, patches, maps, agents, matches, games, and player_game_history tables.")
    return None

def populate_kaggle_data(curs:sqlite3.Cursor) -> None:
    # Tournaments
    tournaments = get_tournaments()
    tournaments.to_sql('tournaments', curs.connection, if_exists='append', index=False)
    print("tournaments table populated with kaggle data")

    # Teams
    teams = get_teams()
    teams.to_sql('teams', curs.connection, if_exists='append', index=False)
    print("teams table populated with kaggle data")

    # Players
    players = get_players()
    players.to_sql('players', curs.connection, if_exists='append', index=False)
    print("players table populated with kaggle data")

    return None

def populate_maps(curs:sqlite3.Cursor) -> None:
    maps = [
        ('Ascent',),
        ('Bind',),
        ('Haven',),
        ('Split',),
        ('Icebox',),
        ('Breeze',),
        ('Fracture',),
        ('Pearl',),
        ('Lotus',),
        ('Sunset',),
        ('Abyss',),
        ('Corrode',)
    ]
    sql_query = 'INSERT INTO maps (name) VALUES (?)'
    curs.executemany(sql_query, maps)
    curs.connection.commit()

    print("maps table populated.")
    return None

def init_db() -> None:
    # Ensure database does not already exist
    if exists('vct_data.db'):
        c = input('vct_data.db already exists. Do you want to reset the database? (Y/N)')
        if c.strip().upper() == 'Y':
            conn = sqlite3.connect('vct_data.db')
            curs = conn.cursor()
            drop_tables(curs)
            print('Successfully dropped all tables in vct_data.db')
            conn.close()
        elif c.strip().upper() == 'N':
            return None
        else:
            raise ValueError(f'"{c}" is not a valid input')

    # Create db connection and cursor object
    conn = sqlite3.connect('vct_data.db')
    curs = conn.cursor()

    # Create tables
    create_vct_tables(curs)

    # Populate from kaggle data
    populate_kaggle_data(curs)

    # Populate maps
    populate_maps(curs)

    # Close database connection
    conn.close()

if __name__ == '__main__':
    init_db()