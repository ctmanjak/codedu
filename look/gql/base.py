import datetime
import hmac
from hashlib import sha256
import graphene

from falcon import HTTPBadRequest, HTTPUnauthorized

from graphene_sqlalchemy import SQLAlchemyObjectType
from graphene_sqlalchemy.converter import convert_sqlalchemy_type
from graphene_sqlalchemy_filter import FilterableConnectionField

from look.config import Config

from . import gql_models
from .util import create_input_class, create_mutation_field, get_instance_by_pk, check_row_by_user_id, \
    create_filter_class, create_connection_class, create_node_class, db_session_flush

def create_base_schema():
    def resolve_model(self, info, model, **kwargs):
        query = model.get_query(info)
        search = info.context.get('search', None)
        
        if 'password' in kwargs:
            raise CodeduExceptionHandler(HTTPBadRequest(description="you can't find user with password"))

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
            db_session = info.context.get('session', None)
            if db_session:
                instance = model(**data)
                db_session.add(instance)
                db_session_flush(db_session)

            return cls(**{model.__tablename__:instance})

    def update_mutate(cls, info, model=None, **kwargs):
        if info.context['auth']['data']:
            query = model.get_query(info)
            model = model._meta.model
            data = kwargs.get('data', None)
            if data:
                instance = get_instance_by_pk(query, model, data)

                if info.context['auth']['data']['admin']:
                # if info.context['auth']['data']['admin'] and check_row_by_user_id(info.context['auth']['data']['user_id'], model, instance):
                    instance.update(data)
                    return cls(**{model.__tablename__:instance.one()})
                else:
                    raise CodeduExceptionHandler(HTTPUnauthorized(description='PERMISSION DENIED'))
        else:
            raise CodeduExceptionHandler(HTTPUnauthorized(description=info.context['auth']['description']))

    def delete_mutate(cls, info, model=None, **kwargs):
        if info.context['auth']['data']:
            query = model.get_query(info)
            model = model._meta.model
            data = kwargs.get('data', None)
            if data:
                instance = get_instance_by_pk(query, model, data)

                if info.context['auth']['data']['admin']:
                # if info.context['auth']['data']['admin'] and check_row_by_user_id(info.context['auth']['data']['user_id'], model, instance):
                    tmp_instance = instance.one()
                    instance.delete()
                    return cls(**{model.__tablename__:tmp_instance})
                else:
                    raise CodeduExceptionHandler(HTTPUnauthorized(description='PERMISSION DENIED'))
        else:
            raise CodeduExceptionHandler(HTTPUnauthorized(description=info.context['auth']['description']))

    query_field = {}
    mutation_field = {}
    input_classes = {}
    filter_field = {}
    fcf_field = {}

    for tablename, model in gql_models.items():
        filter_field[tablename] = create_filter_class(f"{tablename}Filter", model._meta.model)()
        fcf_field[model._meta.model] = filter_field[tablename]
    
    FCF = type("FCF", (FilterableConnectionField,), {
        "filters":fcf_field,
    })

    for tablename, model in gql_models.items():
        if not tablename in ['user', 'post']:
            fields = {}
            for colname, column in model._meta.model.__table__.columns.items():
                if not colname == 'created' and not colname == 'modified':
                    fields[colname] = convert_sqlalchemy_type(getattr(column, 'type', None), column)()

            input_classes[tablename] = create_input_class(f"{tablename}Input", fields)

            mutation_field[f"create_{tablename}"] = create_mutation_field(f"Create{tablename}", model, create_mutate, input_classes[tablename])
            mutation_field[f"update_{tablename}"] = create_mutation_field(f"Update{tablename}", model, update_mutate, input_classes[tablename])
            mutation_field[f"delete_{tablename}"] = create_mutation_field(f"Delete{tablename}", model, delete_mutate, input_classes[tablename])

        tmp_node = create_node_class(f"{tablename}Node", model, FCF.factory)
        
        tmp_node._meta.connection.total_count = graphene.Int()
        tmp_node._meta.connection.resolve_total_count = lambda self, info, **kwargs: self.length
        tmp_node._meta.connection._meta.fields["total_count"] = graphene.Field(graphene.NonNull(graphene.Int))

        tmp_connection = create_connection_class(
            f"{tablename}Connection",
            tmp_node,
        )
        query_field[tablename] = FCF(tmp_connection)

    return (query_field, mutation_field)