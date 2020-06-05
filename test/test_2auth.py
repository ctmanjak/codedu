import time
import json
import falcon
import hmac
from hashlib import sha256
from cerberus import Validator

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
        "title": "400 Bad Request",
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
    assert response.status == falcon.HTTP_400

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
        "title": "400 Bad Request",
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
    assert response.status == falcon.HTTP_400

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
        "title": "400 Bad Request",
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
    assert response.status == falcon.HTTP_400

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