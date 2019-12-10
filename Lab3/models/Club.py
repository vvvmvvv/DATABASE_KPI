from sqlalchemy import Column, Integer, String, Sequence, Date, Index
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import Session

from models.Base import Base
from models.ClubTournament import clubs_tournaments


class Club(Base):
    __tablename__ = 'clubs'
    id = Column('club_id', Integer, Sequence('club_id_seq'), primary_key=True)
    name = Column(String(80), nullable=False, unique=True)
    creation_date = Column(Date, nullable=False)
    number_of_trophies = Column(Integer, nullable=False)
    __table_args__ = (
        Index(
            'creation_date_index',
            creation_date,
            postgresql_using='brin'
        ),

    )


    players = relationship("Player", back_populates="club")
    tournaments = relationship('Tournament', secondary=clubs_tournaments, back_populates='clubs')

    def add(self, session: Session) -> None:
        session.add(self)

    @staticmethod
    def delete(session: Session, club_id: int) -> None:
        session.query(Club).filter(Club.id == club_id).delete()

    def update(self, session: Session) -> None:
        session.query(Club).filter(Club.id == self.id).update({
            'name': self.name,
            'id': self.id,
            'creation_date': self.creation_date,
            'number_of_trophies': self.number_of_trophies
        })

    @staticmethod
    def get(session: Session, club_id: int):
        return session.query(Club).filter(Club.id == club_id).first()

    @staticmethod
    def getAll(session: Session) -> list:
        return session.query(Club).all()

    def __repr__(self):
        return "<Club(id='%s', name='%s', creation_date='%s', number_of_trophies='%s')>" % \
               (self.id, self.name, self.creation_date, self.number_of_trophies)
