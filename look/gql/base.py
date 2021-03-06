import datetime
import hmac
from hashlib import sha256
import graphene

from look.exc.handler import CodeduExceptionHandler

from falcon import HTTPBadRequest, HTTPUnauthorized

from sqlalchemy.sql.expression import func, select

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
        if info.context['auth']['data']:
            if not info.context['auth']['data']['admin']: raise CodeduExceptionHandler(HTTPUnauthorized(description='PERMISSION DENIED'))
            model = model._meta.model
            data = kwargs.get('data', None)
            if data:
                db_session = info.context.get('session', None)
                if db_session:
                    instance = model(**data)
                    db_session.add(instance)
                    db_session_flush(db_session)

                return cls(**{model.__tablename__:instance})
        else:
            raise CodeduExceptionHandler(HTTPUnauthorized(description=info.context['auth']['description']))

    def update_mutate(cls, info, model=None, **kwargs):
        if info.context['auth']['data']:
            if not info.context['auth']['data']['admin']: raise CodeduExceptionHandler(HTTPUnauthorized(description='PERMISSION DENIED'))
            query = model.get_query(info)
            model = model._meta.model
            data = kwargs.get('data', None)
            if data:
                instance = get_instance_by_pk(query, model, data)

                instance.update(data)
                return cls(**{model.__tablename__:instance.one()})
        else:
            raise CodeduExceptionHandler(HTTPUnauthorized(description=info.context['auth']['description']))

    def delete_mutate(cls, info, model=None, **kwargs):
        if info.context['auth']['data']:
            if not info.context['auth']['data']['admin']: raise CodeduExceptionHandler(HTTPUnauthorized(description='PERMISSION DENIED'))
            query = model.get_query(info)
            model = model._meta.model
            data = kwargs.get('data', None)
            if data:
                instance = get_instance_by_pk(query, model, data)

                tmp_instance = instance.one()
                instance.delete()
                return cls(**{model.__tablename__:tmp_instance})
        else:
            raise CodeduExceptionHandler(HTTPUnauthorized(description=info.context['auth']['description']))

    query_field = {}
    mutation_field = {}
    input_classes = {}
    filter_field = {}
    fcf_field = {}

    def random_quiz(cls, info, query, value, model):
        return query.order_by(func.rand()), None

    for tablename, model in gql_models.items():
        filter_class_fields = {}
        if tablename in ['lesson_quiz']:
            filter_class_fields['random'] = graphene.Boolean()
            filter_class_fields['random_filter'] = classmethod(lambda cls, info, query, value, model=model: random_quiz(cls, info, query, value, model))
        filter_field[tablename] = create_filter_class(f"{tablename}Filter", model._meta.model, filter_class_fields)()
        fcf_field[model._meta.model] = filter_field[tablename]
    
    FCF = type("FCF", (FilterableConnectionField,), {
        "filters":fcf_field,
    })
    except_table = ['user', 'post', 'post_comment', 'code', 'code_comment', 'question', 'answer', 'like']
    except_table += ["post_like", "post_comment_like", "code_like", "code_comment_like", "question_like", "answer_like"]
    for tablename, model in gql_models.items():
        if not tablename in except_table:
            fields = {}
            for colname, column in model._meta.model.__table__.columns.items():
                if not colname == 'created' and not colname == 'modified':
                    fields[colname] = convert_sqlalchemy_type(getattr(column, 'type', None), column)()
            for colname, column in model._meta.model.__mapper__.relationships.items():
                    fields[colname] = convert_sqlalchemy_type(getattr(column, 'type', None), column)()

            input_classes[tablename] = create_input_class(f"{tablename}Input", fields)

            mutation_field[f"create_{tablename}"] = create_mutation_field(f"Create{tablename}", model, create_mutate, input_classes[tablename])
            mutation_field[f"update_{tablename}"] = create_mutation_field(f"Update{tablename}", model, update_mutate, input_classes[tablename])
            mutation_field[f"delete_{tablename}"] = create_mutation_field(f"Delete{tablename}", model, delete_mutate, input_classes[tablename])

        tmp_node = create_node_class(f"{tablename}Node", model._meta.model, FCF.factory)
        
        tmp_node._meta.connection.total_count = graphene.Int()
        tmp_node._meta.connection.resolve_total_count = lambda self, info, **kwargs: self.length
        tmp_node._meta.connection._meta.fields["total_count"] = graphene.Field(graphene.NonNull(graphene.Int))
        
        tmp_connection = create_connection_class(
            f"{tablename}Connection",
            tmp_node,
        )
        query_field[tablename] = FCF(tmp_connection)

    return (query_field, mutation_field)