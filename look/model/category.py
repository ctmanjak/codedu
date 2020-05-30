from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import INTEGER, VARCHAR

from . import Base

class Category(Base):
    __tablename__ = 'category'

    id = Column(INTEGER(unsigned=True), primary_key=True)
    title = Column(VARCHAR(64), nullable=False)
    subtitle = Column(VARCHAR(128), nullable=False)

    boards = relationship('Board', backref="categories", secondary="category_board", cascade="all, delete")

class CategoryBoard(Base):
    __tablename__ = 'category_board'

    category_id = Column(INTEGER(unsigned=True), ForeignKey("category.id"), primary_key=True)
    board_id = Column(INTEGER(unsigned=True), ForeignKey("board.id"), primary_key=True)