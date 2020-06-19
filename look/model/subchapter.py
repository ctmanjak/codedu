from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.mysql import INTEGER, VARCHAR

from . import Base

class Subchapter(Base):
    __tablename__ = 'subchapter'

    id = Column(INTEGER(unsigned=True), primary_key=True)
    title = Column(VARCHAR(32), nullable=False)
    content_path = Column(VARCHAR(64))

    chapter_id = Column(INTEGER(unsigned=True), ForeignKey("chapter.id"))
    chapter = relationship('Chapter', backref=backref('subchapters', order_by=id, cascade="all, delete"), cascade="all, delete")