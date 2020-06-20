import datetime

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import INTEGER, VARCHAR, BOOLEAN, DATETIME

from . import Base

class User(Base):
    __tablename__ = 'user'

    id = Column(INTEGER(unsigned=True), primary_key=True)
    username = Column(VARCHAR(32), nullable=False)
    email = Column(VARCHAR(255, charset="utf8"), nullable=False, unique=True)
    password = Column(VARCHAR(64), nullable=False)
    password_modified = Column(DATETIME, nullable=False, default=datetime.datetime.utcnow())
    admin = Column(BOOLEAN, nullable=False, default=False)
    exp = Column(INTEGER(unsigned=True), nullable=False, default=0)
    image = Column(VARCHAR(64))

    learning_progress = relationship("Subchapter", backref="users", secondary="learning_progress")

class LearningProgress(Base):
    __tablename__ = 'learning_progress'

    user_id = Column(INTEGER(unsigned=True), ForeignKey("user.id", ondelete='CASCADE'), primary_key=True)
    subchapter_id = Column(INTEGER(unsigned=True), ForeignKey("subchapter.id", ondelete='CASCADE'), primary_key=True)