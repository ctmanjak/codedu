import graphene

from look.exc.handler import CodeduExceptionHandler

from falcon import HTTPUnauthorized

from sqlalchemy import and_

from . import gql_models
from .util import create_input_class, create_mutation_field, get_instance_by_pk, check_row_by_user_id, \
    db_session_flush, image_handle, simple_create_mutate, simple_update_mutate, simple_delete_mutate

# def create_like_schema(tablename):
#     def update_like_mutate(cls, info, model=None, **kwargs):
#         if info.context['auth']['data']:
#             query = model.get_query(info)
#             model = model._meta.model
#             data = kwargs.get('data', None)
#             image_info = info.context.get('image_info', None)
#             if data:
#                 data['user_id'] = info.context['auth']['data']['user_id']
#                 db_session = info.context.get('session', None)
#                 if db_session:
#                     instance = get_instance_by_pk(query, model, data)
#                     if not instance.first():
#                         tmp_instance = model(**data)
#                         db_session.add(tmp_instance)
#                         db_session_flush(db_session)
#                     else:
#                         tmp_instance = instance.one()
#                         instance.delete()

#                 return cls(**{model.__tablename__:tmp_instance})
#         else:
#             raise CodeduExceptionHandler(HTTPUnauthorized(description=info.context['auth']['description']))

#     query_field = {}
#     mutation_field = {}

#     mutation_field[f"update_{tablename}_like"] = create_mutation_field(f"Update{tablename}Like",
#         gql_models[f'{tablename}_like'],
#         update_like_mutate,
#         create_input_class(f'Update{tablename}LikeInput', {
#             f"{tablename}_id": graphene.ID(required=True),
#         })
#     )

#     return (query_field, mutation_field)

def create_like_schema():
    def update_like_mutate(cls, info, model=None, **kwargs):
        if info.context['auth']['data']:
            query = model.get_query(info)
            base_model = model._meta.model
            data = kwargs.get('data', None)
            image_info = info.context.get('image_info', None)
            if data:
                tablename = data['type']
                model = gql_models[f"{tablename}_like"]._meta.model
                data['user_id'] = info.context['auth']['data']['user_id']
                data[f"{tablename}_id"] = data['id']
                del data['type']
                del data['id']
                db_session = info.context.get('session', None)
                if db_session:
                    # instance = get_instance_by_pk(query, model, data)
                    instance = query.filter(and_(model.user_id==data['user_id'], getattr(model, f"{tablename}_id")==data[f'{tablename}_id']))
                    if not instance or not instance.first():
                        tmp_instance = model(**data)
                        db_session.add(tmp_instance)
                        db_session_flush(db_session)
                    else:
                        tmp_instance = instance.one()
                        instance.delete(synchronize_session='fetch')

                return cls(**{base_model.__tablename__:tmp_instance})
        else:
            raise CodeduExceptionHandler(HTTPUnauthorized(description=info.context['auth']['description']))

    query_field = {}
    mutation_field = {}

    mutation_field[f"update_like"] = create_mutation_field(f"UpdateLike",
        gql_models[f'like'],
        update_like_mutate,
        create_input_class(f'UpdateLikeInput', {
            "type": graphene.String(required=True),
            "id": graphene.ID(required=True),
        })
    )

    return (query_field, mutation_field)