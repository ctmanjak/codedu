from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.mysql import INTEGER, VARCHAR

from look.model.base import Base
from look.model.chapter import Chapter

class Subchapter(Base):
    __tablename__ = 'subchapter'

    id = Column(INTEGER(unsigned=True), primary_key=True)
    parent_chapter_id = Column(INTEGER(unsigned=True), ForeignKey('chapter.id'), nullable=False)
    title = Column(VARCHAR(32), nullable=False)