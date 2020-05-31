import json
import graphene
from urllib.parse import parse_qs

from look.hook.authmanager import validate_token

from falcon import HTTP_200, before, HTTPBadRequest

class Collection(object):
    def __init__(self, search=False):
        self.search = search

    @before(validate_token, is_async=True)
    async def on_get(self, req, res):
        query, variables, operation_name = None, None, None
        if req.query_string:
            query_string = parse_qs(req.query_string)
            query = query_string['query'][0] if 'query' in query_string else None
            variables = json.loads(query_string['variables'][0]) if 'variables' in query_string else None
            operation_name = query_string['operationName'][0] if 'operationName' in query_string else None

        db_session = req.context['db_session']
        schema = req.context['schema']

        result = schema.execute(query, variables=variables, operation_name=operation_name, context_value={'session': db_session, 'search': self.search})
        
        if not result.errors:
            res.status = HTTP_200
            res.body = json.dumps(result.data)
        else: raise HTTPBadRequest(description=result.errors[0].args[0])

    async def on_post(self, req, res):
        db_session = req.context['db_session']
        schema = req.context['schema']
        data = req.context['data']

        query = data.get('query', None)
        variables = data.get('variables', None)
        operation_name = data.get('operation_name', None)

        result = schema.execute(query, variables=variables, operation_name=operation_name, context_value={'session': db_session})

        if not result.errors:
            res.status = HTTP_200
            res.body = json.dumps(result.data)
        else: raise HTTPBadRequest(description=result.errors[0].args[0])