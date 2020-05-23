from sqlalchemy import Column, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import INTEGER, VARCHAR

from look.model.base import Base

category_board = Table('category_board', Base.metadata,
    Column('category_id', INTEGER(unsigned=True), ForeignKey('category.id')),
    Column('board_id', INTEGER(unsigned=True), ForeignKey('board.id')),
)

class Category(Base):
    __tablename__ = 'category'

    id = Column(INTEGER(unsigned=True), primary_key=True)
    title = Column(VARCHAR(64), nullable=False)
    subtitle = Column(VARCHAR(128), nullable=False)

    board = relationship('Board', secondary=category_board)