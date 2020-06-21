import os
import sys
import json
from hashlib import sha256

from look.exc.handler import CodeduExceptionHandler

from falcon import HTTPBadRequest

if "pytest" in sys.modules:
    root_path = 'test'
else: root_path = 'nfs'

class RequetDataManager(object):
        allowed_image = ['image/png', 'image/jpeg']
        async def process_request(self, req, res):
            try:
                print(f"X-Forwarded-For: {req.headers.get('x-forwarded-for', None)}")
                if req.content_type:
                    if req.content_type.startswith('application/json'):
                        try:
                            raw_json = await req.stream.read()
                        except Exception:
                            message = 'Read Error'
                            raise CodeduExceptionHandler(HTTPBadRequest(description=message))
                        if raw_json:
                            try:
                                print(raw_json)
                                req.context['data'] = json.loads(raw_json.decode('utf-8') if type(raw_json) == bytes else raw_json)
                            except (json.decoder.JSONDecodeError, UnicodeDecodeError):
                                raise CodeduExceptionHandler(HTTPBadRequest(description="JSON Decode Error"))
                    elif req.content_type.startswith('multipart/form-data'):
                        media = await req.get_media()
                        image = None
                        if media:
                            image_info = []
                            for part in media:
                                if part.name == 'data' and part.content_type.startswith('application/json'):
                                    try:
                                        req.context['data'] = part.media
                                    except json.decoder.JSONDecodeError as e:
                                        raise CodeduExceptionHandler(HTTPBadRequest(description="JSON Decode Error"))
                                elif part.name == 'image':
                                    if part.content_type in self.allowed_image:
                                        image_num = len(image_info)
                                        image_info.append({})
                                        image_data = part.data
                                        # image_info[image_num]['data'] = part.data
                                        image_info[image_num]['size'] = len(image_data)
                                        if image_info[image_num]['size'] <= 2097152:
                                            if not os.path.isdir(root_path): os.mkdir(root_path)
                                            image_path = f"{root_path}/images"
                                            image_info[image_num]["org_name"] = part.filename
                                            image_info[image_num]["name"] = f"tmp_{sha256(part.filename.encode()).hexdigest()}"
                                            image_info[image_num]["ext"] = f".{part.filename.split('.')[-1]}"
                                            image_info[image_num]["dir"] = f"{image_path}/tmp/"
                                            i = 0
                                            while os.path.isfile(f"{image_info[image_num]['dir']}{image_info[image_num]['name']}{image_info[image_num]['ext']}"):
                                                image_info[image_num]["name"] = f"tmp_{sha256((part.filename+str(i)).encode()).hexdigest()}"
                                                i+=1

                                            if not os.path.isdir(f'{image_path}'): os.mkdir(f'{image_path}')
                                            if not os.path.isdir(f'{image_path}/tmp'): os.mkdir(f'{image_path}/tmp')
                                            with open(f"./{image_info[image_num]['dir']}{image_info[image_num]['name']}{image_info[image_num]['ext']}", 'wb') as f:
                                                f.write(image_data)
                                            image_info[image_num]["full_path"] = f"{image_info[image_num]['dir']}{image_info[image_num]['name']}{image_info[image_num]['ext']}"
                                        else:
                                            raise CodeduExceptionHandler(HTTPBadRequest(description="Max file size is 2MB"))
                                    else:
                                        raise CodeduExceptionHandler(HTTPBadRequest(description="Not allowed image type"))
                                else: pass
                            req.context["image_info"] = image_info
                        else: pass
                    else:
                        req.context['data'] = {}
            except Exception as e:
                description = e.description if hasattr(e, 'description') else 'UNKNOWN ERROR'
                if hasattr(e, 'type'):
                    raise globals()[e.type](description=description)
                else:
                    raise HTTPBadRequest(description=e.args)