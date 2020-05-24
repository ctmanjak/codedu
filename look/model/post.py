# from sqlalchemy import Column
# from sqlalchemy.orm import relationship
# from sqlalchemy.dialects.mysql import INTEGER, VARCHAR, BIGINT

# from look.model.base import Base

# class Board(Base):
#     __tablename__ = 'board'

#     id = Column(BIGINT(unsigned=True), primary_key=True)
#     content = Column(VARCHAR(32), nullable=False)
#     subtitle = Column(VARCHAR(64), nullable=False)

#     chapter = relationship('Chapter')