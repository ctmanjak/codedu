# from sqlalchemy import Column, ForeignKey
# from sqlalchemy.orm import relationship, backref
# from sqlalchemy.dialects.mysql import INTEGER, VARCHAR, BIGINT

# from . import Base

# class Qna(Base):
#     __tablename__ = 'qna'

#     id = Column(BIGINT(unsigned=True), primary_key=True)
#     title = Column(VARCHAR(64), nullable=False)
#     content = Column(VARCHAR(1024), nullable=False)
#     view = Column(INTEGER(unsigned=True), nullable=False, default=0)
#     like = Column(INTEGER(unsigned=True), nullable=False, default=0)
#     tags = Column(VARCHAR(128))

#     user_id = Column(INTEGER(unsigned=True), ForeignKey("user.id"), nullable=True)
#     user = relationship('User', backref=backref('posts', order_by=id, cascade="all, delete"), cascade="all, delete")

#     post_id = Column(BIGINT(unsigned=True), ForeignKey("post.id"), nullable=False)
#     post = relationship('Post', backref=backref('comments', order_by=id, cascade="all, delete"), cascade="all, delete")

#     parent_comment_id = Column(BIGINT(unsigned=True), ForeignKey("post_comment.id"))
#     child_comments = relationship('PostComment', backref=backref('parent_comment',  remote_side=[id]))