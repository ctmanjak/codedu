import graphene

from look.exc.handler import CodeduExceptionHandler

from falcon import HTTPUnauthorized

from . import gql_models
from .util import create_input_class, create_mutation_field, get_instance_by_pk, check_row_by_user_id, \
    db_session_flush, image_handle

def create_question_schema():
    def create_question_mutate(cls, info, model=None, **kwargs):
        if info.context['auth']['data']:
            model = model._meta.model
            data = kwargs.get('data', None)
            if data:
                tags = data.get('tags', None)
                if tags:
                    del data['tags']
                data['user_id'] = info.context['auth']['data']['user_id']
                db_session = info.context.get('session', None)
                if db_session:
                    instance = model(**data)
                    if tags:
                        tags = tags.split(" ")
                        exist_tags = {tag.name:tag for tag in gql_models['tag'].get_query(info).filter(gql_models['tag']._meta.model.name.in_(tags)).all()}
                        new_tags = [gql_models['tag']._meta.model(name=tag) for tag in tags if not tag in exist_tags.keys()]
                        db_session.add_all(new_tags)
                        instance.tags = list(exist_tags.values())+new_tags
                    db_session.add(instance)
                    db_session_flush(db_session)

                return cls(**{model.__tablename__:instance})
        else:
            raise CodeduExceptionHandler(HTTPUnauthorized(description=info.context['auth']['description']))

    def update_question_mutate(cls, info, model=None, **kwargs):
        if info.context['auth']['data']:
            query = model.get_query(info)
            model = model._meta.model
            data = kwargs.get('data', None)
            if data:
                tags = data.get('tags', None)
                if tags:
                    del data['tags']
                instance = get_instance_by_pk(query, model, data)
                
                if info.context['auth']['data']['admin'] or check_row_by_user_id(info.context['auth']['data']['user_id'], model, instance):
                    instance.update(data)
                    if tags:
                        db_session = info.context.get('session', None)
                        tags = tags.split(" ")
                        exist_tags = {tag.name:tag for tag in gql_models['tag'].get_query(info).filter(gql_models['tag']._meta.model.name.in_(tags)).all()}
                        new_tags = [gql_models['tag']._meta.model(name=tag) for tag in tags if not tag in exist_tags.keys()]
                        db_session.add_all(new_tags)
                        instance.one().tags = list(exist_tags.values())+new_tags
                    return cls(**{model.__tablename__:instance.one()})
                else:
                    raise CodeduExceptionHandler(HTTPUnauthorized(description="PERMISSION DENIED"))
        else:
            raise CodeduExceptionHandler(HTTPUnauthorized(description=info.context['auth']['description']))

    def delete_question_mutate(cls, info, model=None, **kwargs):
        if info.context['auth']['data']:
            query = model.get_query(info)
            model = model._meta.model
            data = kwargs.get('data', None)
            if data:
                instance = get_instance_by_pk(query, model, data)

                if info.context['auth']['data']['admin'] or check_row_by_user_id(info.context['auth']['data']['user_id'], model, instance):
                    tmp_instance = instance.one()
                    instance.one().tags = []
                    instance.delete()
                    return cls(**{model.__tablename__:tmp_instance})
                else:
                    raise CodeduExceptionHandler(HTTPUnauthorized(description="PERMISSION DENIED"))
        else:
            raise CodeduExceptionHandler(HTTPUnauthorized(description=info.context['auth']['description']))

    query_field = {}
    mutation_field = {}

    mutation_field["create_question"] = create_mutation_field("CreateQuestion",
        gql_models['question'],
        create_question_mutate,
        create_input_class('CreateQuestionInput', {
            'title': graphene.String(required=True),
            'content': graphene.String(required=True),
            'tags': graphene.String(),
        })
    )

    mutation_field["update_question"] = create_mutation_field("UpdateQuestion",
        gql_models['question'],
        update_question_mutate,
        create_input_class('UpdateQuestionInput', {
            "id": graphene.ID(required=True),
            'title': graphene.String(),
            'content': graphene.String(),
            'tags': graphene.String(),
        }),
    )

    mutation_field["delete_question"] = create_mutation_field("DeleteQuestion",
        gql_models['question'],
        delete_question_mutate,
        create_input_class('DeleteQuestionInput', {
            "id": graphene.ID(required=True)
        }),
    )

    return (query_field, mutation_field)