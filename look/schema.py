import json
import graphene
from hashlib import sha256

from falcon.uri import parse_query_string

from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from graphene.types.json import JSONString

from graphene_sqlalchemy.converter import convert_sqlalchemy_type
from graphene_sqlalchemy.registry import Registry

from look.model import Base, User as UserModel

from sqlalchemy.exc import IntegrityError, OperationalError

def init_schema():
    models = {}
    print("init_schema")

    for model in Base._decl_class_registry.values():
        if hasattr(model, '__tablename__'):
            tablename = model.__tablename__
            models[tablename] = type(tablename, (SQLAlchemyObjectType,), {
                "Meta": type("Meta", (), {
                    "model": model,
                }),
            })

    query_attr = {}

    def resolve_model(self, info, model, **kwargs):
        query = model.get_query(info)
        search = info.context.get('search', None)

        for arg, value in kwargs.items():
            if search:
                print('search')
                query = query.filter(getattr(model._meta.model, arg).like(f"%{value}%"))
            else:
                print('match')
                query = query.filter(getattr(model._meta.model, arg) == value)

        user = query.all()

        return user

    def create_mutate(cls, info, model=None, **kwargs):
        data = kwargs.get('data', None)
        if 'password' in data: data['password'] = sha256(data['password'].encode()).hexdigest()
        db_session = info.context.get('session', None)
        if db_session:
            instance = model(**data)
            db_session.add(instance)

        return cls(**{model.__tablename__:instance})

    tmp_class = {}
    mutation_attr = {}
    for tablename, model in models.items():
        fields = {}
        for colname, column in model._meta.model.__table__.columns.items():
            fields[colname] = convert_sqlalchemy_type(getattr(column, 'type', None), column)
        
        query_attr[f"{tablename}"] = graphene.List(model, **(dict(a for a in map(lambda x: (x[0], graphene.Argument(x[1])), fields.items()))))
        query_attr[f"resolve_{tablename}"] = lambda self, info, model=model, **kwargs: resolve_model(self, info, model, **kwargs)

        mutation_attr[f"create_{tablename}"] = type(f"Create{tablename}", (graphene.Mutation,), {
            "Arguments": type("Arguments", (), {
                f"data": type(f"{tablename}Input", (graphene.InputObjectType,), dict(a for a in map(lambda x: (x[0], x[1]()), fields.items())))(),
            }),
            tablename: graphene.Field(model),
            "mutate": classmethod(lambda cls, _, info, model=model._meta.model, **kwargs: create_mutate(cls, info=info, model=model, **kwargs)),
        }).Field()

    Query = type("Query", (graphene.ObjectType,), query_attr)
    MyMutations = type("MyMutations", (graphene.ObjectType,), mutation_attr)
    return {'query': Query, 'mutation': MyMutations}

schema = graphene.Schema(**init_schema())