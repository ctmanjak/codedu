from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship, backref, foreign
from sqlalchemy.dialects.mysql import BIGINT, INTEGER, VARCHAR
from . import Base

class PostComment(Base):
    __tablename__ = 'post_comment'

    id = Column(BIGINT(unsigned=True), primary_key=True)
    content = Column(VARCHAR(1024), nullable=False)

    user_id = Column(INTEGER(unsigned=True), ForeignKey("user.id", ondelete='SET NULL'))
    user = relationship('User', backref=backref('post_comments', order_by=id))

    post_id = Column(BIGINT(unsigned=True), ForeignKey("post.id", ondelete='CASCADE'), nullable=False)
    post = relationship('Post', backref=backref('comments', order_by=id))

    parent_comment_id = Column(BIGINT(unsigned=True), ForeignKey("post_comment.id", ondelete='CASCADE'))
    child_comments = relationship('PostComment', backref=backref('parent_comment', order_by=id, remote_side=[id]))

class PostCommentLike(Base):
    __tablename__ = 'post_comment_like'

    user_id = Column(INTEGER(unsigned=True), ForeignKey("user.id", ondelete='CASCADE'), primary_key=True)
    user = relationship('User', backref=backref('post_comment_likes'))
    
    post_comment_id = Column(BIGINT(unsigned=True), ForeignKey("post_comment.id", ondelete='CASCADE'), primary_key=True)
    post_comment = relationship('PostComment', backref=backref('likes'))