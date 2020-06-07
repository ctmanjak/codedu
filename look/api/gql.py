import os
import json
import falcon
import graphene
from urllib.parse import parse_qs

from look.hook.authmanager import validate_token

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
        result = await self.graphql_execute(req, res)
        image_info = req.context.get('image_info', None)
        
        if not result.errors:
            res.status = HTTP_200
            res.body = json.dumps(result.data)
        else:
            if image_info:
                if os.path.isfile(f"./{image_info['dir']}{image_info['name']}{image_info['ext']}"):
                    os.remove(f"./{image_info['dir']}{image_info['name']}{image_info['ext']}")

            # error = json.loads(result.errors[0].message)
            # if error['status'] == 401:
            #     raise HTTPUnauthorized(description=error)
            # else:
            #     raise HTTPBadRequest(description=error)
            print(result.errors[0].message if hasattr(result.errors[0], 'message') else result.errors[0].args[0])
            raise HTTPBadRequest(description=result.errors[0].message if hasattr(result.errors[0], 'message') else result.errors[0].args[0])
            # res.status = falcon.HTTP_400
            
            # tmp_error = []
            # for error in result.errors:
            #     tmp_error.append({
            #         'message': error.message,
            #         'locations': {
            #             'line': error.locations[0].line,
            #             'column': error.locations[0].column,
            #         },
            #     })
            # print(tmp_error)
            # res.body = json.dumps(tmp_error)