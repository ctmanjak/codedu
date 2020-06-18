import graphene

from look.exc.handler import CodeduExceptionHandler

from falcon import HTTPUnauthorized

from . import gql_models
from .util import create_input_class, create_mutation_field, get_instance_by_pk, check_row_by_user_id, \
    db_session_flush, image_handle, code_handle

def create_code_schema():
    def create_code_mutate(cls, info, model=None, **kwargs):
        if info.context['auth']['data']:
            model = model._meta.model
            data = kwargs.get('data', None)
            if data:
                data['user_id'] = info.context['auth']['data']['user_id']
                code = data['code']
                del data['code']
                db_session = info.context.get('session', None)
                if db_session:
                    instance = model(**data)
                    db_session.add(instance)
                    db_session_flush(db_session)
                    
                    if code:
                        code_handle(instance, code)

                return cls(**{model.__tablename__:instance})
        else:
            raise CodeduExceptionHandler(HTTPUnauthorized(description=info.context['auth']['description']))

    def update_code_mutate(cls, info, model=None, **kwargs):
        if info.context['auth']['data']:
            query = model.get_query(info)
            model = model._meta.model
            data = kwargs.get('data', None)
            if data:
                code = data.get('code', None)
                if code:
                    del data['code']
                instance = get_instance_by_pk(query, model, data)

                if info.context['auth']['data']['admin'] or check_row_by_user_id(info.context['auth']['data']['user_id'], model, instance):
                    instance.update(data)
                    if code:
                        code_handle(instance.one(), code)
                    return cls(**{model.__tablename__:instance.one()})
                else:
                    raise CodeduExceptionHandler(HTTPUnauthorized(description="PERMISSION DENIED"))
        else:
            raise CodeduExceptionHandler(HTTPUnauthorized(description=info.context['auth']['description']))

    def delete_code_mutate(cls, info, model=None, **kwargs):
        if info.context['auth']['data']:
            query = model.get_query(info)
            model = model._meta.model
            data = kwargs.get('data', None)
            if data:
                instance = get_instance_by_pk(query, model, data)
                
                if info.context['auth']['data']['admin'] or check_row_by_user_id(info.context['auth']['data']['user_id'], model, instance):
                    tmp_instance = instance.one()
                    instance.delete()
                    code_handle(tmp_instance, None)
                    return cls(**{model.__tablename__:tmp_instance})
                else:
                    raise CodeduExceptionHandler(HTTPUnauthorized(description="PERMISSION DENIED"))
        else:
            raise CodeduExceptionHandler(HTTPUnauthorized(description=info.context['auth']['description']))

    query_field = {}
    mutation_field = {}

    mutation_field["create_code"] = create_mutation_field("CreateCode",
        gql_models['code'],
        create_code_mutate,
        create_input_class('CreateCodeInput', {
            'title': graphene.String(required=True),
            'lang': graphene.String(required=True),
            'code': graphene.String(required=True),
        })
    )

    mutation_field["update_code"] = create_mutation_field("UpdateCode",
        gql_models['code'],
        update_code_mutate,
        create_input_class('UpdateCodeInput', {
            "id": graphene.ID(required=True),
            'title': graphene.String(),
            'code': graphene.String(),
        }),
    )

    mutation_field["delete_code"] = create_mutation_field("DeleteCode",
        gql_models['code'],
        delete_code_mutate,
        create_input_class('DeleteCodeInput', {
            "id": graphene.ID(required=True)
        }),
    )

    return (query_field, mutation_field)