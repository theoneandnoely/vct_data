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
                       DROP TABLE IF EXISTS guns;
                       DROP TABLE IF EXISTS patch_map_pool;
                       DROP TABLE IF EXISTS patch_agent_abilities;
                       DROP TABLE IF EXISTS patch_guns;
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
                    tournament_id  INTEGER PRIMARY KEY, 
                    name            TEXT, 
                    year            INTEGER,
                    region          INTEGER REFERENCES regions(region_id)
                );
                ''')
    # Regions
    curs.execute('''
                CREATE TABLE regions (
                    region_id   INTEGER PRIMARY KEY,
                    name        TEXT
                );
                ''')
    # Teams
    curs.execute('''
                CREATE TABLE teams (
                    team_id     INTEGER PRIMARY KEY, 
                    name        TEXT, 
                    short_name  TEXT
                );
                ''')
    # Players
    curs.execute('''
                CREATE TABLE players (
                    player_id       INTEGER PRIMARY KEY, 
                    name            TEXT,
                    current_team    INTEGER REFERENCES teams(team_id)
                );
                ''')
    # Patches
    curs.execute('''
                CREATE TABLE patches (
                    patch_id        INTEGER PRIMARY KEY,
                    patch_number    TEXT,
                    release_date    TEXT
                );
                ''')
    # Maps
    curs.execute('''
                CREATE TABLE maps (
                    map_id              INTEGER PRIMARY KEY,
                    name                TEXT
                );
                ''')
    # Agents
    curs.execute('''
                CREATE TABLE agents (
                    agent_id        INTEGER PRIMARY KEY,
                    name            TEXT,
                    class           TEXT
                );
                ''')
    # Guns
    curs.execute('''
                CREATE TABLE guns (
                    gun_id      INTEGER PRIMARY KEY,
                    name        TEXT,
                    category    TEXT
                );
                ''')
    # Patch Map Pool
    curs.execute('''
                CREATE TABLE patch_map_pool (
                    patch_id    INTEGER REFERENCES patches(patch_id),
                    map_id      INTEGER REFERENCES maps(map_id),
                    PRIMARY KEY (patch_id, map_id)
                ); 
                ''')
    # Patch Agent Abilities
    curs.execute('''
                CREATE TABLE patch_agent_abilities (
                    patch_id        INTEGER REFERENCES patches(patch_id),
                    agent_id        INTEGER REFERENCES agents(agent_id),
                    ability         TEXT,
                    cost            INTEGER,
                    ability_type    TEXT
                );
                ''')
    # Patch Guns
    curs.execute('''
                CREATE TABLE patch_guns (
                    patch_id    INTEGER REFERENCES patches(patch_id),
                    gun_id      INTEGER REFERENCES guns(gun_id),
                    cost        INTEGER,
                    head_dmg    INTEGER,
                    body_dmg    INTEGER,
                    leg_dmg     INTEGER
                );
                ''')
    # Matches
    curs.execute('''
                CREATE TABLE matches (
                    match_id            INTEGER PRIMARY KEY,
                    tournament_id       INTEGER REFERENCES tournaments(tournament_id),
                    match_date          TEXT,
                    team_a              INTEGER REFERENCES teams(team_id),
                    team_b              INTEGER REFERENCES teams(team_id),
                    patch               INTEGER REFERENCES patches(patch_id),
                    best_of             INTEGER,
                    veto_order_a_first  INTEGER,
                    team_a_ban_1        INTEGER REFERENCES maps(map_id),
                    team_b_ban_1        INTEGER REFERENCES maps(map_id),
                    team_a_pick_1       INTEGER REFERENCES maps(map_id),
                    team_b_pick_1       INTEGER REFERENCES maps(map_id),
                    team_a_ban_2        INTEGER REFERENCES maps(map_id),
                    team_b_ban_2        INTEGER REFERENCES maps(map_id),
                    decider             INTEGER REFERENCES maps(map_id),
                    team_a_pick_2       INTEGER REFERENCES maps(map_id),
                    team_b_pick_2       INTEGER REFERENCES maps(map_id)
                );
                ''')
    # Games
    curs.execute('''
                CREATE TABLE games (
                    game_id             INTEGER PRIMARY KEY,
                    match_id            INTEGER REFERENCES matches(match_id),
                    map_id              INTEGER REFERENCES maps(map_id),
                    team_a_score        INTEGER,
                    team_a_att          INTEGER,
                    team_a_def          INTEGER,
                    team_a_ot           INTEGER,
                    team_b_score        INTEGER,
                    team_b_att          INTEGER,
                    team_b_def          INTEGER,
                    team_b_ot           INTEGER,
                    a_1_player          INTEGER REFERENCES players(player_id),
                    a_2_player          INTEGER REFERENCES players(player_id),
                    a_3_player          INTEGER REFERENCES players(player_id),
                    a_4_player          INTEGER REFERENCES players(player_id),
                    a_5_player          INTEGER REFERENCES players(player_id),
                    b_1_player          INTEGER REFERENCES players(player_id),
                    b_2_player          INTEGER REFERENCES players(player_id),
                    b_3_player          INTEGER REFERENCES players(player_id),
                    b_4_player          INTEGER REFERENCES players(player_id),
                    b_5_player          INTEGER REFERENCES players(player_id)
                );
                ''')
    # Player History
    curs.execute('''
                 CREATE TABLE player_game_history (
                    player_id       INTEGER REFERENCES players(player_id),
                    game_id         INTEGER REFERENCES games(game_id),
                    agent_id        INTEGER REFERENCES agents(agent_id),
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
                    vlr_rating_def  REAL,
                    acs_tot         INTEGER,
                    acs_att         INTEGER,
                    acs_def         INTEGER,
                    PRIMARY KEY (player_id, game_id)
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
    sql_query = 'INSERT INTO maps (name) VALUES (?);'
    curs.executemany(sql_query, maps)
    curs.connection.commit()

    print("maps table populated.")
    return None

def populate_agents(curs:sqlite3.Cursor) -> None:
    agents = [
        ('Astra','Controller'),
        ('Breach','Initiator'),
        ('Brimstone','Controller'),
        ('Chamber','Sentinel'),
        ('Clove','Controller'),
        ('Cypher','Sentinel'),
        ('Deadlock','Sentinel'),
        ('Fade','Initiator'),
        ('Gekko','Initiator'),
        ('Harbor','Controller'),
        ('Iso','Duelist'),
        ('Jett','Duelist'),
        ('Kayo','Initiator'),
        ('Killjoy','Sentinel'),
        ('Miks','Controller'),
        ('Neon','Duelist'),
        ('Omen','Controller'),
        ('Pheonix','Duelist'),
        ('Raze','Duelist'),
        ('Reyna','Duelist'),
        ('Sage','Sentinel'),
        ('Skye','Initiator'),
        ('Sova','Initiator'),
        ('Tejo','Initiator'),
        ('Veto','Sentinel'),
        ('Viper','Controller'),
        ('Vyse','Sentinel'),
        ('Waylay','Duelist'),
        ('Yoru','Duelist')
    ]
    sql_query = 'INSERT INTO agents (name, class) VALUES (?, ?);'
    curs.executemany(sql_query, agents)
    curs.connection.commit()

    print('Agents table populated.')
    return None

def populate_patches(curs:sqlite3.Cursor) -> None:
    patches = [
        ('0.47','2020-04-21'),
        ('0.49','2020-04-28'),
        ('0.50','2020-05-12'),
        ('1.0','2020-06-02'),
        ('1.01','2020-06-09'),
        ('1.02','2020-06-23'),
        ('1.03','2020-07-07'),
        ('1.04','2020-07-21'),
        ('1.05','2020-08-04'),
        ('1.06','2020-08-20'),
        ('1.07','2020-09-01'),
        ('1.08','2020-09-15'),
        ('1.09','2020-09-29'),
        ('1.10','2020-10-13'),
        ('1.11','2020-10-27'),
        ('1.12','2020-11-10'),
        ('1.14','2020-12-08'),
        ('2.0','2021-1-12'),
        ('2.01','2021-01-20'),
        ('2.02','2021-02-02'),
        ('2.03','2021-02-17'),
        ('2.04','2021-03-02'),
        ('2.05','2021-03-16'),
        ('2.06','2021-03-30'),
        ('2.07','2021-04-13'),
        ('2.08','2021-04-27'),
        ('2.09','2021-05-11'),
        ('2.11','2021-06-08'),
        ('3.0','2021-06-22'),
        ('3.01','2021-07-07'),
        ('3.02','2021-07-20'),
        ('3.03','2021-08-10'),
        ('3.04','2021-08-24'),
        ('3.05','2021-08-09'),
        ('3.06','2021-09-21'),
        ('3.07','2021-10-05'),
        ('3.08','2021-10-19'),
        ('3.09','2021-11-02'),
        ('3.10','2021-11-16'),
        ('3.12','2021-12-07'),
        ('4.0','2022-01-11'),
        ('4.01','2022-01-19'),
        ('4.02','2022-02-01'),
        ('4.03','2022-02-15'),
        ('4.04','2022-03-01'),
        ('4.05','2022-03-22'),
        ('4.07','2022-04-12'),
        ('4.08','2022-04-27'),
        ('4.09','2022-05-10'),
        ('4.10','2022-05-24'),
        ('4.11','2022-06-07'),
        ('5.0','2022-06-16'),
        ('5.01','2022-07-12'),
        ('5.03','2022-08-09'),
        ('5.04','2022-08-23'),
        ('5.05','2022-09-07'),
        ('5.06','2022-09-20'),
        ('5.07','2022-10-04'),
        ('5.08','2022-10-18'),
        ('5.09','2022-11-01'),
        ('5.10','2022-11-15'),
        ('5.12','2022-12-06'),
        ('6.0','2023-01-10'),
        ('6.01','2023-01-18'),
        ('6.02','2023-02-07'),
        ('6.03','2023-02-14'),
        ('6.04','2023-03-07'),
        ('6.05','2023-03-14'),
        ('6.06','2023-03-28'),
        ('6.07','2023-04-11'),
        ('6.08','2023-04-25'),
        ('6.10','2023-05-23'),
        ('6.11','2023-06-06'),
        ('7.0','2023-06-27'),
        ('7.01','2023-07-11'),
        ('7.02','2023-08-01'),
        ('7.03','2023-08-08'),
        ('7.04','2023-08-29'),
        ('7.05','2023-09-06'),
        ('7.06','2023-09-19'),
        ('7.07','2023-10-03'),
        ('7.08','2023-10-17'),
        ('7.09','2023-10-31'),
        ('7.10','2023-11-14'),
        ('7.12','2023-12-05'),
        ('8.0','2024-01-09'),
        ('8.01','2024-01-23'),
        ('8.02','2024-02-06'),
        ('8.03','2024-02-21'),
        ('8.04','2024-03-05'),
        ('8.05','2024-03-26'),
        ('8.07','2024-04-16'),
        ('8.08','2024-04-30'),
        ('8.09','2024-05-14'),
        ('8.10','2024-05-29'),
        ('8.11','2024-06-11'),
        ('9.0','2024-06-25'),
        ('9.01','2024-07-16'),
        ('9.02','2024-07-30'),
        ('9.03','2024-08-13'),
        ('9.04','2024-08-27'),
        ('9.05','2024-09-10'),
        ('9.06','2024-09-24'),
        ('9.07','2024-10-08'),
        ('9.08','2024-10-22'),
        ('9.09','2024-11-05'),
        ('9.10','2024-11-19'),
        ('9.11','2024-12-10'),
        ('10.00','2025-01-07'),
        ('10.01','2025-01-21'),
        ('10.02','2025-02-04'),
        ('10.03','2025-02-18'),
        ('10.04','2025-03-04'),
        ('10.05','2025-03-18'),
        ('10.06','2025-04-01'),
        ('10.07','2025-04-15'),
        ('10.08','2025-04-29'),
        ('10.09','2025-05-13'),
        ('10.10','2025-05-27'),
        ('10.11','2025-06-10'),
        ('11.00','2025-06-24'),
        ('11.01','2025-07-14'),
        ('11.02','2025-07-29'),
        ('11.04','2025-08-19'),
        ('11.05','2025-09-02'),
        ('11.06','2025-09-16'),
        ('11.07','2025-09-30'),
        ('11.07b','2025-10-07'),
        ('11.08','2025-10-14'),
        ('11.09','2025-10-28'),
        ('11.10','2025-11-11'),
        ('11.11','2025-12-02'),
        ('12.00','2026-01-06'),
        ('12.01','2026-01-20'),
        ('12.02','2026-02-03'),
        ('12.03','2026-02-17'),
        ('12.04','2026-03-03'),
        ('12.05','2026-03-17'),
        ('12.06','2025-03-31'),
        ('12.07','2026-04-14'),
        ('12.08','2026-04-28'),
        ('12.09','2026-05-12')
    ]
    sql_query = 'INSERT INTO patches (patch_number, release_date) VALUES (?,?);'
    curs.executemany(sql_query, patches)
    curs.connection.commit()
    
    print('Patches Table populated')
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

    # Populate tournaments, teams, and players from kaggle data
    populate_kaggle_data(curs)

    # Populate maps, agents, and patches with hard coded data
    populate_maps(curs)
    populate_agents(curs)
    populate_patches(curs)

    # Close database connection
    conn.close()

if __name__ == '__main__':
    init_db()