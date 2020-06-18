import os
import re
import sys
import graphene

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

def create_filter_class(classname, db_model):
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
    class_field = {
        "Meta": type("Meta", (), meta_field),
    }

    return type(classname, (FilterSet,), class_field)

def create_node_class(classname, db_model, connection_field_factory):
    return type(classname, (SQLAlchemyObjectType,), {
        "Meta": type("Meta", (), {
            "model": db_model,
            "interfaces": (graphene.Node,),
            "connection_field_factory": connection_field_factory,
        }),
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
    if not os.path.isdir(f'{image_path}'): os.mkdir(f'{image_path}')
    if not os.path.isdir(f'{image_path}/{tablename}'): os.mkdir(f'{image_path}/{tablename}')
    instance_id = f"{instance.id:010}"
    for ext in ['.jpg', '.png']:
        if os.path.exists(f"./{image_path}/{tablename}/{instance_id}{ext}"):
            os.remove(f"./{image_path}/{tablename}/{instance_id}{ext}")
    if image_info:
        os.rename(f"./{image_info['dir']}{image_info['name']}{image_info['ext']}", f"./{image_path}/{tablename}/{instance_id}{image_info['ext']}")
        image_info['dir'] = f"{image_path}/{tablename}/"
        image_info['name'] = f"{instance_id}"

        instance.image = f"{image_info['dir']}{image_info['name']}{image_info['ext']}"

code_ext = {"python3":".py", "clang":".c"}

def code_handle(instance, code=None):
    code_path = f"{root_path}/codes"
    code_id = f"{instance.id:010}"
    if not os.path.isdir(f'{code_path}'): os.mkdir(f'{code_path}')
    if not os.path.isdir(f'{code_path}/{instance.lang}'): os.mkdir(f'{code_path}/{instance.lang}')
    if not os.path.isdir(f'{code_path}/{instance.lang}/{code_id}'): os.mkdir(f'{code_path}/{instance.lang}/{code_id}')
    
    full_path = f"{code_path}/{instance.lang}/{code_id}/main{code_ext[instance.lang]}"
    if code:
        with open(full_path, "w") as f:
            f.write(code)
    else:
        if os.path.exists(full_path):
            os.remove(full_path)

    instance.path = full_path

def validate_user_data(data):
    username_validation = re.match(r"^(?=.*[가-힣A-Za-z_$])[가-힣A-Za-z_\d]{5,32}$", data['username']) if 'username' in data else True
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
            raise CodeduExceptionHandler(HTTPBadRequest(description="Username must be at least 5 characters long and including at least one letter."))
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