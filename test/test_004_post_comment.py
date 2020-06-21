import json
import falcon

from look.app import app

from . import client, my_token, others_token, admin_token

def test_create_post_comment_without_token(client):
    doc = {
        "title": "401 Unauthorized",
        "description": "토큰이 없는뎁쇼",
    }

    body = {
        "query": '''
            mutation {
                createPostComment(data: {postId: 1, content:"pytest_post_comment_comment-1"}) {
                    postComment {
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

def test_create_post_comment_with_token(client):
    doc = {
        "CreatePostComment": {
            "postComment": {
                "content": "pytest_post_comment-1",
            }
        },
        "CreatePostComment2": {
            "postComment": {
                "content": "pytest_post_comment-2",
            }
        },
        "CreatePostComment3": {
            "postComment": {
                "content": "pytest_post_comment-3",
            }
        },
    }

    body = {
        "query": '''
            mutation {
                CreatePostComment: createPostComment(data: {postId: 1, content:"pytest_post_comment-1"}) {
                    postComment {
                        content
                    }
                }
                CreatePostComment2: createPostComment(data: {postId: 1, content:"pytest_post_comment-2"}) {
                    postComment {
                        content
                    }
                }
                CreatePostComment3: createPostComment(data: {postId: 1, content:"pytest_post_comment-3"}) {
                    postComment {
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

def test_update_post_comment_comment_without_token(client):
    doc = {
        "title": "401 Unauthorized",
        "description": "토큰이 없는뎁쇼",
    }

    body = {
        "query": '''
            mutation {
                updatePostComment(data: {id: 3, content:"pytest_updatedpost_comment-1"}) {
                    postComment {
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

def test_update_post_comment_with_invalid_token(client):
    doc = {
        "title": "401 Unauthorized",
        "description": "PERMISSION DENIED",
    }

    body = {
        "query": '''
            mutation {
                updatePostComment(data: {id: 3, content:"pytest_updatedpost_comment-1"}) {
                    postComment {
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

def test_update_post_comment_with_valid_token(client):
    doc = {
        "updatePostComment": {
            "postComment": {
                "content": "pytest_updatedpost_comment-1"
            }
        }
    }

    body = {
        "query": '''
            mutation {
                updatePostComment(data: {id: 3, content:"pytest_updatedpost_comment-1"}) {
                    postComment {
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

def test_delete_post_comment_without_token(client):
    doc = {
        "title": "401 Unauthorized",
        "description": "토큰이 없는뎁쇼",
    }

    body = {
        "query": '''
            mutation {
                deletePostComment(data: {id: 3}) {
                    postComment {
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

def test_delete_post_comment_with_invalid_token(client):
    doc = {
        "title": "401 Unauthorized",
        "description": "PERMISSION DENIED",
    }

    body = {
        "query": '''
            mutation {
                deletePostComment(data: {id: 3}) {
                    postComment {
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

def test_delete_post_comment_with_valid_token(client):
    doc = {
        "deletePostComment": {
            "postComment": {
                "content": "pytest_updatedpost_comment-1"
            }
        }
    }

    body = {
        "query": '''
            mutation {
                deletePostComment(data: {id: 3}) {
                    postComment {
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

def test_update_post_comment_by_admin(client):
    doc = {
        "updatePostComment": {
            "postComment": {
                "content": "pytest_updatedbyadmin-1"
            }
        }
    }

    body = {
        "query": '''
            mutation {
                updatePostComment(data: {id: 2, content:"pytest_updatedbyadmin-1"}) {
                    postComment {
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

def test_delete_post_comment_by_admin(client):
    doc = {
        "deletePostComment": {
            "postComment": {
                "content": "pytest_updatedbyadmin-1"
            }
        }
    }

    body = {
        "query": '''
            mutation {
                deletePostComment(data: {id: 2}) {
                    postComment {
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

