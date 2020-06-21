import sys
import shutil
import graphene

from look.exc.handler import CodeduExceptionHandler

from falcon import HTTPUnauthorized

from . import gql_models
from .util import create_input_class, create_mutation_field, get_instance_by_pk, check_row_by_user_id, \
    db_session_flush, image_handle

if "pytest" in sys.modules:
    root_path = 'test'
else: root_path = 'nfs'

def create_subchapter_schema():
    def create_subchapter_mutate(cls, info, model=None, **kwargs):
        if info.context['auth']['data']:
            if not info.context['auth']['data']['admin']: raise CodeduExceptionHandler(HTTPUnauthorized(description="PERMISSION DENIED"))
            model = model._meta.model
            data = kwargs.get('data', None)
            image_info = info.context.get('image_info', None)
            if data:
                db_session = info.context.get('session', None)
                if db_session:
                    instance = model(**data)
                    db_session.add(instance)
                    db_session_flush(db_session)

                    if image_info:
                        image_handle('subchapter', instance, image_info)

                return cls(**{model.__tablename__:instance})
        else:
            raise CodeduExceptionHandler(HTTPUnauthorized(description=info.context['auth']['description']))

    def update_subchapter_mutate(cls, info, model=None, **kwargs):
        if info.context['auth']['data']:
            if not info.context['auth']['data']['admin']: raise CodeduExceptionHandler(HTTPUnauthorized(description="PERMISSION DENIED"))
            query = model.get_query(info)
            model = model._meta.model
            data = kwargs.get('data', None)
            image_info = info.context.get('image_info', None)
            if data:
                instance = get_instance_by_pk(query, model, data)
                
                instance.update(data)
                if image_info:
                    image_handle('subchapter', instance.one(), image_info)
                return cls(**{model.__tablename__:instance.one()})
        else:
            raise CodeduExceptionHandler(HTTPUnauthorized(description=info.context['auth']['description']))

    def delete_subchapter_mutate(cls, info, model=None, **kwargs):
        if info.context['auth']['data']:
            if not info.context['auth']['data']['admin']: raise CodeduExceptionHandler(HTTPUnauthorized(description="PERMISSION DENIED"))
            query = model.get_query(info)
            model = model._meta.model
            data = kwargs.get('data', None)
            if data:
                instance = get_instance_by_pk(query, model, data)

                tmp_instance = instance.one()
                instance.delete()
                if tmp_instance.token:
                    shutil.rmtree(f"{root_path}/images/subchapter/{tmp_instance.token}")
                return cls(**{model.__tablename__:tmp_instance})
        else:
            raise CodeduExceptionHandler(HTTPUnauthorized(description=info.context['auth']['description']))

    query_field = {}
    mutation_field = {}

    mutation_field["create_subchapter"] = create_mutation_field("CreateSubchapter",
        gql_models['subchapter'],
        create_subchapter_mutate,
        create_input_class('CreateSubchapterInput', {
            'chapter_id': graphene.ID(required=True),
            'title': graphene.String(required=True),
            'subtitle': graphene.String(),
            'content': graphene.String(required=True),
        })
    )

    mutation_field["update_subchapter"] = create_mutation_field("UpdateSubchapter",
        gql_models['subchapter'],
        update_subchapter_mutate,
        create_input_class('UpdateSubchapterInput', {
            "id": graphene.ID(required=True),
            "title": graphene.String(),
            "subtitle": graphene.String(),
            "content": graphene.String(),
        }),
    )

    mutation_field["delete_subchapter"] = create_mutation_field("DeleteSubchapter",
        gql_models['subchapter'],
        delete_subchapter_mutate,
        create_input_class('DeleteSubchapterInput', {
            "id": graphene.ID(required=True)
        }),
    )

    return (query_field, mutation_field)