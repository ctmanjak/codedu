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

    user_id = Column(INTEGER(unsigned=True), ForeignKey("user.id"), nullable=True)
    user = relationship('User', backref=backref('questions', order_by=id, cascade="all, delete"), cascade="all, delete")

    tags = relationship("Tag", backref="questions", secondary="question_tag", cascade="all, delete")

class Answer(Base):
    __tablename__ = 'answer'

    id = Column(BIGINT(unsigned=True), primary_key=True)
    content = Column(VARCHAR(1024), nullable=False)
    like = Column(INTEGER(unsigned=True), nullable=False, default=0)

    user_id = Column(INTEGER(unsigned=True), ForeignKey("user.id"), nullable=True)
    user = relationship('User', backref=backref('answers', order_by=id, cascade="all, delete"), cascade="all, delete")

    question_id = Column(BIGINT(unsigned=True), ForeignKey("question.id"), nullable=False)
    question = relationship('Question', backref=backref('answers', order_by=id, cascade="all, delete"), cascade="all, delete")

class QuestionTag(Base):
    __tablename__ = 'question_tag'

    question_id = Column(BIGINT(unsigned=True), ForeignKey("question.id"), primary_key=True)
    tag_id = Column(INTEGER(unsigned=True), ForeignKey("tag.id"), primary_key=True)