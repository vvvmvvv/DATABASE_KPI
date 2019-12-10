from sqlalchemy import Column, Integer, String, Sequence, Date, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import Session

from models.Base import Base


class Player(Base):
    __tablename__ = 'players'
    id = Column('player_id', Integer, Sequence('player_id_seq'), primary_key=True)
    first_name = Column(String(80), nullable=False)
    last_name = Column(String(80), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    height = Column(Integer, nullable=False)
    is_injured = Column(Boolean, nullable=False)
    __table_args__ = (
        Index(
            'height_index',
            height,
            postgresql_using='btree'
        ),
        Index(
            'date_of_birth_index',
            date_of_birth,
            postgresql_using='brin'
        ),
    )

    position_id = Column(Integer, ForeignKey('positions.position_id'))
    club_id = Column(Integer, ForeignKey('clubs.club_id', ondelete='set null'))

    club = relationship("Club", back_populates="players")
    position = relationship("Position")

    def add(self, session: Session) -> None:
        session.add(self)

    def update(self, session: Session) -> None:
        session.query(Player).filter(Player.id == self.id).update({
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'date_of_birth': self.date_of_birth,
            'height': self.height,
            'is_injured': self.is_injured,
            'position_id': self.position_id,
            'club_id': self.club_id
        })

    @staticmethod
    def delete(session: Session, player_id: int) -> None:
        session.query(Player).filter(Player.id == player_id).delete()

    @staticmethod
    def get(session: Session, player_id: int):
        return session.query(Player).filter(Player.id == player_id).first()

    @staticmethod
    def getAll(session: Session) -> list:
        return session.query(Player).all()

    @staticmethod
    def getFree(session: Session) -> list:
        return session.query(Player).filter(Player.club_id == None).all()

    def __repr__(self):
        return "<Player(id='%s', first_name='%s', last_name='%s'>" %\
               (self.id, self.first_name, self.last_name)
