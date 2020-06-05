import jwt
import json
import graphene
import datetime
import hmac
from hashlib import sha256

from look.config import Config

from sqlalchemy.orm.exc import NoResultFound

from graphene_sqlalchemy.converter import convert_sqlalchemy_type

from . import gql_models
from .util import create_input_class, create_mutation_field, get_instance_by_pk, check_row_by_user_id

def create_auth_schema():
    def login_mutate(cls, info, model=None, **kwargs):
        query = model.get_query(info)
        model = model._meta.model
        data = kwargs.get('data', {})

        if 'email' in data and 'password' in data:
            try:
                user = query.filter(model.email == data['email']).one()
            except NoResultFound:
                raise Exception("USER NOT FOUND")

            if user.password == hmac.new(Config.SECRET_KEY.encode(), data['password'].encode(), sha256).hexdigest():
                encoded_jwt = jwt.encode({
                    'iat':datetime.datetime.utcnow(),
                    'user_id':user.id,
                    'email':data['email'],
                    'admin':user.admin,
                    # 'exp':datetime.datetime.utcnow() + datetime.timedelta(seconds=30),
                }, Config.SECRET_KEY, algorithm='HS256')

                return cls(**{'user':user, 'token': encoded_jwt.decode()})
            else: raise Exception("INVALID PASSWORD")
        else: raise Exception("INVALID PARAMETER")

    def register_mutate(cls, info, model=None, **kwargs):
        model = model._meta.model
        data = kwargs.get('data', None)
        if data:
            data['password'] = hmac.new(Config.SECRET_KEY.encode(), data['password'].encode(), sha256).hexdigest()
            db_session = info.context.get('session', None)
            if db_session:
                instance = model(**data)
                db_session.add(instance)

            return cls(**{model.__tablename__:instance})

    def update_user_info_mutate(cls, info, model=None, **kwargs):
        if info.context['auth']['data']:
            query = model.get_query(info)
            model = model._meta.model
            data = kwargs.get('data', None)
            if data:
                if not info.context['auth']['data']['admin']:
                    data['id'] = info.context['auth']['data']['user_id']
                    data['password'] = hmac.new(Config.SECRET_KEY.encode(), data['password'].encode(), sha256).hexdigest()
                else:
                    if 'password' in data: del data['password']
                    
                instance = get_instance_by_pk(query, model, data)
                
                if info.context['auth']['data']['admin'] or instance.one().password == data['password']:
                    instance.update(data)
                    return cls(**{model.__tablename__:instance.one()})
                else:
                    raise Exception("INVALID PASSWORD")
        else:
            # raise Exception(json.dumps({'status':401, 'description':info.context['auth']['description']}))
            raise Exception(info.context['auth']['description'])

    def update_password_mutate(cls, info, model=None, **kwargs):
        if info.context['auth']['data']:
            query = model.get_query(info)
            model = model._meta.model
            data = kwargs.get('data', None)
            if data:
                if not info.context['auth']['data']['admin']: data['id'] = info.context['auth']['data']['user_id']
                data["password_modified"] = datetime.datetime.utcnow()
                data['password'] = hmac.new(Config.SECRET_KEY.encode(), data['password'].encode(), sha256).hexdigest()
                
                instance = get_instance_by_pk(query, model, data)

                if info.context['auth']['data']['admin'] or instance.one().password == data['password']:
                    data['password'] = hmac.new(Config.SECRET_KEY.encode(), data['new_password'].encode(), sha256).hexdigest()
                    del data['new_password']
                    instance.update(data)
                    return cls(**{model.__tablename__:instance.one()})
                else:
                    raise Exception('INVALID PASSWORD')
        else:
            raise Exception(info.context['auth']['description'])

    def delete_account_mutate(cls, info, model=None, **kwargs):
        if info.context['auth']['data']:
            query = model.get_query(info)
            model = model._meta.model
            data = kwargs.get('data', None)
            if data:
                if not info.context['auth']['data']['admin']:
                    data['id'] = info.context['auth']['data']['user_id']
                    data['password'] = hmac.new(Config.SECRET_KEY.encode(), data['password'].encode(), sha256).hexdigest()
                    
                instance = get_instance_by_pk(query, model, data)

                if info.context['auth']['data']['admin'] or instance.one().password == data['password']:
                    tmp_instance = instance.one()
                    instance.delete()
                    return cls(**{model.__tablename__:tmp_instance})
                else:
                    raise Exception('INVALID PASSWORD')
        else:
            raise Exception(info.context['auth']['description'])
    
    query_field = {}
    mutation_field = {}

    query_field["login"] = create_mutation_field("Login",
        gql_models['user'],
        login_mutate,
        create_input_class('LoginInput', {
            'email': graphene.String(required=True),
            'password': graphene.String(required=True),
        }),
        {
            'token': graphene.String(),
        }
    )

    mutation_field["register"] = create_mutation_field("Register",
        gql_models['user'],
        register_mutate,
        create_input_class('RegisterInput', {
            'username': graphene.String(required=True),
            'email': graphene.String(required=True),
            'password': graphene.String(required=True),
            'admin': graphene.Boolean(),
        }),
    )

    fields = {}
    for colname, column in gql_models['user']._meta.model.__table__.columns.items():
            if not colname in ['created', 'modified', 'email']:
                fields[colname] = convert_sqlalchemy_type(getattr(column, 'type', None), column)()

    mutation_field["update_user_info"] = create_mutation_field("UpdateUserInfo",
        gql_models['user'],
        update_user_info_mutate,
        create_input_class('UpdateUserInfoInput', fields),
    )

    mutation_field["update_password"] = create_mutation_field("UpdatePassword",
        gql_models['user'],
        update_password_mutate,
        create_input_class('UpdatePasswordInput', {
            'password': graphene.String(),
            'new_password': graphene.String(required=True),
            'id': graphene.ID(),
        }),
    )
    mutation_field["delete_account"] = create_mutation_field("DeleteAccount",
        gql_models['user'],
        delete_account_mutate,
        create_input_class('DeleteAccountInput', {
            'password': graphene.String(),
            'id': graphene.ID(),
        }),
    )

    return (query_field, mutation_field)