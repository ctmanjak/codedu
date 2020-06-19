from sqlalchemy import Column
from sqlalchemy.dialects.mysql import INTEGER, VARCHAR

from . import Base

class Tag(Base):
    __tablename__ = 'tag'

    id = Column(INTEGER(unsigned=True), primary_key=True)
    name = Column(VARCHAR(32), nullable=False, unique=True)
    description = Column(VARCHAR(512))