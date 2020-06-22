from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.mysql import INTEGER, VARCHAR, TEXT, CHAR, TINYINT

from . import Base

class Lesson(Base):
    __tablename__ = 'lesson'

    id = Column(INTEGER(unsigned=True), primary_key=True)
    content = Column(TEXT, nullable=False)
    # token = Column(CHAR(12), unique=True)

    subchapter_id = Column(INTEGER(unsigned=True), ForeignKey("subchapter.id", ondelete='SET NULL'))
    subchapter = relationship('Subchapter', backref=backref('lessons'))

class LessonQuiz(Base):
    __tablename__ = 'lesson_quiz'

    id = Column(INTEGER(unsigned=True), primary_key=True)
    question = Column(VARCHAR(128), nullable=False)

    lesson_id = Column(INTEGER(unsigned=True), ForeignKey("lesson.id", ondelete='SET NULL'))
    lesson = relationship('Lesson', backref=backref('quizzes'))

class LessonQuizAnswer(Base):
    __tablename__ = 'lesson_quiz_answer'

    id = Column(INTEGER(unsigned=True), primary_key=True)
    content = Column(VARCHAR(128), nullable=False)
    is_correct = Column(TINYINT(unsigned=True), nullable=False)

    lesson_quiz_id = Column(INTEGER(unsigned=True), ForeignKey("lesson_quiz.id", ondelete='CASCADE'), nullable=False)
    lesson_quiz = relationship('LessonQuiz', backref=backref('answers'))