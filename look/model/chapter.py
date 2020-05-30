from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.mysql import INTEGER, VARCHAR

from . import Base

class Chapter(Base):
    __tablename__ = 'chapter'

    id = Column(INTEGER(unsigned=True), primary_key=True)
    title = Column(VARCHAR(32), nullable=False)

    board_id = Column(INTEGER(unsigned=True), ForeignKey("board.id"))
    board = relationship('Board', backref=backref('chapters', order_by=id, cascade="all, delete"), cascade="all, delete")