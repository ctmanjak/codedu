from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import INTEGER, VARCHAR, BOOLEAN

from . import Base

class User(Base):
    __tablename__ = 'user'

    id = Column(INTEGER(unsigned=True), primary_key=True)
    username = Column(VARCHAR(32), nullable=False, unique=True)
    email = Column(VARCHAR(255), nullable=False)
    password = Column(VARCHAR(64), nullable=False)
    admin = Column(BOOLEAN, nullable=False, default=False)
    exp = Column(INTEGER(unsigned=True), nullable=False, default=0)
    user_img = Column(VARCHAR(128))

    learning_progress = relationship("Subchapter", backref="users", secondary="learning_progress", cascade="all, delete")

class LearningProgress(Base):
    __tablename__ = 'learning_progress'

    user_id = Column(INTEGER(unsigned=True), ForeignKey("user.id"), primary_key=True)
    subchapter_id = Column(INTEGER(unsigned=True), ForeignKey("subchapter.id"), primary_key=True)