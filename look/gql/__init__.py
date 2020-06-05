from .model import create_gql_models, gql_models
from .base import create_base_schema
from .auth import create_auth_schema
from .post import create_post_schema

create_gql_models()
print(gql_models)
__all__ = [
    "create_base_schema",
    "create_auth_schema",
    "create_post_schema",
    "create_gql_models",
    "gql_models",
]
