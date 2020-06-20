from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.mysql import INTEGER, VARCHAR, BIGINT

from . import Base

class Question(Base):
    __tablename__ = 'question'

    id = Column(BIGINT(unsigned=True), primary_key=True)
    title = Column(VARCHAR(64), nullable=False)
    content = Column(VARCHAR(1024), nullable=False)
    view = Column(INTEGER(unsigned=True), nullable=False, default=0)
    like = Column(INTEGER(unsigned=True), nullable=False, default=0)

    user_id = Column(INTEGER(unsigned=True), ForeignKey("user.id", ondelete='SET NULL'))
    user = relationship('User', backref='questions')

    tags = relationship("Tag", backref="questions", secondary="question_tag")

class Answer(Base):
    __tablename__ = 'answer'

    id = Column(BIGINT(unsigned=True), primary_key=True)
    content = Column(VARCHAR(1024), nullable=False)
    like = Column(INTEGER(unsigned=True), nullable=False, default=0)

    user_id = Column(INTEGER(unsigned=True), ForeignKey("user.id", ondelete='SET NULL'))
    user = relationship('User', backref='answers')

    question_id = Column(BIGINT(unsigned=True), ForeignKey("question.id", ondelete='CASCADE'), nullable=False)
    question = relationship('Question', backref='answers')

class QuestionTag(Base):
    __tablename__ = 'question_tag'

    question_id = Column(BIGINT(unsigned=True), ForeignKey("question.id", ondelete='CASCADE'), primary_key=True)
    tag_id = Column(INTEGER(unsigned=True), ForeignKey("tag.id", ondelete='CASCADE'), primary_key=True)