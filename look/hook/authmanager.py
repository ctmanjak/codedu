import jwt

from jwt.exceptions import InvalidSignatureError, ExpiredSignatureError

from look.config import Config

from falcon import HTTP_403, HTTPUnauthorized

async def validate_token(req, res, resource, params):
    if 'authorization' in req.headers:
        try:
            decoded_token = jwt.decode(req.headers['authorization'], Config.SECRET_KEY, algorithms='HS256')
        except ExpiredSignatureError:
            raise HTTPUnauthorized(description="만료된 토큰임 ㅋ;")
        except:
            raise HTTPUnauthorized(description="잘못된 토큰임 ㅋㅋ")
        else:
            req.context['auth'] = {
                'success':True,
                'description':'OK',
                'data':decoded_token,
            }
    else:
        raise HTTPUnauthorized(description="토큰이 없는뎁쇼")