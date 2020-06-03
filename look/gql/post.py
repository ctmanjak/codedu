import jwt
import graphene
import datetime
import hmac
from hashlib import sha256

from look.config import Config
from look.model import Post

from falcon import HTTPBadRequest

from sqlalchemy.orm.exc import NoResultFound

from .util import create_gql_model, create_query_field, create_input_class, create_mutation_field

def create_post_schema():
    def create_post(cls, info, model=None, **kwargs):
        if info.context['auth']['data']:
            model = model._meta.model
            data = kwargs.get('data', None)
            if data:
                data['user_id'] = info.context['auth']['data']['user_id']
                db_session = info.context.get('session', None)
                if db_session:
                    instance = model(**data)
                    db_session.add(instance)

                return cls(**{model.__tablename__:instance})
        else:
            raise Exception(info.context['auth']['description'])

    query_field = {}
    mutation_field = {}

    mutation_field["create_post"] = create_mutation_field("CreatePost",
        create_gql_model("createpost", Post),
        create_post,
        create_input_class('createpostInput', {
            'content': graphene.String(),
        })
    )

    return (query_field, mutation_field)