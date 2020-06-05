from sqlalchemy.orm.exc import NoResultFound

import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType
from graphene_sqlalchemy_filter import FilterableConnectionField, FilterSet

def create_gql_model_class(classname, db_model, fields={}, meta_fields={}):
    tablename = db_model.__table__.fullname
    meta_fields["model"] = db_model
    fields["Meta"] = type("Meta", (), meta_fields)
    return type(classname, (SQLAlchemyObjectType,), fields)

def get_instance_by_pk(query, db_model, data):
    primary_keys = [a for a in db_model.__table__.primary_key]

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
    fields = {key:[...] for key in db_model.__table__.columns.keys()}

    return type(classname, (FilterSet,), {
        "Meta": type("Meta", (), {
            "model": db_model,
            "fields": fields,
        }),
    })

def create_node_class(classname, db_model, connection_field_factory):
    return type(classname, (SQLAlchemyObjectType,), {
        "Meta": type("Meta", (), {
            "model": db_model._meta.model,
            "interfaces": (graphene.Node,),
            "connection_field_factory": connection_field_factory,
        }),
    })