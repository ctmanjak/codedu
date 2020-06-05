import json, time
import falcon
import hmac
from hashlib import sha256
from cerberus import Validator

from look.app import app
from look.config import Config

from . import client, my_token, others_token, admin_token

v = Validator()

def test_create_post_without_token(client):
    doc = {
        "title": "400 Bad Request",
        "description": "토큰이 없는뎁쇼",
    }

    body = {
        "query": '''
            mutation {
                createPost(data: {content:"pytest_post-1"}) {
                    post {
                        content
                    }
                }
            }
        '''
    }

    response = client.simulate_post('/api/graphql', content_type='application/json', body=json.dumps(body))
    result_doc = json.loads(response.content.decode())

    assert result_doc == doc
    assert response.status == falcon.HTTP_400

def test_create_post(client):
    doc = {
        "CreatePost": {
            "post": {
                "content": "pytest_post-1",
            }
        },
        "CreatePost2": {
            "post": {
                "content": "pytest_post-2",
            }
        },
        "CreatePost3": {
            "post": {
                "content": "pytest_post-3",
            }
        },
    }

    body = {
        "query": '''
            mutation {
                CreatePost: createPost(data: {content:"pytest_post-1"}) {
                    post {
                        content
                    }
                }
                CreatePost2: createPost(data: {content:"pytest_post-2"}) {
                    post {
                        content
                    }
                }
                CreatePost3: createPost(data: {content:"pytest_post-3"}) {
                    post {
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

def test_update_post_without_token(client):
    doc = {
        "title": "400 Bad Request",
        "description": "토큰이 없는뎁쇼",
    }

    body = {
        "query": '''
            mutation {
                updatePost(data: {id: 5, content:"pytest_updatedpost-1"}) {
                    post {
                        content
                    }
                }
            }
        '''
    }

    response = client.simulate_post('/api/graphql', content_type='application/json', body=json.dumps(body))
    result_doc = json.loads(response.content.decode())

    assert result_doc == doc
    assert response.status == falcon.HTTP_400

def test_update_post_with_invalid_token(client):
    doc = {
        "title": "400 Bad Request",
        "description": "PERMISSION DENIED",
    }

    body = {
        "query": '''
            mutation {
                updatePost(data: {id: 5, content:"pytest_updatedpost-1"}) {
                    post {
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
    assert response.status == falcon.HTTP_400

def test_update_post_with_valid_token(client):
    doc = {
        "updatePost": {
            "post": {
                "content": "pytest_updatedpost-1"
            }
        }
    }

    body = {
        "query": '''
            mutation {
                updatePost(data: {id: 5, content:"pytest_updatedpost-1"}) {
                    post {
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

def test_delete_post_without_token(client):
    doc = {
        "title": "400 Bad Request",
        "description": "토큰이 없는뎁쇼",
    }

    body = {
        "query": '''
            mutation {
                deletePost(data: {id: 5}) {
                    post {
                        content
                    }
                }
            }
        '''
    }

    response = client.simulate_post('/api/graphql', content_type='application/json', body=json.dumps(body))
    result_doc = json.loads(response.content.decode())

    assert result_doc == doc
    assert response.status == falcon.HTTP_400

def test_delete_post_with_invalid_token(client):
    doc = {
        "title": "400 Bad Request",
        "description": "PERMISSION DENIED",
    }

    body = {
        "query": '''
            mutation {
                deletePost(data: {id: 5}) {
                    post {
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
    assert response.status == falcon.HTTP_400

def test_delete_post_with_valid_token(client):
    doc = {
        "deletePost": {
            "post": {
                "content": "pytest_updatedpost-1"
            }
        }
    }

    body = {
        "query": '''
            mutation {
                deletePost(data: {id: 5}) {
                    post {
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

def test_update_post_by_admin(client):
    doc = {
        "updatePost": {
            "post": {
                "content": "pytest_updatedbyadmin-1"
            }
        }
    }

    body = {
        "query": '''
            mutation {
                updatePost(data: {id: 4, content:"pytest_updatedbyadmin-1"}) {
                    post {
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

def test_delete_post_by_admin(client):
    doc = {
        "deletePost": {
            "post": {
                "content": "pytest_updatedbyadmin-1"
            }
        }
    }

    body = {
        "query": '''
            mutation {
                deletePost(data: {id: 4}) {
                    post {
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