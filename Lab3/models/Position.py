from sqlalchemy import Column, Integer, String, Sequence
from sqlalchemy.orm.session import Session
from models.Base import Base


class Position(Base):
    __tablename__ = 'positions'
    id = Column('position_id', Integer, Sequence('position_id_seq'), primary_key=True)
    name = Column(String(80), nullable=False)

    def add(self, session: Session):
        session.add(self)

    @staticmethod
    def getAll(session: Session):
        return session.query(Position)

    def __repr__(self):
        return "<Position(id='%s', name='%s')>" % (self.id, self.name)
