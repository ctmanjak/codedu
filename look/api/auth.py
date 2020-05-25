import json
import jwt
import datetime

from hashlib import sha256

from look.config import Config
from look.api import db
from look.model.user import User
from look.hook.authmanager import validate_token

from sqlalchemy.orm.exc import NoResultFound

from falcon import HTTP_200, before, HTTPBadRequest, HTTPMethodNotAllowed

class Check(object):
    @before(validate_token, is_async=True)
    async def on_post(self, req, res):
        res.body = json.dumps(req.context['auth'])
        pass

class Register(db.Collection):
    async def on_get(self, req, res):
        raise HTTPMethodNotAllowed(['POST'])
        
    async def on_post(self, req, res):
        if req.context["data"] and "password" in req.context["data"]:
            req.context["data"]["password"] = sha256(req.context["data"]["password"].encode()).hexdigest()
        await super().on_post(req, res, 'user')

class Login(object):
    async def on_post(self, req, res):
        data = req.context['data']
        db_session = req.context['db_session']
        try:
            db_data = db_session.query(User.password).filter(User.username == data['username']).one()
        except NoResultFound:
            raise HTTPBadRequest(description="USERNAME NOT FOUND")
        else:
            if db_data.password == data['password']:
                encoded_jwt = jwt.encode({
                    'username':data['username'],
                    'iat':datetime.datetime.utcnow(),
                    # 'exp':datetime.datetime.utcnow() + datetime.timedelta(seconds=30),
                }, Config.SECRET_KEY, algorithm='HS256')
                
                res.status = HTTP_200
                res.body = json.dumps({
                    'success' : True,
                    'description' : '',
                    'data' : {
                        'token':encoded_jwt.decode(),
                    },
                })
            else:
                raise HTTPBadRequest(description="INVALID PASSWORD")