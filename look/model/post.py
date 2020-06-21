from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.mysql import INTEGER, VARCHAR, BIGINT

from . import Base

class Post(Base):
    __tablename__ = 'post'

    id = Column(BIGINT(unsigned=True), primary_key=True)
    content = Column(VARCHAR(1024), nullable=False)
    image = Column(VARCHAR(64))
    view = Column(INTEGER(unsigned=True), nullable=False, default=0)

    user_id = Column(INTEGER(unsigned=True), ForeignKey("user.id", ondelete='SET NULL'))
    user = relationship('User', backref=backref('posts', order_by=id))

class PostLike(Base):
    __tablename__ = 'post_like'

    user_id = Column(INTEGER(unsigned=True), ForeignKey("user.id", ondelete='CASCADE'), primary_key=True)
    user = relationship('User', backref=backref('post_likes'))
    
    post_id = Column(BIGINT(unsigned=True), ForeignKey("post.id", ondelete='CASCADE'), primary_key=True)
    post = relationship('Post', backref=backref('likes'))