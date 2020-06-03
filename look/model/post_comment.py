from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.mysql import BIGINT, INTEGER, VARCHAR

from . import Base

class PostComment(Base):
    __tablename__ = 'post_comment'

    id = Column(BIGINT(unsigned=True), primary_key=True)
    content = Column(VARCHAR(1024), nullable=False)
    user_id = Column(VARCHAR(32), nullable=False)
    like = Column(INTEGER(unsigned=True), nullable=False, default=0)

    post_id = Column(BIGINT(unsigned=True), ForeignKey("post.id"), nullable=True)
    post = relationship('Post', backref=backref('comments', order_by=id, cascade="all, delete"), cascade="all, delete")