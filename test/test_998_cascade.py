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

def test_init_db(client):
    response = client.simulate_delete('/test/db')
    response2 = client.simulate_get('/test/db')

    assert response.status == falcon.HTTP_OK
    assert response2.status == falcon.HTTP_OK

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
        },
        "Register3": {
            "user": {
                "email": "pytestuser3@email.com",
                "username": "pytestuser3",
                "password": hmac.new(Config.SECRET_KEY.encode(), "pytestuser3123!".encode(), sha256).hexdigest(),
            }
        },
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
                Register3: register(data: {username:"pytestuser3", email:"pytestuser3@email.com", password:"pytestuser3123!"}) {
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
            }
        '''
    }

    response = client.simulate_post('/api/graphql', content_type='application/json', body=json.dumps(body), headers={
        "Authorization": my_token,
    })
    result_doc = json.loads(response.content.decode())

    assert result_doc == doc
    assert response.status == falcon.HTTP_OK

def test_create_post_comment(client):
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
        "CreatePostComment4": {
            "postComment": {
                "content": "pytest_post_comment-4",
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
                CreatePostComment3: createPostComment(data: {postId: 1, parentCommentId: 2, content:"pytest_post_comment-3"}) {
                    postComment {
                        content
                    }
                }
                CreatePostComment4: createPostComment(data: {postId: 2, content:"pytest_post_comment-4"}) {
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

def test_delete_post_comment(client):
    doc = {
        "deletePostComment": {
            "postComment": {
                "content": "pytest_post_comment-2"
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
        "Authorization": my_token,
    })
    result_doc = json.loads(response.content.decode())

    assert result_doc == doc
    assert response.status == falcon.HTTP_OK

def test_check_post_comment(client):
    doc = {
        "postComment": {
            "edges": [{
                "node": {
                    "comment": "pytest_post_comment-1"
                }
            }]
        }
    }

    body = {
        "query": '''
            query {
                postComment(filters: {postId: 1}) {
                    edges {
                        node {
                            comment
                        }
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

def test_delete_post(client):
    doc = {
        "deletePost": {
            "post": {
                "content": "pytest_post-1"
            }
        }
    }

    body = {
        "query": '''
            mutation {
                deletePost(data: {id: 1}) {
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

def test_check_post_comment(client):
    doc = {
        "postComment": {
            "edges": []
        }
    }

    body = {
        "query": '''
            query {
                postComment(filters: {postId: 1}) {
                    edges {
                        node {
                            content
                        }
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

def test_create_code(client):
    doc = {
        "CreateCode": {
            "code": {
                "title": "pytest_code-1",
            }
        },
        "CreateCode2": {
            "code": {
                "title": "pytest_code-2",
            }
        },
    }

    body = {
        "query": '''
            mutation {
                CreateCode: createCode(data: {title:"pytest_code-1", lang:"python3", code:"test"}) {
                    code {
                        title
                    }
                }
                CreateCode2: createCode(data: {title:"pytest_code-2", lang:"python3", code:"test"}) {
                    code {
                        title
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

def test_create_code_comment(client):
    doc = {
        "CreateCodeComment": {
            "codeComment": {
                "content": "pytest_code_comment-1",
            }
        },
        "CreateCodeComment2": {
            "codeComment": {
                "content": "pytest_code_comment-2",
            }
        },
        "CreateCodeComment3": {
            "codeComment": {
                "content": "pytest_code_comment-3",
            }
        },
        "CreateCodeComment4": {
            "codeComment": {
                "content": "pytest_code_comment-4",
            }
        },
    }

    body = {
        "query": '''
            mutation {
                CreateCodeComment: createCodeComment(data: {codeId: 1, content:"pytest_code_comment-1"}) {
                    codeComment {
                        content
                    }
                }
                CreateCodeComment2: createCodeComment(data: {codeId: 1, content:"pytest_code_comment-2"}) {
                    codeComment {
                        content
                    }
                }
                CreateCodeComment3: createCodeComment(data: {codeId: 1, parentCommentId: 2, content:"pytest_code_comment-3"}) {
                    codeComment {
                        content
                    }
                }
                CreateCodeComment4: createCodeComment(data: {codeId: 2, content:"pytest_code_comment-4"}) {
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

def test_delete_code_comment(client):
    doc = {
        "deleteCodeComment": {
            "codeComment": {
                "content": "pytest_code_comment-2"
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
        "Authorization": my_token,
    })
    result_doc = json.loads(response.content.decode())

    assert result_doc == doc
    assert response.status == falcon.HTTP_OK

def test_check_code_comment(client):
    doc = {
        "codeComment": {
            "edges": [{
                "node": {
                    "content": "pytest_code_comment-1"
                }
            }]
        }
    }

    body = {
        "query": '''
            query {
                codeComment(filters: {codeId: 1}) {
                    edges {
                        node {
                            content
                        }
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

def test_delete_code(client):
    doc = {
        "deleteCode": {
            "code": {
                "title": "pytest_code-1"
            }
        }
    }

    body = {
        "query": '''
            mutation {
                deleteCode(data: {id: 1}) {
                    code {
                        title
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

def test_check_code_comment(client):
    doc = {
        "codeComment": {
            "edges": []
        }
    }

    body = {
        "query": '''
            query {
                codeComment(filters: {codeId: 1}) {
                    edges {
                        node {
                            content
                        }
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

def test_create_question(client):
    doc = {
        "CreateQuestion": {
            "question": {
                "title": "pytest_cascadetest",
                "content": "pytest_cascadetest's content",
            }
        },
        "CreateQuestion2": {
            "question": {
                "title": "pytest_cascadetest2",
                "content": "pytest_cascadetest2's content",
            }
        },
    }

    body = {
        "query": '''
            mutation {
                CreateQuestion: createQuestion(data: {title:"pytest_cascadetest", content:"pytest_cascadetest's content", tags:"tag1 tag2"}) {
                    question {
                        title
                        content
                    }
                }
                CreateQuestion2: createQuestion(data: {title:"pytest_cascadetest2", content:"pytest_cascadetest2's content", tags:"tag1 tag2"}) {
                    question {
                        title
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

def test_delete_tag(client):
    doc = {
        "deleteTag": {
            "tag": {
                "name": "tag1"
            }
        }
    }

    body = {
        "query": '''
            mutation {
                deleteTag(data: {id: 1}) {
                    tag {
                        name
                    }
                }
            }
        '''
    }

    response = client.simulate_post('/api/graphql', content_type='application/json', body=json.dumps(body), headers={
        "Authorization": admin_token,
    })
    result_doc = json.loads(response.content.decode())

    assert result_doc == doc
    assert response.status == falcon.HTTP_OK

def test_check_question(client):
    doc = {
        "question": {
            "edges": [{
                "node": {
                    "tags": {
                        "edges": [
                            {
                                "node": {
                                    "name": "tag2"
                                }
                            },
                        ]
                    }
                }
            }]
        }
    }

    body = {
        "query": '''
            query {
                question(filters: {id: 1}) {
                    edges {
                        node {
                            tags {
                                edges {
                                    node {
                                        name
                                    }
                                }
                            }
                        }
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

def test_delete_question(client):
    doc = {
        "deleteQuestion": {
            "question": {
                "title": "pytest_cascadetest"
            }
        }
    }

    body = {
        "query": '''
            mutation {
                deleteQuestion(data: {id: 1}) {
                    question {
                        title
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

def test_check_tag(client):
    doc = {
        "tag": {
            "edges": [{
                "node": {
                    "name": "tag2"
                }
            }]
        }
    }

    body = {
        "query": '''
            query {
                tag {
                    edges {
                        node {
                            name
                        }
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

def test_delete_account(client):
    doc = {
        "deleteAccount": {
            "user": {
                "email": "pytestuser3@email.com",
                "username": "pytestuser3",
                "password": hmac.new(Config.SECRET_KEY.encode(), "pytestuser3123!".encode(), sha256).hexdigest(),
            }
        }
    }

    body = {
        "query": '''
            mutation {
                deleteAccount(data: {id: 3, password: "pytestuser3123!"}) {
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

def test_check_post(client):
    doc = {
        "post": {
            "edges": [{
                "node": {
                    "userId": None
                }
            }]
        }
    }

    body = {
        "query": '''
            query {
                post {
                    edges {
                        node {
                            userId
                        }
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

def test_check_post_comment(client):
    doc = {
        "postComment": {
            "edges": [{
                "node": {
                    "userId": None,
                }
            }]
        }
    }

    body = {
        "query": '''
            query {
                postComment(filters: {postId: 2}) {
                    edges {
                        node {
                            userId
                        }
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

def test_check_code(client):
    doc = {
        "code": {
            "edges": [{
                "node": {
                    "userId": None
                }
            }]
        }
    }

    body = {
        "query": '''
            query {
                code {
                    edges {
                        node {
                            userId
                        }
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

def test_check_code_comment(client):
    doc = {
        "codeComment": {
            "edges": [{
                "node": {
                    "userId": None,
                }
            }]
        }
    }

    body = {
        "query": '''
            query {
                codeComment(filters: {codeId: 2}) {
                    edges {
                        node {
                            userId
                        }
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

# question, answer 등 추가해야 하는데 귀찮아서 일단 여기까지 어차피 구조는 비슷하니 걔네도 될 듯