import json, time
import falcon
import hmac
from hashlib import sha256
from cerberus import Validator
from requests_toolbelt import MultipartEncoder

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

def test_register_with_not_allowed_image(client):
    doc = {
        "title": "400 Bad Request",
        "description": "Not allowed image type"
    }

    query = {
        "query": '''
            mutation {
                createPost(data: {content:"imagetest_post-1"}) {
                    post {
                        content
                        image
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
    
    response = client.simulate_post('/api/graphql', content_type=m.content_type, body=m.to_string(), headers={
        "Authorization": my_token,
    })

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
                createPost(data: {content:"imagetest_post-1"}) {
                    post {
                        content
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
    
    response = client.simulate_post('/api/graphql', content_type=m.content_type, body=m.to_string(), headers={
        "Authorization": my_token,
    })

    result_doc = json.loads(response.content.decode())

    assert result_doc == doc
    assert response.status == falcon.HTTP_400

def test_register_with_valid_image(client):
    doc = {
        "createPost": {
            "post": {
                "content": "imagetest_post-1",
                "image": "test/images/post/0000000006.png",
            }
        },
    }

    query = {
        "query": '''
            mutation {
                createPost(data: {content:"imagetest_post-1"}) {
                    post {
                        content
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
    
    response = client.simulate_post('/api/graphql', content_type=m.content_type, body=m.to_string(), headers={
        "Authorization": my_token,
    })

    result_doc = json.loads(response.content.decode())

    assert result_doc == doc
    assert response.status == falcon.HTTP_OK

    with open(doc['createPost']['post']['image'], 'rb') as f:
        assert f.read() == fake_image_byte

