import json
import falcon

from look.app import app

from . import client, my_token, others_token, admin_token

def test_create_code_comment_without_token(client):
    doc = {
        "title": "401 Unauthorized",
        "description": "토큰이 없는뎁쇼",
    }

    body = {
        "query": '''
            mutation {
                createCodeComment(data: {codeId: 1, content:"pytest_code_comment_comment-1"}) {
                    codeComment {
                        content
                    }
                }
            }
        '''
    }

    response = client.simulate_post('/api/graphql', content_type='application/json', body=json.dumps(body))
    result_doc = json.loads(response.content.decode())

    assert result_doc == doc
    assert response.status == falcon.HTTP_401

def test_create_code_comment_with_token(client):
    doc = {
        "createCodeComment": {
            "codeComment": {
                "content": "pytest_code_comment-1",
            }
        },
        "createCodeComment2": {
            "codeComment": {
                "content": "pytest_code_comment-2",
            }
        },
        "createCodeComment3": {
            "codeComment": {
                "content": "pytest_code_comment-3",
            }
        },
    }

    body = {
        "query": '''
            mutation {
                createCodeComment: createCodeComment(data: {codeId: 1, content:"pytest_code_comment-1"}) {
                    codeComment {
                        content
                    }
                }
                createCodeComment2: createCodeComment(data: {codeId: 1, content:"pytest_code_comment-2"}) {
                    codeComment {
                        content
                    }
                }
                createCodeComment3: createCodeComment(data: {codeId: 1, content:"pytest_code_comment-3"}) {
                    codeComment {
                        content
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

def test_update_code_comment_comment_without_token(client):
    doc = {
        "title": "401 Unauthorized",
        "description": "토큰이 없는뎁쇼",
    }

    body = {
        "query": '''
            mutation {
                updateCodeComment(data: {id: 3, content:"pytest_updatedcode_comment-1"}) {
                    codeComment {
                        content
                    }
                }
            }
        '''
    }

    response = client.simulate_post('/api/graphql', content_type='application/json', body=json.dumps(body))
    result_doc = json.loads(response.content.decode())

    assert result_doc == doc
    assert response.status == falcon.HTTP_401

def test_update_code_comment_with_invalid_token(client):
    doc = {
        "title": "401 Unauthorized",
        "description": "PERMISSION DENIED",
    }

    body = {
        "query": '''
            mutation {
                updateCodeComment(data: {id: 3, content:"pytest_updatedcode_comment-1"}) {
                    codeComment {
                        content
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

def test_update_code_comment_with_valid_token(client):
    doc = {
        "updateCodeComment": {
            "codeComment": {
                "content": "pytest_updatedcode_comment-1"
            }
        }
    }

    body = {
        "query": '''
            mutation {
                updateCodeComment(data: {id: 3, content:"pytest_updatedcode_comment-1"}) {
                    codeComment {
                        content
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

def test_delete_code_comment_without_token(client):
    doc = {
        "title": "401 Unauthorized",
        "description": "토큰이 없는뎁쇼",
    }

    body = {
        "query": '''
            mutation {
                deleteCodeComment(data: {id: 3}) {
                    codeComment {
                        content
                    }
                }
            }
        '''
    }

    response = client.simulate_post('/api/graphql', content_type='application/json', body=json.dumps(body))
    result_doc = json.loads(response.content.decode())

    assert result_doc == doc
    assert response.status == falcon.HTTP_401

def test_delete_code_comment_with_invalid_token(client):
    doc = {
        "title": "401 Unauthorized",
        "description": "PERMISSION DENIED",
    }

    body = {
        "query": '''
            mutation {
                deleteCodeComment(data: {id: 3}) {
                    codeComment {
                        content
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

def test_delete_code_comment_with_valid_token(client):
    doc = {
        "deleteCodeComment": {
            "codeComment": {
                "content": "pytest_updatedcode_comment-1"
            }
        }
    }

    body = {
        "query": '''
            mutation {
                deleteCodeComment(data: {id: 3}) {
                    codeComment {
                        content
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

def test_update_code_comment_by_admin(client):
    doc = {
        "updateCodeComment": {
            "codeComment": {
                "content": "pytest_updatedbyadmin-1"
            }
        }
    }

    body = {
        "query": '''
            mutation {
                updateCodeComment(data: {id: 2, content:"pytest_updatedbyadmin-1"}) {
                    codeComment {
                        content
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

def test_delete_code_comment_by_admin(client):
    doc = {
        "deleteCodeComment": {
            "codeComment": {
                "content": "pytest_updatedbyadmin-1"
            }
        }
    }

    body = {
        "query": '''
            mutation {
                deleteCodeComment(data: {id: 2}) {
                    codeComment {
                        content
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

