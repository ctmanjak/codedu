import os
import re
import sys
import string
import secrets
import graphene

from hashlib import sha256

from traceback import print_exc

from look.exc.handler import CodeduExceptionHandler

from falcon import HTTPBadRequest, HTTPInternalServerError, HTTPUnauthorized

from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm.exc import NoResultFound

from graphql import GraphQLError
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType
from graphene_sqlalchemy_filter import FilterableConnectionField, FilterSet

if "pytest" in sys.modules:
    root_path = 'test'
else: root_path = 'nfs'

def create_gql_model_class(classname, db_model, fields={}, meta_fields={}):
    tablename = db_model.__table__.fullname
    meta_fields["model"] = db_model
    fields["Meta"] = type("Meta", (), meta_fields)
    return type(classname, (SQLAlchemyObjectType,), fields)

def get_instance_by_pk(query, db_model, data):
    primary_keys = [a for a in db_model.__table__.primary_key]
    instance = None
    
    find_pks = {}
    for pk in primary_keys:
        if pk.name in data:
            find_pks[pk.name] = data[pk.name]
            
    if find_pks:
        instance = query.filter_by(**find_pks)
        
    return instance

def create_input_class(classname, fields):
    return type(classname,
        (graphene.InputObjectType,),
        fields,
    )

def create_query_field(model, resolve_func, fields):
    return (
        graphene.List(model, **(dict(a for a in map(lambda x: (x[0], graphene.Argument(type(x[1]))), fields.items())))),
        lambda self, info, model=model, **kwargs: resolve_func(self, info, model, **kwargs),
    )
    
def create_mutation_field(classname, model, mutate_func, input_class, fields={}, input_fields={}):
    tablename = model._meta.model.__table__.fullname
    input_fields["data"] = input_class()
    fields["Arguments"] = type("Arguments", (), input_fields)
    fields[tablename] = graphene.Field(model)
    fields["mutate"] = classmethod(lambda cls, _, info, model=model, **kwargs: mutate_func(cls, info, model, **kwargs))
    
    return type(classname, (graphene.Mutation,), fields).Field()

def check_row_by_user_id(user_id, db_model, instance):
    if db_model.__table__.fullname == 'user':
        instance = instance.filter_by(id=user_id)
    elif 'user_id' in db_model.__table__.columns:
        instance = instance.filter_by(user_id=user_id)

    try:
        instance.one()
    except NoResultFound:
        return False

    return True

def create_connection_class(classname, model):
    return type(classname, (graphene.Connection,), {
        "Meta": type("Meta", (), {
            "node": model,
        }),
        "total_count": graphene.Int(),
        "resolve_total_count": lambda self, info, **kwargs: self.iterable.count(),
    })

def create_filter_class(classname, db_model, class_fields={}):
    fields = {}
    for colname, column in db_model.__table__.columns.items():
        if column.expression.foreign_keys or column.expression.primary_key:
            fields[colname] = ['eq', 'is_null']
        else:
            fields[colname] = [...]
    
    meta_field = {
        "model": db_model,
        "fields": fields,
    }
    class_fields["Meta"] = type("Meta", (), meta_field)

    return type(classname, (FilterSet,), class_fields)

def create_node_class(classname, db_model, connection_field_factory=None):
    meta_fields = {}
    meta_fields["model"] = db_model
    meta_fields["interfaces"] = (graphene.Node,)
    if connection_field_factory:
        meta_fields["connection_field_factory"] = connection_field_factory
    return type(classname, (SQLAlchemyObjectType,), {
        "Meta": type("Meta", (), meta_fields),
    })

def db_session_flush(db_session):
    try:
        db_session.flush()
    except IntegrityError:
        db_session.rollback()
        raise CodeduExceptionHandler(HTTPBadRequest(description="INTEGRITY ERROR"))
    except OperationalError:
        db_session.rollback()
        print_exc()
        raise CodeduExceptionHandler(HTTPBadRequest(description="OPERATIONAL ERROR"))
    except:
        db_session.rollback()
        print_exc()
        raise CodeduExceptionHandler(HTTPBadRequest(description="UNKNOWN ERROR"))

def image_handle(tablename, instance, image_info=None):
    image_path = f"{root_path}/images"
    if not image_info:
        if instance.image and os.path.exists(f"{root_path}/{instance.image}"):
            os.remove(f"{root_path}/{instance.image}")
            # os.rmdir(f"{root_path}/{'/'.join(instance.image.split('/')[:-1])}")
    elif type(image_info) == list:
        if tablename == "lesson":
            if not os.path.isdir(f'{image_path}'): os.mkdir(f'{image_path}')
            if not os.path.isdir(f'{image_path}/{tablename}'): os.mkdir(f'{image_path}/{tablename}')
            
            # if not instance.token:
            #     while True:
            #         token = make_token(12)
            #         if not os.path.isdir(f"{image_path}/{tablename}/{token}"):
            #             os.mkdir(f"{image_path}/{tablename}/{token}")
            #             break
            #     instance.token = token
            # else: token = instance.token
            file_path = f"{image_path}/{tablename}"
            token_path_list = []
            
            for image in image_info:
                while True:
                    token = make_token(12)
                    if not os.path.isfile(f"{file_path}/{token}{image['ext']}"): break
                token_path_list.append(f"{file_path}/{token}{image['ext']}")
                if not os.path.isdir(file_path): os.mkdir(file_path)
                os.rename(image['full_path'], token_path_list[-1])
                instance.content = re.sub(f"\[image={image['org_name']}\]", f"{'http://'+os.getenv('SERVER_IP')+'/'+token_path_list[-1][len(root_path)+1:]}", instance.content)
            return token_path_list
    else:
        instance_id = f"{instance.id:010}"
        if not os.path.isdir(f'{image_path}'): os.mkdir(f'{image_path}')
        if not os.path.isdir(f'{image_path}/{tablename}'): os.mkdir(f'{image_path}/{tablename}')

        if instance.image:
            if os.path.exists(f"{root_path}/{instance.image}"):
                os.remove(f"{root_path}/{instance.image}")

        while True:
            token = make_token(12)
            if not os.path.isfile(f"{image_path}/{tablename}/{token}{image_info['ext']}"): break
        token_path = f"{image_path}/{tablename}/{token}{image_info['ext']}"

        os.rename(image_info['full_path'], token_path)
        instance.image = token_path[len(root_path)+1:]

        return token_path

code_ext = {"python3":".py", "clang":".c"}

def make_token(length):
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(length))

def make_token_path(file_path, instance_id, length=12):
    while True:
        tmp_token = make_token(length)
        token_path = file_path.replace(instance_id, tmp_token)
        if not os.path.isdir(token_path): break

    return token_path

def code_handle(instance, code=None):
    if not code:
        if instance.path and os.path.exists(f"{root_path}/{instance.path}"):
            os.remove(f"{root_path}/{instance.path}")
            os.rmdir(f"{root_path}/{'/'.join(instance.path.split('/')[:-1])}")
    else:
        code_path = f"{root_path}/codes"
    
        if not os.path.isdir(f'{code_path}'): os.mkdir(f'{code_path}')
        if not os.path.isdir(f'{code_path}/{instance.lang}'): os.mkdir(f'{code_path}/{instance.lang}')

        while True:
            token = make_token(12)
            if not os.path.isdir(f"{code_path}/{instance.lang}/{token}"):
                os.mkdir(f"{code_path}/{instance.lang}/{token}")
                break
        token_path = f"{code_path}/{instance.lang}/{token}/main{code_ext[instance.lang]}"

        with open(token_path, "w") as f:
            f.write(code)
        
        instance.path = token_path[len(root_path)+1:]

def validate_user_data(data):
    username_validation = re.match(r"^(?=.*[가-힣A-Za-z_$])[가-힣A-Za-z_\d]{2,32}$", data['username']) if 'username' in data else True
    password_validation = re.match(r"^(?=.*[A-Za-z$])(?=.*\d)[A-Za-z@$!%*#?&\d]{8,}$", data['password']) if 'password' in data else True
    email_validation = re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", data['email']) if 'email' in data else True
    if not email_validation:
        raise CodeduExceptionHandler(HTTPBadRequest(description="INVALID EMAIL ADDRESS"))
    if not username_validation:
        # 포함하면 안 되는 문자 있는지 체크
        username_validation_2 = re.search(r"[^가-힣A-Za-z_\d]+", data['username'])
        if username_validation_2:
            raise CodeduExceptionHandler(HTTPBadRequest(description="Username can only contain 한글, alphanumeric characters and underscore."))
        else:
            raise CodeduExceptionHandler(HTTPBadRequest(description="Username must be at least 2 characters long and including at least one letter."))
    if not password_validation:
        # 포함하면 안 되는 문자 있는지 체크
        password_validation_2 = re.search(r"[^A-Za-z@$!%*#?&\d]+", data['password'])
        if password_validation_2:
            raise CodeduExceptionHandler(HTTPBadRequest(description="Password contains characters that cannot be included."))
        else:
            raise CodeduExceptionHandler(HTTPBadRequest(description="Password must be at least 8 characters long and including at least one letter and one number."))


def simple_create_mutate(cls, info, model=None, **kwargs):
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

def simple_update_mutate(cls, info, model=None, **kwargs):
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

def simple_delete_mutate(cls, info, model=None, **kwargs):
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

def simple_update_view_mutate(cls, info, model=None, **kwargs):
    if info.context['auth']['data']:
        query = model.get_query(info)
        model = model._meta.model
        data = kwargs.get('data', None)
        image_info = info.context.get('image_info', None)
        if data:
            instance = get_instance_by_pk(query, model, data)
            data = {"view": instance.one().view + 1}
            instance.update(data)
            return cls(**{model.__tablename__:instance.one()})
    else:
        raise CodeduExceptionHandler(HTTPUnauthorized(description=info.context['auth']['description']))