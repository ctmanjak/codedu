import json
from falcon import HTTPBadRequest

class JSONTranslator(object):
    async def process_request(self, req, res):
        if req.content_type == 'application/json':
            try:
                raw_json = await req.stream.read()
            except Exception:
                message = 'Read Error'
                raise HTTPBadRequest(description=message)
            if raw_json:
                try:
                    req.context['data'] = json.loads(raw_json.decode('utf-8'))
                except json.decoder.JSONDecodeError as e:
                    raise HTTPBadRequest(description="JSON Decode Error")
        else:
            req.context['data'] = None