from sqlalchemy import Column, Integer, String, Sequence, Text, Index, event, DDL
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import Session

from models.Base import Base
from models.ClubTournament import clubs_tournaments


class Tournament(Base):
    __tablename__ = 'tournaments'
    id = Column('tournament_id', Integer, Sequence('tournament_id_seq'), primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(Text, nullable=False)
    tsv = Column(TSVECTOR, nullable=False)
    __table_args__ = (Index('text_search_idx', tsv, postgresql_using="gin"),)

    clubs = relationship('Club', secondary=clubs_tournaments, back_populates='tournaments')

    def add(self, session: Session) -> None:
        session.add(self)

    @staticmethod
    def delete(session: Session, tournament_id: int) -> None:
        session.query(Tournament).filter(Tournament.id == tournament_id).delete()

    def update(self, session: Session) -> None:
        session.query(Tournament).filter(Tournament.id == self.id).update({
            'id': self.id,
            'name': self.name,
            'description': self.description
        })

    @staticmethod
    def get(session: Session, tournament_id: int):
        return session.query(Tournament).filter(Tournament.id == tournament_id).first()

    @staticmethod
    def getAll(session: Session) -> list:
        return session.query(Tournament).all()

    def __repr__(self):
        return "<Tournament(id='%s', name='%s', description='%s')>" % (self.id, self.name, self.description)


event.listen(Tournament.__table__, 'after_create', DDL("""
            CREATE TRIGGER tsvectorupdate BEFORE INSERT OR UPDATE
            ON tournaments
            FOR EACH ROW EXECUTE PROCEDURE
            tsvector_update_trigger(tsv, 'pg_catalog.english', description);
       """))

