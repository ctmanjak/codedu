import json
import graphene
from urllib.parse import parse_qs

from look.hook.authmanager import validate_token

from falcon import HTTP_200, before, HTTPBadRequest

class Collection(object):
    def __init__(self, search=False):
        self.search = search

    async def graphql_execute(self, req, res):
        db_session = req.context.get('db_session', None)
        schema = req.context.get('schema', None)
        data = req.context.get('data', {})
        auth = req.context.get('auth', {})

        query = data.get('query', None)
        variables = data.get('variables', None)
        operation_name = data.get('operation_name', None)

        result = schema.execute(query, variables=variables, operation_name=operation_name, context_value={'session': db_session, 'auth': auth, 'search': self.search})
        
        return result

    @before(validate_token, is_async=True)
    async def on_post(self, req, res):
        result = await self.graphql_execute(req, res)
        
        if not result.errors:
            res.status = HTTP_200
            res.body = json.dumps(result.data)
        else: raise HTTPBadRequest(description=result.errors[0].args[0])