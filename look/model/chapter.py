from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import INTEGER, VARCHAR

from look.model.base import Base

class Chapter(Base):
    __tablename__ = 'chapter'

    id = Column(INTEGER(unsigned=True), primary_key=True)
    parent_board_id = Column(INTEGER(unsigned=True), ForeignKey('board.id'), nullable=False)
    title = Column(VARCHAR(32), nullable=False)

    subchapter = relationship('Subchapter')