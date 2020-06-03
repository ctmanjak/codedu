import jwt
import graphene
import datetime
import hmac
from hashlib import sha256

from look.config import Config
from look.model import User

from falcon import HTTPBadRequest

from sqlalchemy.orm.exc import NoResultFound

from .util import create_gql_model, create_query_field, create_input_class, create_mutation_field

def create_auth_schema():
    def login_mutate(cls, info, model=None, **kwargs):
        query = model.get_query(info)
        model = model._meta.model
        data = kwargs.get('data', {})

        if 'username' in data and 'password' in data:
            try:
                user = query.filter(model.username == data['username']).one()
            except NoResultFound:
                raise Exception("USER NOT FOUND")

            if user.password == hmac.new(Config.SECRET_KEY.encode(), data['password'].encode(), sha256).hexdigest():
                encoded_jwt = jwt.encode({
                    'iat':datetime.datetime.utcnow(),
                    'user_id':user.id,
                    'username':data['username'],
                    'admin':user.admin,
                    # 'exp':datetime.datetime.utcnow() + datetime.timedelta(seconds=30),
                }, Config.SECRET_KEY, algorithm='HS256')

                return cls(**{'user':user, 'token': encoded_jwt.decode()})
            else: raise Exception("INVALID PASSWORD")
        else: raise Exception("INVALID PARAMETER")

    query_field = {}
    mutation_field = {}

    query_field["login"] = create_mutation_field("Login",
        create_gql_model("login", User),
        login_mutate,
        create_input_class('LoginInput', {
            'username': graphene.String(),
            'password': graphene.String(),
        }),
        {
            'token': graphene.String(),
        }
    )

    return (query_field, mutation_field)