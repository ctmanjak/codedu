from sqlalchemy import Column, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import INTEGER, VARCHAR

from look.model.base import Base
from look.model.subchapter import Subchapter

_learning_progress = Table('learning_progress', Base.metadata,
    Column('user_id', INTEGER(unsigned=True), ForeignKey('user.id')),
    Column('subchapter_id', INTEGER(unsigned=True), ForeignKey('subchapter.id')),
)

class User(Base):
    __tablename__ = 'user'

    id = Column(INTEGER(unsigned=True), primary_key=True)
    username = Column(VARCHAR(32), nullable=False, unique=True)
    email = Column(VARCHAR(255), nullable=False)
    password = Column(VARCHAR(64), nullable=False)
    exp = Column(INTEGER(unsigned=True), nullable=False, default=0)
    user_img = Column(VARCHAR(128))

    learning_progress = relationship('Subchapter', secondary=_learning_progress, cascade="all, delete")