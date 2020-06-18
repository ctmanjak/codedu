import os
import time
import json
import falcon
import hmac
from hashlib import sha256
from cerberus import Validator
from requests_toolbelt import MultipartEncoder

from look.app import app
from look.config import Config

from . import client, my_token, others_token, admin_token

v = Validator()

def test_register(client):
    doc = {
        "Register": {
            "user": {
                "email": "pytestuser@email.com",
                "username": "pytestuser",
                "password": hmac.new(Config.SECRET_KEY.encode(), "pytestuser123!".encode(), sha256).hexdigest(),
            }
        },
        "Register2": {
            "user": {
                "email": "pytestuser2@email.com",
                "username": "pytestuser2",
                "password": hmac.new(Config.SECRET_KEY.encode(), "pytestuser2123!".encode(), sha256).hexdigest(),
            }
        }
    }

    body = {
        "query": '''
            mutation {
                Register: register(data: {username:"pytestuser", email:"pytestuser@email.com", password:"pytestuser123!"}) {
                    user {
                        email
                        username
                        password
                    }
                }
                Register2: register(data: {username:"pytestuser2", email:"pytestuser2@email.com", password:"pytestuser2123!"}) {
                    user {
                        email
                        username
                        password
                    }
                }
            }
        '''
    }

    response = client.simulate_post('/api/graphql', content_type='application/json', body=json.dumps(body))
    result_doc = json.loads(response.content.decode())

    assert result_doc == doc
    assert response.status == falcon.HTTP_OK

def test_login_with_valid_password(client):
    global my_token
    
    schema = {
        "Login": { "type": "dict", "schema": {
            "user": { "type": "dict", "schema": {
                "email": { "type": "string", "allowed": ["pytestuser@email.com"]},
                "password": { "type": "string", "allowed": [hmac.new(Config.SECRET_KEY.encode(), "pytestuser123!".encode(), sha256).hexdigest()]},
            }},
            "token": { "type": "string" }
        }},
        "Login2": { "type": "dict", "schema": {
            "user": { "type": "dict", "schema": {
                "email": { "type": "string", "allowed": ["pytestuser2@email.com"]},
                "password": { "type": "string", "allowed": [hmac.new(Config.SECRET_KEY.encode(), "pytestuser2123!".encode(), sha256).hexdigest()]},
            }},
            "token": { "type": "string" }
        }},
    }

    body = {
        "query": '''
            query {
                Login: login(data: {email:"pytestuser@email.com", password:"pytestuser123!"}) {
                    user {
                        email
                        password
                    }
                    token
                }
                Login2: login(data: {email:"pytestuser2@email.com", password:"pytestuser2123!"}) {
                    user {
                        email
                        password
                    }
                    token
                }
            }
        '''
    }

    response = client.simulate_post('/api/graphql', content_type='application/json', body=json.dumps(body))
    result_doc = json.loads(response.content.decode())
    my_token = result_doc["Login"]["token"]
    
    assert v.validate(result_doc, schema)
    assert response.status == falcon.HTTP_OK

def test_login_with_invalid_password(client):
    doc = {
        "title": "400 Bad Request",
        "description": "INVALID PASSWORD",
    }

    body = {
        "query": '''
            query {
                login(data: {email:"pytestuser@email.com", password:"pytestuser1234!"}) {
                    user {
                        email
                        password
                    }
                    token
                }
            }
        '''
    }

    response = client.simulate_post('/api/graphql', content_type='application/json', body=json.dumps(body))
    result_doc = json.loads(response.content.decode())

    assert result_doc == doc
    assert response.status == falcon.HTTP_400

def test_update_user_without_token(client):
    doc = {
        "title": "401 Unauthorized",
        "description": "토큰이 없는뎁쇼",
    }

    body = {
        "query": '''
            mutation {
                updateUserInfo(data: {username:"updateduser", password:"pytestuser2123!"}) {
                    user {
                        email
                        username
                        password
                    }
                }
            }
        '''
    }

    response = client.simulate_post('/api/graphql', content_type='application/json', body=json.dumps(body))
    result_doc = json.loads(response.content.decode())

    assert result_doc == doc
    assert response.status == falcon.HTTP_401

def test_update_user_with_invalid_token(client):
    doc = {
        "title": "400 Bad Request",
        "description": "INVALID PASSWORD",
    }

    body = {
        "query": '''
            mutation {
                updateUserInfo(data: {username:"updateduser", password:"pytestuser123!"}) {
                    user {
                        email
                        username
                        password
                    }
                }
            }
        '''
    }

    response = client.simulate_post('/api/graphql', content_type='application/json', body=json.dumps(body), headers={
        'Authorization': others_token
    })
    result_doc = json.loads(response.content.decode())

    assert result_doc == doc
    assert response.status == falcon.HTTP_400

def test_update_user_with_valid_token(client):
    doc = {
        "updateUserInfo": {
            "user": {
                "email": "pytestuser@email.com",
                "username": "updateduser",
                "password": hmac.new(Config.SECRET_KEY.encode(), "pytestuser123!".encode(), sha256).hexdigest(),
            }
        }
    }

    body = {
        "query": '''
            mutation {
                updateUserInfo(data: {username:"updateduser", password:"pytestuser123!"}) {
                    user {
                        email
                        username
                        password
                    }
                }
            }
        '''
    }
    response = client.simulate_post('/api/graphql', content_type='application/json', body=json.dumps(body), headers={
        'Authorization': my_token
    })
    result_doc = json.loads(response.content.decode())

    assert result_doc == doc
    assert response.status == falcon.HTTP_OK

def test_update_password_without_token(client):
    doc = {
        "title": "401 Unauthorized",
        "description": "토큰이 없는뎁쇼",
    }

    body = {
        "query": '''
            mutation {
                updatePassword(data: {newPassword:"updateduser123!", password:"pytestuser123!"}) {
                    user {
                        email
                        username
                        password
                    }
                }
            }
        '''
    }

    response = client.simulate_post('/api/graphql', content_type='application/json', body=json.dumps(body))
    result_doc = json.loads(response.content.decode())

    assert result_doc == doc
    assert response.status == falcon.HTTP_401

def test_update_password_with_invalid_token(client):
    doc = {
        "title": "400 Bad Request",
        "description": "INVALID PASSWORD",
    }

    body = {
        "query": '''
            mutation {
                updatePassword(data: {newPassword:"updateduser123!", password:"pytestuser123!"}) {
                    user {
                        email
                        username
                        password
                    }
                }
            }
        '''
    }

    response = client.simulate_post('/api/graphql', content_type='application/json', body=json.dumps(body), headers={
        'Authorization': others_token
    })
    result_doc = json.loads(response.content.decode())

    assert result_doc == doc
    assert response.status == falcon.HTTP_400

def test_update_password_with_valid_token(client):
    doc = {
        "updatePassword": {
            "user": {
                "email": "pytestuser@email.com",
                "username": "updateduser",
                "password": hmac.new(Config.SECRET_KEY.encode(), "updateduser123!".encode(), sha256).hexdigest(),
            }
        }
    }

    body = {
        "query": '''
            mutation {
                updatePassword(data: {newPassword:"updateduser123!", password:"pytestuser123!"}) {
                    user {
                        email
                        username
                        password
                    }
                }
            }
        '''
    }

    response = client.simulate_post('/api/graphql', content_type='application/json', body=json.dumps(body), headers={
        'Authorization': my_token
    })
    result_doc = json.loads(response.content.decode())

    assert result_doc == doc
    assert response.status == falcon.HTTP_OK

def test_delete_account_without_token(client):
    doc = {
        "title": "401 Unauthorized",
        "description": "토큰이 없는뎁쇼",
    }

    body = {
        "query": '''
            mutation {
                deleteAccount(data: {password:"updateduser123!"}) {
                    user {
                        email
                        username
                        password
                    }
                }
            }
        '''
    }

    response = client.simulate_post('/api/graphql', content_type='application/json', body=json.dumps(body))
    result_doc = json.loads(response.content.decode())

    assert result_doc == doc
    assert response.status == falcon.HTTP_401

def test_delete_account_with_invalid_token(client):
    doc = {
        "title": "400 Bad Request",
        "description": "INVALID PASSWORD",
    }

    body = {
        "query": '''
            mutation {
                deleteAccount(data: {password:"updateduser123!"}) {
                    user {
                        email
                        username
                        password
                    }
                }
            }
        '''
    }

    response = client.simulate_post('/api/graphql', content_type='application/json', body=json.dumps(body), headers={
        'Authorization': others_token
    })
    result_doc = json.loads(response.content.decode())

    assert result_doc == doc
    assert response.status == falcon.HTTP_400

def test_delete_account_with_valid_token(client):
    doc = {
        "deleteAccount": {
            "user": {
                "email": "pytestuser@email.com",
                "username": "updateduser",
                "password": hmac.new(Config.SECRET_KEY.encode(), "updateduser123!".encode(), sha256).hexdigest(),
            }
        }
    }

    body = {
        "query": '''
            mutation {
                deleteAccount(data: {password:"updateduser123!"}) {
                    user {
                        email
                        username
                        password
                    }
                }
            }
        '''
    }

    response = client.simulate_post('/api/graphql', content_type='application/json', body=json.dumps(body), headers={
        'Authorization': my_token
    })
    result_doc = json.loads(response.content.decode())

    assert result_doc == doc
    assert response.status == falcon.HTTP_OK

def test_update_user_by_admin(client):
    doc = {
        "updateUserInfo": {
            "user": {
                "email": "pytestuser2@email.com",
                "username": "updatedbyadmin",
                "password": hmac.new(Config.SECRET_KEY.encode(), "pytestuser2123!".encode(), sha256).hexdigest(),
            }
        }
    }

    body = {
        "query": '''
            mutation {
                updateUserInfo(data: {id: 8, username:"updatedbyadmin", password:"updatedbyadmin123!"}) {
                    user {
                        email
                        username
                        password
                    }
                }
            }
        '''
    }

    response = client.simulate_post('/api/graphql', content_type='application/json', body=json.dumps(body), headers={
        'Authorization': admin_token
    })
    result_doc = json.loads(response.content.decode())

    assert result_doc == doc
    assert response.status == falcon.HTTP_OK

def test_update_password_by_admin(client):
    doc = {
        "updatePassword": {
            "user": {
                "email": "pytestuser2@email.com",
                "username": "updatedbyadmin",
                "password": hmac.new(Config.SECRET_KEY.encode(), "updatedbyadmin123!".encode(), sha256).hexdigest(),
            }
        }
    }

    body = {
        "query": '''
            mutation {
                updatePassword(data: {id: 8, newPassword:"updatedbyadmin123!"}) {
                    user {
                        email
                        username
                        password
                    }
                }
            }
        '''
    }

    response = client.simulate_post('/api/graphql', content_type='application/json', body=json.dumps(body), headers={
        'Authorization': admin_token
    })
    result_doc = json.loads(response.content.decode())

    assert result_doc == doc
    assert response.status == falcon.HTTP_OK

def test_delete_account_by_admin(client):
    doc = {
        "deleteAccount": {
            "user": {
                "email": "pytestuser2@email.com",
                "username": "updatedbyadmin",
                "password": hmac.new(Config.SECRET_KEY.encode(), "updatedbyadmin123!".encode(), sha256).hexdigest(),
            }
        }
    }

    body = {
        "query": '''
            mutation {
                deleteAccount(data: {id: 8}) {
                    user {
                        email
                        username
                        password
                    }
                }
            }
        '''
    }

    response = client.simulate_post('/api/graphql', content_type='application/json', body=json.dumps(body), headers={
        'Authorization': admin_token
    })
    result_doc = json.loads(response.content.decode())

    assert result_doc == doc
    assert response.status == falcon.HTTP_OK

def test_register_with_not_allowed_image(client):
    doc = {
        "title": "400 Bad Request",
        "description": "Not allowed image type"
    }

    query = {
        "query": '''
            mutation {
                register(data: {username:"imagetestuser", email:"imagetestuser@email.com", password:"imagetestuser123!"}) {
                    user {
                        email
                        username
                        password
                    }
                }
            }
        '''
    }
    fake_image_byte = b"a" * (2 * 1024 * 1024)
    
    m = MultipartEncoder(
    fields={'data': ('data', json.dumps(query), 'application/json'),
            'image': ('a.gif', fake_image_byte, 'image/gif')}
    )
    
    response = client.simulate_post('/api/graphql', content_type=m.content_type, body=m.to_string())

    result_doc = json.loads(response.content.decode())

    assert result_doc == doc
    assert response.status == falcon.HTTP_400

def test_register_with_larger_than_2mb_image(client):
    doc = {
        "title": "400 Bad Request",
        "description": "Max file size is 2MB"
    }

    query = {
        "query": '''
            mutation {
                register(data: {username:"imagetestuser", email:"imagetestuser@email.com", password:"imagetestuser123!"}) {
                    user {
                        email
                        username
                        password
                    }
                }
            }
        '''
    }
    fake_image_byte = b"a" * (2 * 1024 * 1024 + 1)
    
    m = MultipartEncoder(
    fields={'data': ('data', json.dumps(query), 'application/json'),
            'image': ('a.png', fake_image_byte, 'image/png')}
    )
    
    response = client.simulate_post('/api/graphql', content_type=m.content_type, body=m.to_string())

    result_doc = json.loads(response.content.decode())

    assert result_doc == doc
    assert response.status == falcon.HTTP_400

def test_register_with_valid_image(client):
    doc = {
        "register": {
            "user": {
                "email": "imagetestuser@email.com",
                "username": "imagetestuser",
                "password": hmac.new(Config.SECRET_KEY.encode(), "imagetestuser123!".encode(), sha256).hexdigest(),
                "image": "images/user/0000000009.png"
            }
        }
    }

    query = {
        "query": '''
            mutation {
                register(data: {username:"imagetestuser", email:"imagetestuser@email.com", password:"imagetestuser123!"}) {
                    user {
                        email
                        username
                        password
                        image
                    }
                }
            }
        '''
    }
    fake_image_byte = b"a" * (2 * 1024 * 1024)
    
    m = MultipartEncoder(
    fields={'data': ('data', json.dumps(query), 'application/json'),
            'image': ('a.png', fake_image_byte, 'image/png')}
    )
    
    response = client.simulate_post('/api/graphql', content_type=m.content_type, body=m.to_string())

    result_doc = json.loads(response.content.decode() if type(response.content) == bytes else response)

    assert result_doc == doc
    assert response.status == falcon.HTTP_OK

    with open(f"test/{doc['register']['user']['image']}", 'rb') as f:
        assert f.read() == fake_image_byte

def test_register_with_invalid_email_1(client):
    doc = {
        "title": "400 Bad Request",
        "description": "INVALID EMAIL ADDRESS",
    }

    body = {
        "query": '''
            mutation {
                register(data: {username:"invaliduser", email:"invaliduser@@email.com", password:"invaliduser123!"}) {
                    user {
                        email
                        username
                        password
                        image
                    }
                }
            }
        '''
    }
    response = client.simulate_post('/api/graphql', content_type="application/json", body=json.dumps(body))

    result_doc = json.loads(response.content.decode() if type(response.content) == bytes else response)

    assert result_doc == doc
    assert response.status == falcon.HTTP_400

def test_register_with_invalid_email_2(client):
    doc = {
        "title": "400 Bad Request",
        "description": "INVALID EMAIL ADDRESS",
    }

    body = {
        "query": '''
            mutation {
                register(data: {username:"invaliduser", email:"invaliduseremail.com", password:"invaliduser123!"}) {
                    user {
                        email
                        username
                        password
                        image
                    }
                }
            }
        '''
    }
    response = client.simulate_post('/api/graphql', content_type="application/json", body=json.dumps(body))

    result_doc = json.loads(response.content.decode() if type(response.content) == bytes else response)

    assert result_doc == doc
    assert response.status == falcon.HTTP_400

def test_register_with_invalid_email_3(client):
    doc = {
        "title": "400 Bad Request",
        "description": "INVALID EMAIL ADDRESS",
    }

    body = {
        "query": '''
            mutation {
                register(data: {username:"invaliduser", email:"invaliduser@emailcom", password:"invaliduser123!"}) {
                    user {
                        email
                        username
                        password
                        image
                    }
                }
            }
        '''
    }
    response = client.simulate_post('/api/graphql', content_type="application/json", body=json.dumps(body))

    result_doc = json.loads(response.content.decode() if type(response.content) == bytes else response)

    assert result_doc == doc
    assert response.status == falcon.HTTP_400

def test_register_with_invalid_password_1(client):
    doc = {
        "title": "400 Bad Request",
        "description": "Password contains characters that cannot be included.",
    }

    body = {
        "query": '''
            mutation {
                register(data: {username:"invaliduser", email:"invaliduser@email.com", password:"aaaaaa1..."}) {
                    user {
                        email
                        username
                        password
                        image
                    }
                }
            }
        '''
    }
    response = client.simulate_post('/api/graphql', content_type="application/json", body=json.dumps(body))

    result_doc = json.loads(response.content.decode() if type(response.content) == bytes else response)

    assert result_doc == doc
    assert response.status == falcon.HTTP_400

def test_register_with_invalid_password_2(client):
    doc = {
        "title": "400 Bad Request",
        "description": "Password must be at least 8 characters long and including at least one letter and one number.",
    }

    body = {
        "query": '''
            mutation {
                register(data: {username:"invaliduser", email:"invaliduser@email.com", password:"aaaaaa1"}) {
                    user {
                        email
                        username
                        password
                        image
                    }
                }
            }
        '''
    }
    response = client.simulate_post('/api/graphql', content_type="application/json", body=json.dumps(body))

    result_doc = json.loads(response.content.decode() if type(response.content) == bytes else response)

    assert result_doc == doc
    assert response.status == falcon.HTTP_400

def test_register_with_invalid_password_3(client):
    doc = {
        "title": "400 Bad Request",
        "description": "Password must be at least 8 characters long and including at least one letter and one number.",
    }

    body = {
        "query": '''
            mutation {
                register(data: {username:"invaliduser", email:"invaliduser@email.com", password:"aaaaaaaaa"}) {
                    user {
                        email
                        username
                        password
                        image
                    }
                }
            }
        '''
    }
    response = client.simulate_post('/api/graphql', content_type="application/json", body=json.dumps(body))

    result_doc = json.loads(response.content.decode() if type(response.content) == bytes else response)

    assert result_doc == doc
    assert response.status == falcon.HTTP_400

def test_register_with_invalid_password_4(client):
    doc = {
        "title": "400 Bad Request",
        "description": "Password must be at least 8 characters long and including at least one letter and one number.",
    }

    body = {
        "query": '''
            mutation {
                register(data: {username:"invaliduser", email:"invaliduser@email.com", password:"123123123"}) {
                    user {
                        email
                        username
                        password
                        image
                    }
                }
            }
        '''
    }
    response = client.simulate_post('/api/graphql', content_type="application/json", body=json.dumps(body))

    result_doc = json.loads(response.content.decode() if type(response.content) == bytes else response)

    assert result_doc == doc
    assert response.status == falcon.HTTP_400

def test_register_with_invalid_password_5(client):
    doc = {
        "title": "400 Bad Request",
        "description": "Password must be at least 8 characters long and including at least one letter and one number.",
    }

    body = {
        "query": '''
            mutation {
                register(data: {username:"invaliduser", email:"invaliduser@email.com", password:"123123123!!!"}) {
                    user {
                        email
                        username
                        password
                        image
                    }
                }
            }
        '''
    }
    response = client.simulate_post('/api/graphql', content_type="application/json", body=json.dumps(body))

    result_doc = json.loads(response.content.decode() if type(response.content) == bytes else response)

    assert result_doc == doc
    assert response.status == falcon.HTTP_400

def test_register_with_invalid_username_1(client):
    doc = {
        "title": "400 Bad Request",
        "description": "Username must be at least 5 characters long and including at least one letter.",
    }

    body = {
        "query": '''
            mutation {
                register(data: {username:"inva", email:"invaliduser@email.com", password:"invaliduser123!"}) {
                    user {
                        email
                        username
                        password
                        image
                    }
                }
            }
        '''
    }
    response = client.simulate_post('/api/graphql', content_type="application/json", body=json.dumps(body))

    result_doc = json.loads(response.content.decode() if type(response.content) == bytes else response)

    assert result_doc == doc
    assert response.status == falcon.HTTP_400

def test_register_with_invalid_username_2(client):
    doc = {
        "title": "400 Bad Request",
        "description": "Username can only contain 한글, alphanumeric characters and underscore.",
    }

    body = {
        "query": '''
            mutation {
                register(data: {username:"invaliduser!", email:"invaliduser@email.com", password:"invaliduser123!"}) {
                    user {
                        email
                        username
                        password
                        image
                    }
                }
            }
        '''
    }
    response = client.simulate_post('/api/graphql', content_type="application/json", body=json.dumps(body))

    result_doc = json.loads(response.content.decode() if type(response.content) == bytes else response)

    assert result_doc == doc
    assert response.status == falcon.HTTP_400

def test_update_user_image(client):
    doc = {
        "updateUserInfo": {
            "user": {
                "image": "images/user/0000000009.png",
            }
        }
    }

    query = {
        "query": '''
            mutation {
                updateUserInfo(data: {id: 9}) {
                    user {
                        image
                    }
                }
            }
        '''
    }
    fake_image_byte = b"b" * (2 * 1024 * 1024)
    
    m = MultipartEncoder(
    fields={'data': ('data', json.dumps(query), 'application/json'),
            'image': ('a.png', fake_image_byte, 'image/png')}
    )
    
    response = client.simulate_post('/api/graphql', content_type=m.content_type, body=m.to_string(), headers={
        'Authorization': admin_token
    })

    result_doc = json.loads(response.content.decode() if type(response.content) == bytes else response)

    assert result_doc == doc
    assert response.status == falcon.HTTP_OK

    with open(f"test/{doc['updateUserInfo']['user']['image']}", 'rb') as f:
        assert f.read() == fake_image_byte

def test_delete_user_image(client):
    doc = {
        "deleteAccount": {
            "user": {
                "image": "images/user/0000000009.png",
            }
        }
    }

    body = {
        "query": '''
            mutation {
                deleteAccount(data: {id: 9}) {
                    user {
                        image
                    }
                }
            }
        '''
    }
    
    response = client.simulate_post('/api/graphql', content_type='application/json', body=json.dumps(body), headers={
        'Authorization': admin_token
    })
    result_doc = json.loads(response.content.decode())

    assert result_doc == doc
    assert response.status == falcon.HTTP_OK

    assert not os.path.exists(f"test/{doc['deleteAccount']['user']['image']}")