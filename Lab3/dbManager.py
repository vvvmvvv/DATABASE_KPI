import math
import os
from random import random

import sqlalchemy
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from config.config import get_url_connection
from config.session_scope import session_scope
from models.Club import Club
from models.Player import Player
from models.Position import Position
from models.Tournament import Tournament
from models.Base import Base
from models.ClubTournament import clubs_tournaments
from models.ClubAudit import clubs_audit
from faker import Faker


class FootballDatabase(object):
    def __init__(self):
        url = get_url_connection()
        self.engine = create_engine(url)
        Base.metadata.drop_all(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
        self.sessionMaker = sessionmaker()

    def get_session(self) -> Session:
        return self.sessionMaker()

    def connect(self):
        try:
            self.sessionMaker.configure(bind=self.engine)
        except Exception as error:
            print(error)

    def close_connection(self) -> None:
        if self.sessionMaker is not None:
            self.sessionMaker.close_all()
            print('Database connection closed.')

    def execute_script(self, script_file_name: str) -> None:
        script_file = open(os.path.join(os.path.dirname(__file__), 'scripts', script_file_name), 'r', encoding="utf8")
        with self.engine.connect() as con:
            con.execute(sqlalchemy.text(script_file.read()))

    # region Random data generating
    def generate_positions(self) -> None:
        with session_scope(self.get_session) as session:
            Position(name='Goalkeeper').add(session)
            Position(name='Defender').add(session)
            Position(name='Midfielder').add(session)
            Position(name='Forward').add(session)

    def generate_random_players(self, players_count: int) -> None:
        fake = Faker()
        with session_scope(self.get_session) as session:
            for i in range(players_count):
                Player(first_name=fake.first_name_male(), last_name=fake.last_name_male(),
                       date_of_birth=fake.date_of_birth(tzinfo=None, minimum_age=17, maximum_age=35),
                       is_injured=random() > 0.5, height=math.ceil(random() * 39 + 160),
                       position_id=math.ceil(random() * 3 + 1), club_id=session.query(Club.id).order_by(func.random())
                       .first()).add(session)

    def generate_random_clubs(self, clubs_count: int) -> None:
        fake = Faker()
        club_names = fake.words(nb=clubs_count, ext_word_list=None, unique=True)
        with session_scope(self.get_session) as session:
            for i in range(clubs_count):
                Club(name=club_names[i],
                     creation_date=fake.date_of_birth(tzinfo=None, minimum_age=5, maximum_age=200),
                     number_of_trophies=math.ceil(random() * 29 + 1)).add(session)

    def generate_random_tournaments(self, tournaments_count: int) -> None:
        fake = Faker()
        with session_scope(self.get_session) as session:
            for i in range(tournaments_count):
                Tournament(name=fake.word(), description=fake.text()).add(session)

    # endregion

    # region Text Search
    def text_search_by_words(self, words: list) -> list:
        search_words = ' & '.join(words)
        with session_scope(self.get_session) as session:
            results = session.query(Tournament) \
                .filter(Tournament.tsv.match(search_words, postgresql_regconfig='english')).all()
            return [Tournament(id=t.id,
                               name=t.name,
                               description=session.query(
                                   func.ts_headline('english', t.description,
                                                    func.to_tsquery(search_words, postgresql_regconfig='english')))
                               .first())
                    for t in results]

    def text_search_by_phrase(self, phrase: str) -> list:
        with session_scope(self.get_session) as session:
            query_func = func.phraseto_tsquery(phrase, postgresql_regconfig='english')
            results = session.query(Tournament) \
                .filter(Tournament.tsv.op('@@')(query_func)).all()
            return [Tournament(id=t.id,
                               name=t.name,
                               description=session.query(func.ts_headline('english', t.description, query_func))
                               .first())
                    for t in results]
    # endregion

    def advanced_player_search(self, min_height: int, max_height: int,
                               min_number: int, max_number: int, position_id: int) -> list:
        with session_scope(self.get_session) as session:
            results = session.query(Player, Club, Position).filter(Player.height.between(min_height, max_height)) \
                .join(Club, Club.id == Player.club_id).filter(Club.number_of_trophies.between(min_number, max_number)) \
                .join(Position, Player.position_id == Position.id).filter(Position.id == position_id).all()
            session.expunge_all()
            return results

    # region Positions operations
    def get_positions(self):
        return Position.getAll(self.get_session())

    # endregion

    # region Players operations
    def get_player(self, player_id: int) -> Player:
        return Player.get(self.get_session(), player_id)

    def get_players(self) -> list:
        return Player.getAll(self.get_session())

    def get_players_free(self):
        return Player.getFree(self.get_session())

    def upsert_player(self, player_id: int, player: Player) -> None:
        with session_scope(self.get_session) as session:
            if player_id:
                player.id = player_id
                player.update(session)
            else:
                player.add(session)

    def delete_player(self, player_id: int) -> None:
        with session_scope(self.get_session) as session:
            Player.delete(session, player_id)

    # endregion

    # region Club operations
    def get_club(self, club_id: int) -> Club:
        return Club.get(self.get_session(), club_id)

    def get_clubs(self) -> list:
        return Club.getAll(self.get_session())

    def upsert_club(self, club_id: int, club: Club, free_players: list):
        with session_scope(self.get_session) as session:
            if club_id:
                club.id = club_id
                club.update(session)
            else:
                club.add(session)
                session.refresh(club)
                club_id = club.id
            for player_id in free_players:
                player = Player.get(session, player_id)
                player.club_id = club_id

    def delete_club(self, club_id: int) -> None:
        with session_scope(self.get_session) as session:
            Club.delete(session, club_id)

    # endregion

    # region Tournament operations
    def get_tournament(self, tournament_id: int) -> Tournament:
        return Tournament.get(self.get_session(), tournament_id)

    def get_tournaments(self) -> list:
        return Tournament.getAll(self.get_session())

    def delete_tournament(self, tournament_id: int) -> None:
        with session_scope(self.get_session) as session:
            Tournament.delete(session, tournament_id)

    def upsert_tournament(self, tournament_id: int, tournament: Tournament, clubs: list):
        with session_scope(self.get_session) as session:
            if tournament_id:
                tournament.id = tournament_id
                tournament.update(session)
            else:
                tournament.add(session)
            for club_id in clubs:
                statement = clubs_tournaments.insert().values(club_id=club_id, tournament_id=tournament.id)
                session.execute(statement)
    # endregion
