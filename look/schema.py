import json
import graphene
from datetime import datetime
from hashlib import sha256

from falcon.uri import parse_query_string

from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from graphene.types.json import JSONString

from graphene_sqlalchemy.converter import convert_sqlalchemy_type
from graphene_sqlalchemy.registry import Registry

from look.model import Base, User as UserModel

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError, OperationalError

def init_schema():
    models = {}
    print("init_schema")

    for model in Base._decl_class_registry.values():
        if hasattr(model, '__table__'):
            tablename = model.__table__.fullname
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
        model = model._meta.model
        data = kwargs.get('data', None)
        if 'password' in data: data['password'] = sha256(data['password'].encode()).hexdigest()
        db_session = info.context.get('session', None)
        if db_session:
            instance = model(**data)
            db_session.add(instance)

        return cls(**{model.__tablename__:instance})

    def get_instance_by_pk(query, model, data):
        primary_keys = [a for a in model.__table__.primary_key]

        find_pks = {}
        for pk in primary_keys:
            if pk.name in data:
                find_pks[pk.name] = data[pk.name]

        if find_pks:
            instance = query.filter_by(**find_pks)

        return instance

    def update_mutate(cls, info, model=None, **kwargs):
        query = model.get_query(info)
        model = model._meta.model
        data = kwargs.get('data', None)
        data["modified"] = datetime.utcnow()
        if 'password' in data: data['password'] = sha256(data['password'].encode()).hexdigest()
        
        instance = get_instance_by_pk(query, model, data)

        instance.update(data)

        return cls(**{model.__tablename__:instance.one()})

    def delete_mutate(cls, info, model=None, **kwargs):
        query = model.get_query(info)
        model = model._meta.model
        data = kwargs.get('data', None)
        
        instance = get_instance_by_pk(query, model, data)
        
        tmp_instance = instance.one()
        instance.delete()

        return cls(**{model.__tablename__:tmp_instance})

    def create_mutataion_attr(control_name, mutate_func):
        return type(f"{control_name}{tablename}", (graphene.Mutation,), {
            "Arguments": type("Arguments", (), {
                f"data": input_classes[tablename](),
            }),
            tablename: graphene.Field(model),
            "mutate": classmethod(lambda cls, _, info, model=model, **kwargs: mutate_func(cls, info=info, model=model, **kwargs)),
        }).Field()

    tmp_class = {}
    mutation_attr = {}
    input_classes = {}
    print(models)
    for tablename, model in models.items():
        fields = {}
        for colname, column in model._meta.model.__table__.columns.items():
            fields[colname] = convert_sqlalchemy_type(getattr(column, 'type', None), column)
        
        query_attr[tablename] = graphene.List(model, **(dict(a for a in map(lambda x: (x[0], graphene.Argument(x[1])), fields.items()))))
        query_attr[f"resolve_{tablename}"] = lambda self, info, model=model, **kwargs: resolve_model(self, info, model, **kwargs)

        input_classes[tablename] = type(f"{tablename}Input", (graphene.InputObjectType,), dict(a for a in map(lambda x: (x[0], x[1]()), fields.items())))

        mutation_attr[f"create_{tablename}"] = create_mutataion_attr("create", create_mutate)
        mutation_attr[f"update_{tablename}"] = create_mutataion_attr("update", update_mutate)
        mutation_attr[f"delete_{tablename}"] = create_mutataion_attr("delete", delete_mutate)

    Query = type("Query", (graphene.ObjectType,), query_attr)
    MyMutations = type("MyMutations", (graphene.ObjectType,), mutation_attr)
    return {'query': Query, 'mutation': MyMutations}

schema = graphene.Schema(**init_schema())