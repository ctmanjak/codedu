import graphene

from look.exc.handler import CodeduExceptionHandler

from falcon import HTTPUnauthorized

from . import gql_models
from .util import create_input_class, create_mutation_field, get_instance_by_pk, check_row_by_user_id, \
    db_session_flush, image_handle, simple_create_mutate, simple_update_mutate, simple_delete_mutate

def create_post_comment_schema():
    query_field = {}
    mutation_field = {}

    mutation_field["create_post_comment"] = create_mutation_field("CreatePostComment",
        gql_models['post_comment'],
        simple_create_mutate,
        create_input_class('CreatePostCommentInput', {
            'post_id': graphene.ID(required=True),
            'content': graphene.String(required=True),
        })
    )

    mutation_field["update_post_comment"] = create_mutation_field("UpdatePostComment",
        gql_models['post_comment'],
        simple_update_mutate,
        create_input_class('UpdatePostCommentInput', {
            "id": graphene.ID(required=True),
            "content": graphene.String(required=True),
        }),
    )

    mutation_field["delete_post_comment"] = create_mutation_field("DeletePostComment",
        gql_models['post_comment'],
        simple_delete_mutate,
        create_input_class('DeletePostCommentInput', {
            "id": graphene.ID(required=True)
        }),
    )

    return (query_field, mutation_field)