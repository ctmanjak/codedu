import os
import sys
import json
from hashlib import sha256

from falcon import HTTPBadRequest

if "pytest" in sys.modules:
    image_path = 'test/images/'
else: image_path = 'images/'

class RequetDataManager(object):
    allowed_image = ['image/png', 'image/jpeg']
    async def process_request(self, req, res):
        print(f"X-Forwarded-For: {req.headers.get('x-forwarded-for', None)}")
        print(req.content_type)
        print(req.headers)
        if req.content_type:
            if req.content_type.startswith('application/json'):
                try:
                    raw_json = await req.stream.read()
                except Exception:
                    message = 'Read Error'
                    raise HTTPBadRequest(description=message)
                if raw_json:
                    try:
                        print(raw_json)
                        req.context['data'] = json.loads(raw_json.decode('utf-8') if type(raw_json) == bytes else raw_json)
                    except (json.decoder.JSONDecodeError, UnicodeDecodeError):
                        raise HTTPBadRequest(description="JSON Decode Error")
            elif req.content_type.startswith('multipart/form-data'):
                media = await req.get_media()
                image = None
                if media:
                    try:
                        for part in media:
                            print(part.name, part.content_type)
                            if part.content_type.startswith('application/json'):
                                try:
                                    req.context['data'] = part.media
                                    print(req.context['data'])
                                except json.decoder.JSONDecodeError as e:
                                    raise HTTPBadRequest(description="JSON Decode Error")
                            elif part.name == 'image':
                                if part.content_type in self.allowed_image:
                                    image_info = {}
                                    image_info['data'] = part.data
                                    image_info['size'] = len(image_info['data'])
                                    if image_info['size'] <= 2097152:
                                        image_info["name"] = f"tmp_{sha256(part.filename.encode()).hexdigest()}"
                                        image_info["ext"] = f".{part.filename.split('.')[-1]}"
                                        image_info["dir"] = f"{image_path}/tmp/"
                                        i = 0
                                        while os.path.isfile(f"{image_info['dir']}{image_info['name']}{image_info['ext']}"):
                                            image_info["name"] = f"tmp_{sha256((part.filename+str(i)).encode()).hexdigest()}"
                                            i+=1

                                        if not os.path.isdir(f'{image_path}'): os.mkdir(f'{image_path}')
                                        if not os.path.isdir(f'{image_path}/tmp'): os.mkdir(f'{image_path}/tmp')
                                        with open(f"./{image_info['dir']}{image_info['name']}{image_info['ext']}", 'wb') as f:
                                            f.write(image_info['data'])
                                            
                                        req.context["image_info"] = image_info
                                    else:
                                        raise HTTPBadRequest(description="Max file size is 2MB")
                                else:
                                    raise HTTPBadRequest(description="Not allowed image type")
                            else: pass
                    except Exception as e:
                        print(e)
                else: pass
            else:
                req.context['data'] = {}
        
        print(res.body)