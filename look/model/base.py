import datetime
import collections

from sqlalchemy import Column, DateTime, func
from sqlalchemy.ext.declarative import declarative_base, as_declarative
from sqlalchemy.ext.declarative.api import DeclarativeMeta
from sqlalchemy.orm.collections import InstrumentedList

@as_declarative()
class BaseModel(object):
    created = Column(DateTime, nullable=False, default=func.now())
    modified = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    def __init(self, **kwargs):
        for arg in kwargs:
            setattr(self, arg, kwargs(arg))

    def get_data(self, col_list=None, depth=0, print_parent=False, parents=None):
        if parents == None:
            parents = [type(self)]
        else:
            parents.append(type(self))
        
        if not col_list:
            col_list = self.__table__.columns.keys()
            for relationship in self.__mapper__.relationships.keys():
                col_list.append(relationship)
                
        tmp = {}
        for arg in col_list:
            column = getattr(self, arg)
            if not issubclass(type(column), self.__class__.__bases__[0]):
                if column and type(column) == InstrumentedList:
                    tmp[arg] = []
                    if depth > 0:
                        tmp[arg] = [obj.get_data(depth=depth-1, print_parent=print_parent, parents=list(parents)) for obj in column if not type(obj) in parents]
                    elif depth == -1:
                        tmp[arg] = [obj.get_data(depth=depth, print_parent=print_parent, parents=list(parents)) for obj in column if not type(obj) in parents]
                else:
                    tmp[arg] = str(column) if type(column) == datetime.datetime else column
            elif print_parent:
                tmp[arg] = column.get_data(depth=0, print_parent=print_parent, parents=list(parents))
        return tmp

    def __str__(self):
        cols = self.__table__.columns.keys()
        for relationship in self.__mapper__.relationships.keys():
            cols.append(relationship)
        return self.get_data(cols)

Base = declarative_base(cls=BaseModel)