import json
import jwt
import graphene
import datetime
from hashlib import sha256

from falcon.uri import parse_query_string

from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from graphene.types.json import JSONString

from graphene_sqlalchemy.converter import convert_sqlalchemy_type
from graphene_sqlalchemy.registry import Registry

from look.config import Config
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
        data["modified"] = datetime.datetime.utcnow()
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

    def login_mutate(cls, info, model=None, **kwargs):
        query = model.get_query(info)
        model = model._meta.model
        data = kwargs.get('data', None)

        if 'username' in data and 'password' in data:
            user = query.filter(model.username == data['username']).one()

            if user.password == sha256(data['password'].encode()).hexdigest():
                encoded_jwt = jwt.encode({
                    'username':data['username'],
                    'iat':datetime.datetime.utcnow(),
                    # 'exp':datetime.datetime.utcnow() + datetime.timedelta(seconds=30),
                }, Config.SECRET_KEY, algorithm='HS256')

        return cls(**{'user':user, 'token': encoded_jwt.decode()})

    def create_input_class(classname, fields):
        return type(classname,
            (graphene.InputObjectType,),
            dict(map(lambda x: (x[0], x[1]), fields.items())),
        )

    def create_mutation_field(classname, model, mutate_func, input_class, additional_fields={}):
        tablename = model._meta.model.__table__.fullname
        tmp_field = additional_fields
        tmp_field["Arguments"] = type("Arguments", (), {
            "data": input_class(),
        })
        tmp_field[tablename] = graphene.Field(model)
        tmp_field["mutate"] = classmethod(lambda cls, _, info, model=model, **kwargs: mutate_func(cls, info, model, **kwargs))
        
        return type(classname, (graphene.Mutation,), tmp_field).Field()

    query_field = {}
    tmp_class = {}
    mutation_field = {}
    input_classes = {}
    
    for tablename, model in models.items():
        fields = {}
        for colname, column in model._meta.model.__table__.columns.items():
            if not colname == 'created' and not colname == 'modified':
                fields[colname] = convert_sqlalchemy_type(getattr(column, 'type', None), column)()
        
        query_field[tablename] = graphene.List(model, **(dict(a for a in map(lambda x: (x[0], graphene.Argument(type(x[1]))), fields.items()))))
        query_field[f"resolve_{tablename}"] = lambda self, info, model=model, **kwargs: resolve_model(self, info, model, **kwargs)

        input_classes[tablename] = create_input_class(f"{tablename}Input", fields)

        mutation_field[f"create_{tablename}"] = create_mutation_field(f"Create{tablename}", model, create_mutate, input_classes[tablename])
        mutation_field[f"update_{tablename}"] = create_mutation_field(f"Update{tablename}", model, update_mutate, input_classes[tablename])
        mutation_field[f"delete_{tablename}"] = create_mutation_field(f"Delete{tablename}", model, delete_mutate, input_classes[tablename])

    mutation_field["register"] = mutation_field["create_user"]
    mutation_field["login"] = create_mutation_field("Login",
        models['user'],
        login_mutate,
        create_input_class('LoginInput', {
            'username': graphene.String(),
            'password': graphene.String(),
        }),
        {
            'token': graphene.String(),
        },
    )
    
    Query = type("Query", (graphene.ObjectType,), query_field)
    MyMutations = type("MyMutations", (graphene.ObjectType,), mutation_field)
    return {'query': Query, 'mutation': MyMutations}

schema = graphene.Schema(**init_schema())