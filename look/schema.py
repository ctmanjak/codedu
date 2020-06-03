import graphene

from look.model import Base

from look.gql import create_base_schema, create_auth_schema, create_post_schema

def init_schema():
    print("init_schema")

    query_field = {}
    mutation_field = {}
    
    schemas = [
        create_base_schema,
        create_auth_schema,
        create_post_schema,
    ]

    for schema in schemas:
        tmp_query_field, tmp_mutation_field = schema()

        query_field.update(tmp_query_field)
        mutation_field.update(tmp_mutation_field)

    mutation_field["register"] = mutation_field["create_user"]

    Query = type("Query", (graphene.ObjectType,), query_field)
    Mutation = type("Mutation", (graphene.ObjectType,), mutation_field)
    return {'query': Query, 'mutation': Mutation}

schema = graphene.Schema(**init_schema())