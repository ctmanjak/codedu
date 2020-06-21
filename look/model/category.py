from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.mysql import INTEGER, VARCHAR

from . import Base
from .util import default_subtitle

class Category(Base):
    __tablename__ = 'category'

    id = Column(INTEGER(unsigned=True), primary_key=True)
    title = Column(VARCHAR(64), nullable=False)
    subtitle = Column(VARCHAR(128), default=default_subtitle)

    boards = relationship('Board', backref=backref("categories", order_by=id), secondary="category_board")

class CategoryBoard(Base):
    __tablename__ = 'category_board'

    category_id = Column(INTEGER(unsigned=True), ForeignKey("category.id", ondelete='CASCADE'), primary_key=True)
    board_id = Column(INTEGER(unsigned=True), ForeignKey("board.id", ondelete='CASCADE'), primary_key=True)