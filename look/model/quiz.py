# from sqlalchemy import Column, ForeignKey
# from sqlalchemy.orm import relationship, backref
# from sqlalchemy.dialects.mysql import INTEGER, VARCHAR

# from . import Base

# class Quiz(Base):
#     __tablename__ = 'quiz'

#     id = Column(INTEGER(unsigned=True), primary_key=True)
#     question = Column(VARCHAR(128), nullable=False)
#     choice = Column(VARCHAR(512), nullable=False)
#     answer = Column(INTEGER, nullable=False)

#     subchapter_id = Column(INTEGER(unsigned=True), ForeignKey("subchapter.id", ondelete='SET NULL'))
#     subchapter = relationship('Subchapter', backref=backref('quizzes'))