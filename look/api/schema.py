import json
import graphene
from collections import OrderedDict

from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField

from look.model import Base
from look.model import User as UserModel

def init_schema():
    models = {}
    print("init_schema")

    for model in Base._decl_class_registry.values():
        if hasattr(model, '__tablename__'):
            # tablename = model.__tablename__[0].upper()+model.__tablename__[1:]
            tablename = model.__tablename__
            models[tablename] = type(tablename, (SQLAlchemyObjectType,), {
                "Meta": type("Meta", (), {
                    "model": model,
                    "interfaces": (relay.Node,),
                }),
            })

    query_attr = {"node":relay.Node.Field()}

    def resolve_model(self, info, model, depth=0, print_parent=False, **kwargs):
        return [row.get_data([], depth=depth, print_parent=print_parent) for row in model.get_query(info).all()]
        # return model.get_query(info).all()

    for tablename, model in models.items():
        query_attr[tablename] = graphene.List(model)
        query_attr[f"resolve_{tablename}"] = lambda self, info, model=model, **kwargs: resolve_model(self, info, model, **kwargs)
        query_attr[f"all_{tablename}"] = SQLAlchemyConnectionField(model.connection)

    Query = type("Query", (graphene.ObjectType,), query_attr)
    return models, Query

class Collection(object):
    async def on_get(self, req, res):
        query = '''
            {
                user {
                    id
                    username
                    password
                }
            }
        '''
        db_session = req.context['db_session']
        
        models, Query = init_schema()
        schema = graphene.Schema(query=Query)
        result = schema.execute(query, context_value={'session': db_session})
        # print(result.data)
        res.body = json.dumps(result.data)