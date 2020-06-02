import datetime
import hmac
from hashlib import sha256

from graphene_sqlalchemy import SQLAlchemyObjectType

from graphene_sqlalchemy.converter import convert_sqlalchemy_type

from look.model import Base

from .util import create_gql_model, create_query_field, create_input_class, create_mutation_field, get_instance_by_pk

def create_base_schema():
    models = {}

    for model in Base._decl_class_registry.values():
        if hasattr(model, '__table__'):
            tablename = model.__table__.fullname
            models[tablename] = create_gql_model(tablename, model)

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
        if data:
            if 'password' in data: data['password'] = hmac.new(Config.SECRET_KEY.encode(), data['password'].encode(), sha256).hexdigest()
            db_session = info.context.get('session', None)
            if db_session:
                instance = model(**data)
                db_session.add(instance)

            return cls(**{model.__tablename__:instance})

    def update_mutate(cls, info, model=None, **kwargs):
        query = model.get_query(info)
        model = model._meta.model
        data = kwargs.get('data', None)
        if data:
            data["modified"] = datetime.datetime.utcnow()
            if 'password' in data: data['password'] = hmac.new(Config.SECRET_KEY.encode(), data['password'].encode(), sha256).hexdigest()
            
            instance = get_instance_by_pk(query, model, data)

            instance.update(data)

            return cls(**{model.__tablename__:instance.one()})

    def delete_mutate(cls, info, model=None, **kwargs):
        query = model.get_query(info)
        model = model._meta.model
        data = kwargs.get('data', None)
        if data:
            instance = get_instance_by_pk(query, model, data)
            tmp_instance = instance.one()

            instance.delete()

            return cls(**{model.__tablename__:tmp_instance})

    query_field = {}
    mutation_field = {}
    input_classes = {}

    for tablename, model in models.items():
        fields = {}
        for colname, column in model._meta.model.__table__.columns.items():
            if not colname == 'created' and not colname == 'modified':
                fields[colname] = convert_sqlalchemy_type(getattr(column, 'type', None), column)()
        
        query_field[tablename], query_field[f"resolve_{tablename}"] = create_query_field(model, resolve_model, fields)

        input_classes[tablename] = create_input_class(f"{tablename}Input", fields)

        mutation_field[f"create_{tablename}"] = create_mutation_field(f"Create{tablename}", model, create_mutate, input_classes[tablename])
        mutation_field[f"update_{tablename}"] = create_mutation_field(f"Update{tablename}", model, update_mutate, input_classes[tablename])
        mutation_field[f"delete_{tablename}"] = create_mutation_field(f"Delete{tablename}", model, delete_mutate, input_classes[tablename])

    return (query_field, mutation_field)