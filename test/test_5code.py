import os
import json
import subprocess
import falcon
from cerberus import Validator

from look.app import app

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
    schema = {
        "CreateCode1": { "type": "dict", "schema": {
            "code": { "type": "dict", "schema": {
                "title": { "type": "string", "allowed": ["pytest_code-1"]},
                "lang": { "type": "string", "allowed": ["python3"]},
                "path": { "type": "string" , "regex": "^codes/python3/[A-Za-z0-9]{12}/main.py$"},
            }}
        }},
        "CreateCode2": { "type": "dict", "schema": {
            "code": { "type": "dict", "schema": {
                "title": { "type": "string", "allowed": ["pytest_code-2"]},
                "lang": { "type": "string", "allowed": ["python3"]},
                "path": { "type": "string" , "regex": "^codes/python3/[A-Za-z0-9]{12}/main.py$"},
            }}
        }},
        "CreateCode3": { "type": "dict", "schema": {
            "code": { "type": "dict", "schema": {
                "title": { "type": "string", "allowed": ["pytest_code-3"]},
                "lang": { "type": "string", "allowed": ["python3"]},
                "path": { "type": "string" , "regex": "^codes/python3/[A-Za-z0-9]{12}/main.py$"},
            }}
        }},
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

    assert v.validate(result_doc, schema)
    assert response.status == falcon.HTTP_OK

    with open(f"test/{result_doc['CreateCode1']['code']['path']}", 'rb') as code1, open(f"test/{result_doc['CreateCode2']['code']['path']}", 'rb') as code2, open(f"test/{result_doc['CreateCode3']['code']['path']}", 'rb') as code3:
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
    schema = {
        "updateCode": { "type": "dict", "schema": {
            "code": { "type": "dict", "schema": {
                "title": { "type": "string", "allowed": ["pytest_updatedcode-1"]},
                "path": { "type": "string" , "regex": "^codes/python3/[A-Za-z0-9]{12}/main.py$"},
            }}
        }}
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

    assert v.validate(result_doc, schema)
    assert response.status == falcon.HTTP_OK

    with open(f"test/{result_doc['updateCode']['code']['path']}", 'rb') as f:
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
    schema = {
        "deleteCode": { "type": "dict", "schema": {
            "code": { "type": "dict", "schema": {
                "title": { "type": "string", "allowed": ["pytest_code-3"]},
                "path": { "type": "string" , "regex": "^codes/python3/[A-Za-z0-9]{12}/main.py$"},
            }}
        }}
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

    assert v.validate(result_doc, schema)
    assert response.status == falcon.HTTP_OK

    assert not os.path.exists(f"test/{result_doc['deleteCode']['code']['path']}")

def test_update_code_by_admin(client):
    schema = {
        "updateCode": { "type": "dict", "schema": {
            "code": { "type": "dict", "schema": {
                "title": { "type": "string", "allowed": ["pytest_updatedbyadmin-1"]},
                "path": { "type": "string" , "regex": "^codes/python3/[A-Za-z0-9]{12}/main.py$"},
            }}
        }}
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

    assert v.validate(result_doc, schema)
    assert response.status == falcon.HTTP_OK

    with open(f"test/{result_doc['updateCode']['code']['path']}", 'rb') as f:
        assert f.read().decode() == body['variables']['code']

def test_delete_code_by_admin(client):
    schema = {
        "deleteCode": { "type": "dict", "schema": {
            "code": { "type": "dict", "schema": {
                "title": { "type": "string", "allowed": ["pytest_updatedbyadmin-1"]},
                "path": { "type": "string" , "regex": "^codes/python3/[A-Za-z0-9]{12}/main.py$"},
            }}
        }}
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

    assert v.validate(result_doc, schema)
    assert response.status == falcon.HTTP_OK

    assert not os.path.exists(f"test/{result_doc['deleteCode']['code']['path']}")

def test_python3_is_runnable(client):
    schema = {
        "createCode": { "type": "dict", "schema": {
            "code": { "type": "dict", "schema": {
                "title": { "type": "string", "allowed": ["pytest_code-4"]},
                "lang": { "type": "string", "allowed": ["python3"]},
                "path": { "type": "string" , "regex": "^codes/python3/[A-Za-z0-9]{12}/main.py$"},
            }}
        }}
    }

    body = {
        "query": '''
            mutation ($code:String!) {
                createCode(data: {title:"pytest_code-4", lang:"python3", code:$code}) {
                    code {
                        title
                        lang
                        path
                    }
                }
            }
        ''',
        "variables": {
            "code": '''
import json
data = {
    "hi": "hello",
}
print(json.dumps(data))
            ''',
        }
    }

    response = client.simulate_post('/api/graphql', content_type='application/json', body=json.dumps(body), headers={
        "Authorization": my_token,
    })
    result_doc = json.loads(response.content.decode())

    assert v.validate(result_doc, schema)
    assert response.status == falcon.HTTP_OK

    run = {
        "hi": "hello",
    }

    result_run = subprocess.run(["python3", f"test/{result_doc['createCode']['code']['path']}"], stdout=subprocess.PIPE)
    assert result_run.stdout.decode() == f"{json.dumps(run)}\n"

def test_clang_is_runnable(client):
    schema = {
        "createCode": { "type": "dict", "schema": {
            "code": { "type": "dict", "schema": {
                "title": { "type": "string", "allowed": ["pytest_code-5"]},
                "lang": { "type": "string", "allowed": ["clang"]},
                "path": { "type": "string" , "regex": "^codes/clang/[A-Za-z0-9]{12}/main.c$"},
            }}
        }}
    }

    body = {
        "query": '''
            mutation ($code:String!) {
                createCode(data: {title:"pytest_code-5", lang:"clang", code:$code}) {
                    code {
                        title
                        lang
                        path
                    }
                }
            }
        ''',
        "variables": {
            "code": '''
                #include <stdio.h>

                int main() {
                    printf("%d", 133);
                }
            ''',
        }
    }

    response = client.simulate_post('/api/graphql', content_type='application/json', body=json.dumps(body), headers={
        "Authorization": my_token,
    })
    result_doc = json.loads(response.content.decode())

    assert v.validate(result_doc, schema)
    assert response.status == falcon.HTTP_OK

    path = '/'.join(result_doc['createCode']['code']['path'].split('/')[:-1])
    compile_proc = subprocess.run(["gcc", "-o", f"test/{path}/main", f"test/{result_doc['createCode']['code']['path']}"])
    result_run = subprocess.run([f"test/{path}/main"], shell=True, stdout=subprocess.PIPE)
    
    assert result_run.stdout.decode() == "133"