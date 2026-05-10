import sqlite3
from os.path import exists

if exists('vct_data.db'):
    raise RuntimeError('Tried to initialise database which already exists.')

# Create db connection and cursor object
conn = sqlite3.connect('vct_data.db')
curs = conn.cursor()

# Enable FOREIGN KEYS constraints
curs.execute('PRAGMA foreign_keys = 1;')

# Tournaments
curs.execute('CREATE TABLE tournaments (id INTEGER PRIMARY KEY, name TEXT, year INTEGER);')

# Players
curs.execute('CREATE TABLE players (id INTEGER PRIMARY KEY, name TEXT);')

# Teams
curs.execute('''
             CREATE TABLE teams (
                id INTEGER PRIMARY KEY, 
                name TEXT, 
                short_name TEXT
             );
             ''')

# Matches
curs.execute('''
             CREATE TABLE matches (
                id INTEGER PRIMARY KEY, 
                team_a INTEGER REFERENCES teams(id), 
                team_b INTEGER REFERENCES teams(id),
                date TEXT, 
                tournament INTEGER REFERENCES tournaments(id), 
                patch TEXT
             );
             ''')

# Games
curs.execute('''
             CREATE TABLE games (
                id              INTEGER PRIMARY KEY,
                match_id        INTEGER REFERENCES matches(id),
                map             TEXT,
                team_a_score    INTEGER,
                team_a_att      INTEGER,
                team_a_def      INTEGER,
                team_a_ot       INTEGER,
                team_b_score    INTEGER,
                team_b_att      INTEGER,
                team_b_def      INTEGER,
                team_b_ot       INTEGER,
                a_1_player      INTEGER REFERENCES players(id),
                a_2_player      INTEGER REFERENCES players(id),
                a_3_player      INTEGER REFERENCES players(id),
                a_4_player      INTEGER REFERENCES players(id),
                a_5_player      INTEGER REFERENCES players(id).
                b_1_player      INTEGER REFERENCES players(id),
                b_2_player      INTEGER REFERENCES players(id),
                b_3_player      INTEGER REFERENCES players(id),
                b_4_player      INTEGER REFERENCES players(id),
                b_5_player      INTEGER REFERENCES players(id),
                a_1_agent       TEXT,
                a_2_agent       TEXT,
                a_3_agent       TEXT,
                a_4_agent       TEXT,
                a_5_agent       TEXT,
                b_1_agent       TEXT,
                b_2_agent       TEXT,
                b_3_agent       TEXT,
                b_4_agent       TEXT,
                b_5_agent       TEXT
             );
             ''')