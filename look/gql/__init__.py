from .model import create_gql_models, gql_models
from .base import create_base_schema
from .auth import create_auth_schema
from .post import create_post_schema
from .post_comment import create_post_comment_schema
from .code import create_code_schema, create_code_comment_schema
from .qna import create_question_schema, create_answer_schema
from .subchapter import create_subchapter_schema
from .like import create_like_schema

create_gql_models()
print(gql_models)
__all__ = [
    "create_base_schema",
    "create_auth_schema",
    "create_post_schema",
    "create_gql_models",
    "create_post_comment_schema",
    "create_code_schema",
    "create_code_comment_schema",
    "create_question_schema",
    "create_answer_schema",
    "create_subchapter_schema",
    "create_like_schema",
    "gql_models",
]
