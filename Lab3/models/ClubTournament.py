from sqlalchemy import Column, ForeignKey, Integer, Table

from models.Base import Base

clubs_tournaments = Table('clubs_tournaments', Base.metadata,
                          Column('club_id', Integer, ForeignKey('clubs.club_id', onupdate='cascade', ondelete='cascade'),
                                 primary_key=True),
                          Column('tournament_id', Integer, ForeignKey('tournaments.tournament_id', onupdate='cascade', ondelete='cascade'),
                                 primary_key=True))
