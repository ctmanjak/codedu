from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import INTEGER, VARCHAR

from .base import Base

class Board(Base):
    __tablename__ = 'board'

    id = Column(INTEGER(unsigned=True), primary_key=True)
    title = Column(VARCHAR(32), nullable=False)
    subtitle = Column(VARCHAR(64), nullable=False)