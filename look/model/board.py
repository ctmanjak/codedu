from sqlalchemy import Column
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import INTEGER, VARCHAR

from look.model.base import Base
from look.model.category import Category

class Board(Base):
    __tablename__ = 'board'

    id = Column(INTEGER(unsigned=True), primary_key=True)
    title = Column(VARCHAR(32), nullable=False)
    subtitle = Column(VARCHAR(64), nullable=False)

    chapter = relationship('Chapter', cascade="all, delete, delete-orphan")