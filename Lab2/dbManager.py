import math
import os
from random import random

import psycopg2
import psycopg2.extras

from config.config import config
from models.Club import Club
from models.Player import Player
from models.Position import Position
from models.Tournament import Tournament
from faker import Faker


class FootballDatabase(object):
    def __init__(self):
        self.conn = None

    def exec_script_file(self, script_file_name: str) -> None:
        script_file = open(os.path.join(os.path.dirname(__file__), 'scripts', script_file_name), 'r')
        with self.get_cursor() as cur:
            cur.execute(script_file.read())
            self.conn.commit()

    def get_cursor(self):
        return self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    def connect(self) -> None:
        try:
            # read connection parameters
            params = config()

            # connect to the PostgreSQL server
            self.conn = psycopg2.connect(**params)
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

    def close_connection(self) -> None:
        if self.conn is not None:
            self.conn.close()
            print('Database connection closed.')

    def generate_random_players(self):
        fake = Faker()
        script = """INSERT INTO players(first_name, last_name, date_of_birth, is_injured, height, position_id, club_id)
                    VALUES(%s, %s, %s, %s, %s, %s, (SELECT club_id FROM clubs ORDER BY random() LIMIT 1));"""
        with self.get_cursor() as cur:
            for i in range(1000):
                cur.execute(script, [fake.first_name_male(),
                                     fake.last_name_male(),
                                     fake.date_of_birth(tzinfo=None, minimum_age=17, maximum_age=35),
                                     random() > 0.5,
                                     math.ceil(random() * 39 + 160),
                                     math.ceil(random() * 3 + 1)])

    def generate_random_clubs(self):
        fake = Faker()
        clubs_amount = 100
        club_names = fake.words(nb=clubs_amount, ext_word_list=None, unique=True)
        script = """INSERT INTO clubs(name, creation_date, number_of_trophies) VALUES (%s, %s, %s);"""
        with self.get_cursor() as cur:
            for i in range(clubs_amount):
                cur.execute(script, [club_names[i],
                                     fake.date_of_birth(tzinfo=None, minimum_age=5, maximum_age=200),
                                     math.ceil(random() * 29 + 1)])

    def generate_random_tournaments(self):
        fake = Faker()
        script = """INSERT INTO tournaments(name, description) VALUES (%s, %s);"""
        with self.get_cursor() as cur:
            for i in range(20):
                cur.execute(script, [fake.word(), fake.text()])

    def text_search_by_words(self, words: list) -> list:
        search_words = ' & '.join(words)
        script = """SELECT id, ts_headline('english', description, q) description, name
                    FROM (SELECT tournament_id id, description, name, q
                          FROM tournaments, to_tsquery('english', %s) q
                          WHERE tsv @@ q) AS t;"""
        with self.get_cursor() as cur:
            cur.execute(script, [search_words])
            tournaments = cur.fetchall()
        return [Tournament(id=t['id'], name=t['name'], description=t['description']) for t in tournaments]

    def text_search_by_phrase(self, phrase: str) -> list:
        script = """SELECT id, ts_headline('english', description, q) description, name
                            FROM (SELECT tournament_id id, description, name, q
                                  FROM tournaments, phraseto_tsquery('english', %s) q
                                  WHERE tsv @@ q) AS t;"""
        with self.get_cursor() as cur:
            cur.execute(script, [phrase])
            tournaments = cur.fetchall()
        return [Tournament(id=t['id'], name=t['name'], description=t['description']) for t in tournaments]

    def advanced_player_search(self,
                               min_height: int,
                               max_height: int,
                               min_number: int,
                               max_number: int,
                               position_id: int) -> list:
        script = """
            SELECT p.first_name, p.last_name, p.height, c.name as club , c.number_of_trophies, pos.name as position 
            FROM players p 
            JOIN clubs c
            ON p.club_id = c.club_id
            JOIN positions pos
            ON p.position_id = pos.position_id
            WHERE (p.height BETWEEN %s AND %s) 
                AND (c.number_of_trophies BETWEEN %s AND %s)
                AND p.position_id = %s;"""
        with self.get_cursor() as cur:
            try:
                cur.execute(script, [min_height, max_height, min_number, max_number, position_id])
            except Exception as e:
                print(e)
                return []
            rows = cur.fetchall()
        res = [(Club(name=r['club'], number_of_trophies=r['number_of_trophies']),
                 Player(first_name=r['first_name'], last_name=r['last_name'], height=r['height']),
                 Position(name=r['position'])) for r in rows]
        res.reverse()
        return res

    #  Positions operations
    def get_positions(self):
        script = """
            SELECT position_id, name 
            FROM positions"""
        with self.get_cursor() as cur:
            cur.execute(script)
            positions = cur.fetchall()
        return [Position(id=p['position_id'], name=p['name']) for p in positions]


    # Players operations
    def get_player(self, player_id: int) -> Player:
        script = """
            SELECT * FROM players
            WHERE player_id = %s"""
        with self.get_cursor() as cur:
            cur.execute(script, [player_id])
            db_player = cur.fetchone()
        return Player(id=db_player['player_id'], first_name=db_player['first_name'], last_name=db_player['last_name'],
                      date_of_birth=db_player['date_of_birth'], is_injured=db_player['is_injured'],
                      height=db_player['height'], club_id=db_player['club_id'], position_id=db_player['position_id'])

    def get_players(self) -> list:
        with self.get_cursor() as cur:
            cur.execute('SELECT player_id, first_name, last_name FROM players')
            db_players = cur.fetchall()
        res = [Player(id=p['player_id'], first_name=p['first_name'], last_name=p['last_name']) for p in db_players]
        res.reverse()
        return res

    def get_players_by_club(self, club_id) -> list:
        script = """
                    SELECT p.first_name, p.last_name
                    FROM players AS p
                    WHERE p.club_id = %s"""
        with self.get_cursor() as cur:
            cur.execute(script, [club_id])
            db_players = cur.fetchall()
        res = [Player(first_name=p['first_name'], last_name=p['last_name']) for p in db_players]
        res.reverse()
        return res

    def get_players_free(self):
        script = """
            SELECT p.player_id, p.first_name, p.last_name 
            FROM players p
            WHERE club_id is NULL"""
        with self.get_cursor() as cur:
            cur.execute(script)
            db_players = cur.fetchall()
        res = [Player(first_name=p['first_name'], last_name=p['last_name'], id=p['player_id']) for p in db_players]
        res.reverse()
        return res

    def add_player(self, player: Player) -> None:
        insert_script = """
            INSERT INTO players (first_name, last_name, date_of_birth, is_injured, position_id, height, club_id) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        insert_data = (player.first_name,
                       player.last_name,
                       player.date_of_birth,
                       player.is_injured,
                       player.position_id,
                       player.height,
                       player.club_id)
        with self.get_cursor() as cur:
            cur.execute(insert_script, insert_data)
            self.conn.commit()

    def update_player(self, player: Player) -> None:
        update_script = """
                    UPDATE players
                    SET (first_name, last_name, date_of_birth, is_injured, position_id, height ,club_id) = 
                        (%s, %s, %s, %s, %s, %s, %s) 
                    WHERE player_id = %s;"""
        update_data = (player.first_name, player.last_name,
                       player.date_of_birth, player.is_injured,
                       player.position_id, player.height, player.club_id, player.id)
        with self.get_cursor() as cur:
            cur.execute(update_script, update_data)
            self.conn.commit()

    def update_players_club(self, club_id: int, player_ids: list):
        update_player = """
                    UPDATE players
                    SET club_id = %s
                    WHERE player_id IN %s"""
        if player_ids:
            with self.get_cursor() as cur:
                cur.execute(update_player, (club_id, tuple(player_ids),))
                self.conn.commit()

    def delete_player(self, player_id: int) -> None:
        delete_script = """DELETE FROM players WHERE player_id=%s;"""
        with self.get_cursor()as cur:
            cur.execute(delete_script, [player_id])
            self.conn.commit()

    #  Club operations
    def get_club(self, club_id: int) -> Club:
        with self.get_cursor() as cur:
            cur.execute('SELECT * FROM clubs WHERE club_id = {0}'.format(club_id))
            c = cur.fetchone()
        return Club(id=c['club_id'],
                    name=c['name'],
                    creation_date=c['creation_date'],
                    number_of_trophies=c['number_of_trophies'])

    def get_clubs(self) -> list:
        with self.get_cursor() as cur:
            cur.execute('SELECT club_id as id, name FROM clubs')
            db_clubs = cur.fetchall()
        res = [Club(id=c['id'], name=c['name']) for c in db_clubs]
        res.reverse()
        return res

    def add_club(self, club: Club) -> int:
        insert_script = """
                    INSERT INTO clubs (name, creation_date, number_of_trophies) 
                    VALUES (%s, %s, %s) RETURNING club_id;"""
        insert_data = (club.name, club.creation_date, club.number_of_trophies)
        with self.get_cursor() as cur:
            cur.execute(insert_script, insert_data)
            new_id = cur.fetchone()[0]
            self.conn.commit()
        return new_id

    def update_club(self, club: Club) -> None:
        update_script = """
                    UPDATE clubs
                    SET (name, creation_date, number_of_trophies) = (%s, %s, %s) 
                    WHERE club_id = %s;"""
        update_data = (club.name, club.creation_date, club.number_of_trophies, club.id)
        with self.get_cursor() as cur:
            cur.execute(update_script, update_data)
            self.conn.commit()

    def delete_club(self, club_id: int) -> None:
        delete_script = """DELETE FROM clubs WHERE club_id=%s;"""
        with self.get_cursor() as cur:
            cur.execute(delete_script, [club_id])
            self.conn.commit()

    def get_clubs_by_tournament(self, tournament_id: int):
        script = """
            SELECT c.club_id as id, c.name as name FROM clubs c 
            JOIN clubs_tournaments ct
            ON ct.club_id = c.club_id
            WHERE ct.tournament_id = %s"""
        with self.get_cursor() as cur:
            cur.execute(script, [tournament_id])
            clubs = cur.fetchall()
            self.conn.commit()
        res = [Club(id=c['id'], name=c['name']) for c in clubs]
        res.reverse()
        return res

    def get_clubs_not_in_tournament(self, tournament_id: int):
        script = """
            SELECT c.club_id as id, c.name as name FROM clubs c
            WHERE c.club_id NOT IN(
                SELECT c.club_id FROM clubs c 
                JOIN clubs_tournaments ct
                ON ct.club_id = c.club_id
                WHERE ct.tournament_id = %s)"""
        with self.get_cursor() as cur:
            cur.execute(script, [tournament_id])
            clubs = cur.fetchall()
        res =  [Club(id=c['id'], name=c['name']) for c in clubs]
        res.reverse()
        return res

    def add_clubs_to_tournament(self, tournament_id: int, club_ids: list):
        data = [(cid, tournament_id) for cid in club_ids]
        script = """INSERT INTO clubs_tournaments(club_id, tournament_id) VALUES %s"""
        with self.get_cursor() as cur:
            psycopg2.extras.execute_values(cur, script, data, template=None, page_size=100)
            self.conn.commit()

    # Tournament operations
    def get_tournament(self, tournament_id: int) -> Tournament:
        with self.get_cursor() as cur:
            cur.execute('SELECT * FROM tournaments WHERE tournament_id = {0}'.format(tournament_id))
            t = cur.fetchone()
        return Tournament(id=t['tournament_id'], name=t['name'], description=t['description'])

    def get_tournaments(self) -> list:
        with self.get_cursor() as cur:
            cur.execute('SELECT tournament_id as id, name FROM tournaments')
            db_tournaments = cur.fetchall()
        res = [Tournament(id=t['id'], name=t['name']) for t in db_tournaments]
        res.reverse()
        return res

    def delete_tournament(self, tournament_id: int) -> None:
        delete_script = """DELETE FROM tournaments WHERE tournament_id=%s;"""
        with self.get_cursor() as cur:
            cur.execute(delete_script, [tournament_id])
            self.conn.commit()

    def add_tournament(self, tournament: Tournament) -> int:
        insert_script = """
                    INSERT INTO tournaments (name, description) 
                    VALUES (%s, %s) RETURNING tournament_id"""
        insert_data = (tournament.name, tournament.description)
        with self.get_cursor() as cur:
            cur.execute(insert_script, insert_data)
            new_id = cur.fetchone()[0]
            self.conn.commit()
        return new_id

    def update_tournament(self, tournament: Tournament) -> None:
        update_script = """
                    UPDATE tournaments
                    SET (name, description) = (%s, %s) 
                    WHERE tournament_id = %s;"""
        update_data = (tournament.name, tournament.description, tournament.id)
        with self.get_cursor() as cur:
            cur.execute(update_script, update_data)
            self.conn.commit()

    def get_tournaments_by_club(self, club_id: int):
        script = """
            SELECT t.tournament_id as id, t.name as name FROM tournaments t
            JOIN clubs_tournaments ct
            ON t.tournament_id = ct.tournament_id
            WHERE ct.club_id = %s"""
        with self.get_cursor() as cur:
            cur.execute(script, [club_id])
            tournaments = cur.fetchall()
        res = [Tournament(id=t['id'], name=t['name']) for t in tournaments]
        res.reverse()
        return res
