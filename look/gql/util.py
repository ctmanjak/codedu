import graphene

from graphene_sqlalchemy import SQLAlchemyObjectType

def create_gql_model(classname, model, fields={}, meta_fields={}):
    tablename = model.__table__.fullname
    meta_fields["model"] = model
    fields["Meta"] = type("Meta", (), meta_fields)
    return type(classname, (SQLAlchemyObjectType,), fields)

def get_instance_by_pk(query, model, data):
    primary_keys = [a for a in model.__table__.primary_key]

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