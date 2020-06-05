import jwt
import datetime

from look.config import Config

my_token = encoded_jwt = jwt.encode({
    'iat':datetime.datetime.utcnow(),
    'user_id':3,
    'email':"xptmxmek@naver.com",
    'admin':False,
    # 'exp':datetime.datetime.utcnow() + datetime.timedelta(seconds=30),
}, Config.SECRET_KEY, algorithm='HS256').decode()

others_token = encoded_jwt = jwt.encode({
    'iat':datetime.datetime.utcnow(),
    'user_id':2,
    'email':"test@gmail.com",
    'admin':False,
    # 'exp':datetime.datetime.utcnow() + datetime.timedelta(seconds=30),
}, Config.SECRET_KEY, algorithm='HS256').decode()

admin_token = encoded_jwt = jwt.encode({
    'iat':datetime.datetime.utcnow(),
    'user_id':1,
    'email':"admin@codedu.org",
    'admin':True,
    # 'exp':datetime.datetime.utcnow() + datetime.timedelta(seconds=30),
}, Config.SECRET_KEY, algorithm='HS256').decode()