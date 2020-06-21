import os
import json
import falcon
import graphene
from traceback import print_exc
from urllib.parse import parse_qs

from look.hook.authmanager import validate_token
from look.exc.handler import CodeduExceptionHandler

from falcon import HTTP_200, before, HTTPBadRequest, HTTPUnauthorized

class Collection(object):
    async def graphql_execute(self, req, res):
        db_session = req.context.get('db_session', None)
        schema = req.context.get('schema', None)
        data = req.context.get('data', {})
        auth = req.context.get('auth', {})
        image_info = req.context.get('image_info', None)

        query = data.get('query', None)
        variables = data.get('variables', None)
        operation_name = data.get('operation_name', None)

        result = schema.execute(query, variable_values=variables, operation_name=operation_name, context_value={'session': db_session, 'auth': auth, 'image_info': image_info})
        
        return result

    @before(validate_token, is_async=True)
    async def on_post(self, req, res):
        try:
            result = await self.graphql_execute(req, res)
            image_info = req.context.get('image_info', None)
            
            if not result.errors:
                res.status = HTTP_200
                res.body = json.dumps(result.data)
            else:
                if image_info:
                    for image in image_info:
                        if os.path.isfile(image['full_path']):
                            os.remove(image['full_path'])

                raise CodeduExceptionHandler(result.errors[0].args[0])
                print(result.errors)
        except Exception as e:
            description = e.description if hasattr(e, 'description') else 'UNKNOWN ERROR'
            if hasattr(e, 'type'):
                raise globals()[e.type](description=description)
            else:
                print_exc()
                raise HTTPBadRequest(description=e.args)