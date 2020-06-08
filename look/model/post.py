from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.mysql import INTEGER, VARCHAR, BIGINT

from . import Base

class Post(Base):
    __tablename__ = 'post'

    id = Column(BIGINT(unsigned=True), primary_key=True)
    content = Column(VARCHAR(1024), nullable=False)
    image = Column(VARCHAR(128))
    view = Column(INTEGER(unsigned=True), nullable=False, default=0)
    like = Column(INTEGER(unsigned=True), nullable=False, default=0)

    user_id = Column(INTEGER(unsigned=True), ForeignKey("user.id"), nullable=True)
    user = relationship('User', backref=backref('posts', order_by=id, cascade="all, delete"), cascade="all, delete")