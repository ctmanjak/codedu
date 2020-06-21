# from sqlalchemy import Column, ForeignKey
# from sqlalchemy.orm import relationship, backref
# from sqlalchemy.dialects.mysql import INTEGER, VARCHAR, BIGINT

# from . import Base

# class Like(Base):
#     __tablename__ = 'like'

#     id = Column(BIGINT(unsigned=True), primary_key=True)
#     tablename = Column(VARCHAR(32), nullable=False)
#     table_id = Column(BIGINT(unsigned=True))

#     user_id = Column(INTEGER(unsigned=True), ForeignKey("user.id", ondelete='SET NULL'))
#     user = relationship('User', backref=backref('likes', order_by=id))
