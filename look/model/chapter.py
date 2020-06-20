from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.mysql import INTEGER, VARCHAR

from . import Base
from .util import default_subtitle

class Chapter(Base):
    __tablename__ = 'chapter'

    id = Column(INTEGER(unsigned=True), primary_key=True)
    title = Column(VARCHAR(64), nullable=False)
    subtitle = Column(VARCHAR(128), default=default_subtitle)

    board_id = Column(INTEGER(unsigned=True), ForeignKey("board.id", ondelete='SET NULL'))
    board = relationship('Board', backref='chapters')