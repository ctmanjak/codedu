from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.mysql import INTEGER, VARCHAR, TEXT, CHAR, TINYINT

from . import Base
from .util import default_subtitle

class Subchapter(Base):
    __tablename__ = 'subchapter'

    id = Column(INTEGER(unsigned=True), primary_key=True)
    title = Column(VARCHAR(64), nullable=False)
    subtitle = Column(VARCHAR(128), default=default_subtitle)
    # content = Column(TEXT, nullable=False)
    # token = Column(CHAR(12), unique=True)

    chapter_id = Column(INTEGER(unsigned=True), ForeignKey("chapter.id", ondelete='SET NULL'))
    chapter = relationship('Chapter', backref=backref('subchapters'))