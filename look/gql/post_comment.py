import graphene

from look.exc.handler import CodeduExceptionHandler

from falcon import HTTPUnauthorized

from . import gql_models
from .util import create_input_class, create_mutation_field, get_instance_by_pk, check_row_by_user_id, \
    db_session_flush, image_handle

def create_post_comment_schema():
    def create_post_comment(cls, info, model=None, **kwargs):
        if info.context['auth']['data']:
            model = model._meta.model
            data = kwargs.get('data', None)
            image_info = info.context.get('image_info', None)
            if data:
                data['user_id'] = info.context['auth']['data']['user_id']
                db_session = info.context.get('session', None)
                if db_session:
                    instance = model(**data)
                    db_session.add(instance)
                    db_session_flush(db_session)

                return cls(**{model.__tablename__:instance})
        else:
            raise CodeduExceptionHandler(HTTPUnauthorized(description=info.context['auth']['description']))

    def update_post_comment_mutate(cls, info, model=None, **kwargs):
        if info.context['auth']['data']:
            query = model.get_query(info)
            model = model._meta.model
            data = kwargs.get('data', None)
            image_info = info.context.get('image_info', None)
            if data:
                instance = get_instance_by_pk(query, model, data)
                
                if info.context['auth']['data']['admin'] or check_row_by_user_id(info.context['auth']['data']['user_id'], model, instance):
                    instance.update(data)
                    return cls(**{model.__tablename__:instance.one()})
                else:
                    raise CodeduExceptionHandler(HTTPUnauthorized(description="PERMISSION DENIED"))
        else:
            raise CodeduExceptionHandler(HTTPUnauthorized(description=info.context['auth']['description']))

    def delete_post_comment_mutate(cls, info, model=None, **kwargs):
        if info.context['auth']['data']:
            query = model.get_query(info)
            model = model._meta.model
            data = kwargs.get('data', None)
            if data:
                instance = get_instance_by_pk(query, model, data)
                
                if info.context['auth']['data']['admin'] or check_row_by_user_id(info.context['auth']['data']['user_id'], model, instance):
                    tmp_instance = instance.one()
                    instance.delete()
                    return cls(**{model.__tablename__:tmp_instance})
                else:
                    raise CodeduExceptionHandler(HTTPUnauthorized(description="PERMISSION DENIED"))
        else:
            raise CodeduExceptionHandler(HTTPUnauthorized(description=info.context['auth']['description']))

    query_field = {}
    mutation_field = {}

    mutation_field["create_post_comment"] = create_mutation_field("CreatePostComment",
        gql_models['post_comment'],
        create_post_comment,
        create_input_class('CreatePostCommentInput', {
            'post_id': graphene.ID(required=True),
            'content': graphene.String(required=True),
        })
    )

    mutation_field["update_post_comment"] = create_mutation_field("UpdatePostComment",
        gql_models['post_comment'],
        update_post_comment_mutate,
        create_input_class('UpdatePostCommentInput', {
            "id": graphene.ID(required=True),
            "content": graphene.String(required=True),
        }),
    )

    mutation_field["delete_post_comment"] = create_mutation_field("DeletePostComment",
        gql_models['post_comment'],
        delete_post_comment_mutate,
        create_input_class('DeletePostCommentInput', {
            "id": graphene.ID(required=True)
        }),
    )

    return (query_field, mutation_field)