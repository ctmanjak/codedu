import sys
import shutil
import graphene

from look.exc.handler import CodeduExceptionHandler

from falcon import HTTPUnauthorized

from . import gql_models
from .util import create_input_class, create_mutation_field, get_instance_by_pk, check_row_by_user_id, \
    db_session_flush, image_handle, simple_create_mutate, simple_update_mutate, simple_delete_mutate

if "pytest" in sys.modules:
    root_path = 'test'
else: root_path = 'nfs'

def create_lesson_schema():
    def create_lesson_mutate(cls, info, model=None, **kwargs):
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
                        image_handle('lesson', instance, image_info)

                return cls(**{model.__tablename__:instance})
        else:
            raise CodeduExceptionHandler(HTTPUnauthorized(description=info.context['auth']['description']))

    def update_lesson_mutate(cls, info, model=None, **kwargs):
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
                    image_handle('lesson', instance.one(), image_info)
                return cls(**{model.__tablename__:instance.one()})
        else:
            raise CodeduExceptionHandler(HTTPUnauthorized(description=info.context['auth']['description']))

    def delete_lesson_mutate(cls, info, model=None, **kwargs):
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
                    shutil.rmtree(f"{root_path}/images/lesson/{tmp_instance.token}")
                return cls(**{model.__tablename__:tmp_instance})
        else:
            raise CodeduExceptionHandler(HTTPUnauthorized(description=info.context['auth']['description']))

    query_field = {}
    mutation_field = {}

    mutation_field["create_lesson"] = create_mutation_field("CreateLesson",
        gql_models['lesson'],
        create_lesson_mutate,
        create_input_class('CreateLessonInput', {
            'subchapter_id': graphene.ID(required=True),
            'content': graphene.String(required=True),
        })
    )

    mutation_field["update_lesson"] = create_mutation_field("UpdateLesson",
        gql_models['lesson'],
        update_lesson_mutate,
        create_input_class('UpdateLessonInput', {
            "id": graphene.ID(required=True),
            "content": graphene.String(),
        }),
    )

    mutation_field["delete_lesson"] = create_mutation_field("DeleteLesson",
        gql_models['lesson'],
        delete_lesson_mutate,
        create_input_class('DeleteLessonInput', {
            "id": graphene.ID(required=True)
        }),
    )

    return (query_field, mutation_field)

def create_lesson_quiz_schema():
    def create_lesson_quiz_mutate(cls, info, model=None, **kwargs):
        if info.context['auth']['data']:
            if not info.context['auth']['data']['admin']: raise CodeduExceptionHandler(HTTPUnauthorized(description="PERMISSION DENIED"))
            model = model._meta.model
            data = kwargs.get('data', None)
            image_info = info.context.get('image_info', None)
            if data:
                answers = []
                for i, choice in enumerate(data['choice']):
                    answers_data = {'content': choice, 'is_correct': 0}
                    if i == data['answer']: answers_data['is_correct'] = 1
                    answers.append(gql_models['lesson_quiz_answer']._meta.model(**answers_data))
                del data['choice']
                del data['answer']
                db_session = info.context.get('session', None)
                if db_session:
                    instance = model(**data)
                    db_session.add(instance)
                    db_session_flush(db_session)
                    for answer in answers:
                        answer.lesson_quiz_id = instance.id
                    db_session.add_all(answers)
                    db_session_flush(db_session)

                return cls(**{model.__tablename__:instance})
        else:
            raise CodeduExceptionHandler(HTTPUnauthorized(description=info.context['auth']['description']))

    def update_lesson_quiz_mutate(cls, info, model=None, **kwargs):
        if info.context['auth']['data']:
            if not info.context['auth']['data']['admin']: raise CodeduExceptionHandler(HTTPUnauthorized(description="PERMISSION DENIED"))
            query = model.get_query(info)
            model = model._meta.model
            data = kwargs.get('data', None)
            image_info = info.context.get('image_info', None)
            if data:
                answers_data_list = []
                for i, choice in enumerate(data['choice']):
                    answers_data = {'content': choice, 'is_correct': 0}
                    if i == data['answer']: answers_data['is_correct'] = 1
                    answers_data_list.append(answers_data)
                del data['choice']
                del data['answer']
                instance = get_instance_by_pk(query, model, data)

                for i, answer in enumerate(instance.one().answers):
                    answer.content = answers_data_list[i]['content']
                    answer.is_correct = answers_data_list[i]['is_correct']
                
                instance.update(data)
                return cls(**{model.__tablename__:instance.one()})
        else:
            raise CodeduExceptionHandler(HTTPUnauthorized(description=info.context['auth']['description']))

    def delete_lesson_quiz_mutate(cls, info, model=None, **kwargs):
        if info.context['auth']['data']:
            if not info.context['auth']['data']['admin']: raise CodeduExceptionHandler(HTTPUnauthorized(description="PERMISSION DENIED"))
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

    mutation_field["create_lesson_quiz"] = create_mutation_field("CreateLessonQuiz",
        gql_models['lesson_quiz'],
        create_lesson_quiz_mutate,
        create_input_class('CreateLessonQuizInput', {
            'lesson_id': graphene.ID(required=True),
            'question': graphene.String(required=True),
            'choice': graphene.List(graphene.String, required=True),
            'answer': graphene.Int(required=True)
        })
    )

    mutation_field["update_lesson_quiz"] = create_mutation_field("UpdateLessonQuiz",
        gql_models['lesson_quiz'],
        update_lesson_quiz_mutate,
        create_input_class('UpdateLessonQuizInput', {
            "id": graphene.ID(required=True),
            'question': graphene.String(),
            'choice': graphene.List(graphene.String),
            'answer': graphene.Int()
        }),
    )

    mutation_field["delete_lesson_quiz"] = create_mutation_field("DeleteLessonQuiz",
        gql_models['lesson_quiz'],
        delete_lesson_quiz_mutate,
        create_input_class('DeleteLessonQuizInput', {
            "id": graphene.ID(required=True)
        }),
    )

    return (query_field, mutation_field)