from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.mysql import INTEGER, VARCHAR, BIGINT

from . import Base

class Like(Base):
    __tablename__ = 'like'

    id = Column(BIGINT(unsigned=True), primary_key=True)

    user_id = Column(INTEGER(unsigned=True), ForeignKey("user.id", ondelete='SET NULL'))
    user = relationship('User', backref=backref('test_likes'))

    type = Column(VARCHAR(50))
    __mapper_args__ = {
        'polymorphic_identity':'like',
        'polymorphic_on':"type",
    }

for tablename in ["post", "post_comment", "code", "code_comment", "question", "answer"]:
    components = tablename.split("_")
    camel_tablename = ''.join(x.title() for x in tablename.split('_'))
    globals()[f"{camel_tablename}Like"] = type(f"{camel_tablename}Like", (Like,), {
        "__tablename__": f"{tablename}_like",
        "__mapper_args__": {
            'polymorphic_identity':f"{tablename}_like",
        },
        "id": Column("like_id", BIGINT(unsigned=True), ForeignKey('like.id', ondelete='CASCADE'), primary_key=True),
        f"{tablename}_id": Column(BIGINT(unsigned=True), ForeignKey(f"{tablename}.id", ondelete='CASCADE')),
        tablename: relationship(f"{camel_tablename}", backref=backref(f'likes')),
    })