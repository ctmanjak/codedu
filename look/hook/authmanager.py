import jwt

from jwt.exceptions import InvalidSignatureError, ExpiredSignatureError

from look.config import Config

from falcon import HTTPUnauthorized

async def validate_token(req, res, resource, params):
    tmp_auth = {
        'success':False,
        'description':'OK',
        'data':"",
    }

    if 'authorization' in req.headers:
        try:
            decoded_token = jwt.decode(req.headers['authorization'], Config.SECRET_KEY, algorithms='HS256')
        except ExpiredSignatureError:
            tmp_auth['description'] = "만료된 토큰임 ㅋ;"
        except:
            tmp_auth['description'] = "잘못된 토큰임 ㅋㅋ"
        else:
            tmp_auth['success'] = True
            tmp_auth['data'] = decoded_token
    else:
        tmp_auth['description'] = "토큰이 없는뎁쇼"
        # raise HTTPUnauthorized(description="토큰이 없는뎁쇼")

    req.context['auth'] = tmp_auth