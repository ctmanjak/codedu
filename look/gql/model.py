from .util import create_gql_model_class
from look.model.base import Base

gql_models = {}

def create_gql_models():
    for model in Base._decl_class_registry.values():
        if hasattr(model, '__table__'):
            tablename = model.__table__.fullname
            gql_models[tablename] = create_gql_model_class(tablename, model)
