import graphene

from look.model import Base

from look.gql import create_gql_models, create_base_schema, create_auth_schema, create_post_schema, create_post_comment_schema, \
    create_code_schema, create_code_comment_schema, create_question_schema, create_answer_schema, create_subchapter_schema, \
    create_like_schema

def init_schema():
    print("init_schema")

    query_field = {}
    mutation_field = {}
    
    schemas = [
        create_base_schema,
        create_auth_schema,
        create_post_schema,
        create_post_comment_schema,
        create_code_schema,
        create_code_comment_schema,
        create_question_schema,
        create_answer_schema,
        create_subchapter_schema,
        create_like_schema,
        # create_post_like_schema,
    ]

    for schema in schemas:
        if not schema == create_like_schema:
            tmp_query_field, tmp_mutation_field = schema()

            query_field.update(tmp_query_field)
            mutation_field.update(tmp_mutation_field)
        else:
            for tablename in ['post', 'post_comment', 'question', 'answer', 'code', 'code_comment']:
                tmp_query_field, tmp_mutation_field = schema(tablename)

                query_field.update(tmp_query_field)
                mutation_field.update(tmp_mutation_field)

    Query = type("Query", (graphene.ObjectType,), query_field)
    Mutation = type("Mutation", (graphene.ObjectType,), mutation_field)
    return {'query': Query, 'mutation': Mutation}

schema = graphene.Schema(**init_schema())