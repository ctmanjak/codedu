from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.mysql import INTEGER, VARCHAR, BIGINT

from . import Base

class Code(Base):
    __tablename__ = 'code'

    id = Column(BIGINT(unsigned=True), primary_key=True)
    title = Column(VARCHAR(64), nullable=False)
    lang = Column(VARCHAR(32), nullable=False)
    path = Column(VARCHAR(64))
    view = Column(INTEGER(unsigned=True), nullable=False, default=0)
    like = Column(INTEGER(unsigned=True), nullable=False, default=0)

    user_id = Column(INTEGER(unsigned=True), ForeignKey("user.id"), nullable=True)
    user = relationship('User', backref=backref('codes', order_by=id, cascade="all, delete"), cascade="all, delete")

class CodeComment(Base):
    __tablename__ = 'code_comment'

    id = Column(BIGINT(unsigned=True), primary_key=True)
    content = Column(VARCHAR(1024), nullable=False)
    like = Column(INTEGER(unsigned=True), nullable=False, default=0)

    user_id = Column(INTEGER(unsigned=True), ForeignKey("user.id"), nullable=False)
    user = relationship('User', backref=backref('code_comments', order_by=id, cascade="all, delete"), cascade="all, delete")

    code_id = Column(BIGINT(unsigned=True), ForeignKey("code.id"), nullable=False)
    code = relationship('Code', backref=backref('comments', order_by=id, cascade="all, delete"), cascade="all, delete")

    parent_comment_id = Column(BIGINT(unsigned=True), ForeignKey("code_comment.id"))
    child_comments = relationship('CodeComment', backref=backref('parent_comment',  remote_side=[id]))