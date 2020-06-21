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

    user_id = Column(INTEGER(unsigned=True), ForeignKey("user.id", ondelete='SET NULL'))
    user = relationship('User', backref=backref('questions', order_by=id))

    tags = relationship("Tag", backref=backref("questions", order_by=id), secondary="question_tag")

class Answer(Base):
    __tablename__ = 'answer'

    id = Column(BIGINT(unsigned=True), primary_key=True)
    content = Column(VARCHAR(1024), nullable=False)

    user_id = Column(INTEGER(unsigned=True), ForeignKey("user.id", ondelete='SET NULL'))
    user = relationship('User', backref=backref('answers', order_by=id))

    question_id = Column(BIGINT(unsigned=True), ForeignKey("question.id", ondelete='CASCADE'), nullable=False)
    question = relationship('Question', backref=backref('answers', order_by=id))

class QuestionTag(Base):
    __tablename__ = 'question_tag'

    question_id = Column(BIGINT(unsigned=True), ForeignKey("question.id", ondelete='CASCADE'), primary_key=True)
    tag_id = Column(INTEGER(unsigned=True), ForeignKey("tag.id", ondelete='CASCADE'), primary_key=True)

class QuestionLike(Base):
    __tablename__ = 'question_like'

    user_id = Column(INTEGER(unsigned=True), ForeignKey("user.id", ondelete='CASCADE'), primary_key=True)
    user = relationship('User', backref=backref('question_likes'))
    
    question_id = Column(BIGINT(unsigned=True), ForeignKey("question.id", ondelete='CASCADE'), primary_key=True)
    question = relationship('Question', backref=backref('likes'))

class AnswerLike(Base):
    __tablename__ = 'answer_like'

    user_id = Column(INTEGER(unsigned=True), ForeignKey("user.id", ondelete='CASCADE'), primary_key=True)
    user = relationship('User', backref=backref('answer_likes'))
    
    answer_id = Column(BIGINT(unsigned=True), ForeignKey("answer.id", ondelete='CASCADE'), primary_key=True)
    answer = relationship('Answer', backref=backref('likes'))