import os
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

def test_create_code_without_token(client):
    doc = {
        "title": "401 Unauthorized",
        "description": "토큰이 없는뎁쇼",
    }

    body = {
        "query": '''
            mutation ($code: String!){
                createCode(data: {title:"pytest_code-1", lang:"python3", code:$code}) {
                    code {
                        title
                    }
                }
            }
        ''',
        "variables": {
            "code": "testcode",
        },
    }

    response = client.simulate_post('/api/graphql', content_type='application/json', body=json.dumps(body))
    result_doc = json.loads(response.content.decode())

    assert result_doc == doc
    assert response.status == falcon.HTTP_401

def test_create_code_with_token(client):
    doc = {
        "CreateCode1": {
            "code": {
                "title": "pytest_code-1",
                "lang": "python3",
                "path": "test/codes/python3/0000000001/main.py",
            }
        },
        "CreateCode2": {
            "code": {
                "title": "pytest_code-2",
                "lang": "python3",
                "path": "test/codes/python3/0000000002/main.py",
            }
        },
        "CreateCode3": {
            "code": {
                "title": "pytest_code-3",
                "lang": "python3",
                "path": "test/codes/python3/0000000003/main.py",
            }
        },
    }

    body = {
        "query": '''
            mutation ($code1:String!, $code2:String!, $code3:String!) {
                CreateCode1: createCode(data: {title:"pytest_code-1", lang:"python3", code:$code1}) {
                    code {
                        title
                        lang
                        path
                    }
                }
                CreateCode2: createCode(data: {title:"pytest_code-2", lang:"python3", code:$code2}) {
                    code {
                        title
                        lang
                        path
                    }
                }
                CreateCode3: createCode(data: {title:"pytest_code-3", lang:"python3", code:$code3}) {
                    code {
                        title
                        lang
                        path
                    }
                }
            }
        ''',
        "variables": {
            "code1": "testcode1",
            "code2": "testcode2",
            "code3": "testcode3",
        }
    }

    response = client.simulate_post('/api/graphql', content_type='application/json', body=json.dumps(body), headers={
        "Authorization": my_token,
    })
    result_doc = json.loads(response.content.decode())

    assert result_doc == doc
    assert response.status == falcon.HTTP_OK

    with open(doc['CreateCode1']['code']['path'], 'rb') as code1, open(doc['CreateCode2']['code']['path'], 'rb') as code2, open(doc['CreateCode3']['code']['path'], 'rb') as code3:
        assert code1.read().decode() == body['variables']['code1']
        assert code2.read().decode() == body['variables']['code2']
        assert code3.read().decode() == body['variables']['code3']

def test_update_code_without_token(client):
    doc = {
        "title": "401 Unauthorized",
        "description": "토큰이 없는뎁쇼",
    }

    body = {
        "query": '''
            mutation {
                updateCode(data: {id: 2, title:"pytest_updatedcode-1"}) {
                    code {
                        title
                    }
                }
            }
        '''
    }

    response = client.simulate_post('/api/graphql', content_type='application/json', body=json.dumps(body))
    result_doc = json.loads(response.content.decode())

    assert result_doc == doc
    assert response.status == falcon.HTTP_401

def test_update_code_with_invalid_token(client):
    doc = {
        "title": "401 Unauthorized",
        "description": "PERMISSION DENIED",
    }

    body = {
        "query": '''
            mutation {
                updateCode(data: {id: 2, title:"pytest_updatedcode-1"}) {
                    code {
                        title
                    }
                }
            }
        '''
    }

    response = client.simulate_post('/api/graphql', content_type='application/json', body=json.dumps(body), headers={
        "Authorization": others_token,
    })
    result_doc = json.loads(response.content.decode())

    assert result_doc == doc
    assert response.status == falcon.HTTP_401

def test_update_post_with_valid_token(client):
    doc = {
        "updateCode": {
            "code": {
                "title": "pytest_updatedcode-1",
                "path": "test/codes/python3/0000000002/main.py",
            }
        }
    }

    body = {
        "query": '''
            mutation ($code: String!){
                updateCode(data: {id: 2, title:"pytest_updatedcode-1", code:$code}) {
                    code {
                        title
                        path
                    }
                }
            }
        ''',
        "variables": {
            "code": "updatedcode",
        },
    }

    response = client.simulate_post('/api/graphql', content_type='application/json', body=json.dumps(body), headers={
        "Authorization": my_token,
    })
    result_doc = json.loads(response.content.decode())

    assert result_doc == doc
    assert response.status == falcon.HTTP_OK

    with open(doc['updateCode']['code']['path'], 'rb') as f:
        assert f.read().decode() == body['variables']['code']

def test_delete_code_without_token(client):
    doc = {
        "title": "401 Unauthorized",
        "description": "토큰이 없는뎁쇼",
    }

    body = {
        "query": '''
            mutation {
                deleteCode(data: {id: 3}) {
                    code {
                        title
                    }
                }
            }
        '''
    }

    response = client.simulate_post('/api/graphql', content_type='application/json', body=json.dumps(body))
    result_doc = json.loads(response.content.decode())

    assert result_doc == doc
    assert response.status == falcon.HTTP_401

def test_delete_code_with_invalid_token(client):
    doc = {
        "title": "401 Unauthorized",
        "description": "PERMISSION DENIED",
    }

    body = {
        "query": '''
            mutation {
                deleteCode(data: {id: 3}) {
                    code {
                        title
                    }
                }
            }
        '''
    }

    response = client.simulate_post('/api/graphql', content_type='application/json', body=json.dumps(body), headers={
        "Authorization": others_token,
    })
    result_doc = json.loads(response.content.decode())

    assert result_doc == doc
    assert response.status == falcon.HTTP_401

def test_delete_code_with_valid_token(client):
    doc = {
        "deleteCode": {
            "code": {
                "title": "pytest_code-3",
                "path": "test/codes/python3/0000000003/main.py",
            }
        }
    }

    body = {
        "query": '''
            mutation {
                deleteCode(data: {id: 3}) {
                    code {
                        title
                        path
                    }
                }
            }
        '''
    }

    response = client.simulate_post('/api/graphql', content_type='application/json', body=json.dumps(body), headers={
        "Authorization": my_token,
    })
    result_doc = json.loads(response.content.decode())

    assert result_doc == doc
    assert response.status == falcon.HTTP_OK

    assert not os.path.exists(doc['deleteCode']['code']['path'])

def test_update_code_by_admin(client):
    doc = {
        "updateCode": {
            "code": {
                "title": "pytest_updatedbyadmin-1",
                "path": "test/codes/python3/0000000002/main.py"
            }
        }
    }

    body = {
        "query": '''
            mutation ($code: String!) {
                updateCode(data: {id: 2, title:"pytest_updatedbyadmin-1", code:$code}) {
                    code {
                        title
                        path
                    }
                }
            }
        ''',
        "variables": {
            "code": "updatedbyadmincode",
        }
    }

    response = client.simulate_post('/api/graphql', content_type='application/json', body=json.dumps(body), headers={
        'Authorization': admin_token
    })
    result_doc = json.loads(response.content.decode())

    assert result_doc == doc
    assert response.status == falcon.HTTP_OK

    with open(doc['updateCode']['code']['path'], 'rb') as f:
        assert f.read().decode() == body['variables']['code']

def test_delete_code_by_admin(client):
    doc = {
        "deleteCode": {
            "code": {
                "title": "pytest_updatedbyadmin-1",
                "path": "test/codes/python3/0000000002/main.py",
            }
        }
    }

    body = {
        "query": '''
            mutation {
                deleteCode(data: {id: 2}) {
                    code {
                        title
                        path
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

    assert not os.path.exists(doc['deleteCode']['code']['path'])