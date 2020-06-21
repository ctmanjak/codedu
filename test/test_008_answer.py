import json
import falcon

from look.app import app

from . import client, my_token, others_token, admin_token

def test_create_answer_without_token(client):
    doc = {
        "title": "401 Unauthorized",
        "description": "토큰이 없는뎁쇼",
    }

    body = {
        "query": '''
            mutation {
                createAnswer(data: {questionId: 1, content:"pytest_answer-1"}) {
                    answer {
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

def test_create_answer_with_token(client):
    doc = {
        "CreateAnswer": {
            "answer": {
                "content": "pytest_answer-1",
            }
        },
        "CreateAnswer2": {
            "answer": {
                "content": "pytest_answer-2",
            }
        },
        "CreateAnswer3": {
            "answer": {
                "content": "pytest_answer-3",
            }
        },
    }

    body = {
        "query": '''
            mutation {
                CreateAnswer: createAnswer(data: {questionId: 1, content:"pytest_answer-1"}) {
                    answer {
                        content
                    }
                }
                CreateAnswer2: createAnswer(data: {questionId: 1, content:"pytest_answer-2"}) {
                    answer {
                        content
                    }
                }
                CreateAnswer3: createAnswer(data: {questionId: 1, content:"pytest_answer-3"}) {
                    answer {
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

def test_update_answer_without_token(client):
    doc = {
        "title": "401 Unauthorized",
        "description": "토큰이 없는뎁쇼",
    }

    body = {
        "query": '''
            mutation {
                updateAnswer(data: {id: 3, content:"pytest_updatedanswer-1"}) {
                    answer {
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

def test_update_answer_with_invalid_token(client):
    doc = {
        "title": "401 Unauthorized",
        "description": "PERMISSION DENIED",
    }

    body = {
        "query": '''
            mutation {
                updateAnswer(data: {id: 3, content:"pytest_updatedanswer-1"}) {
                    answer {
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

def test_update_answer_with_valid_token(client):
    doc = {
        "updateAnswer": {
            "answer": {
                "content": "pytest_updatedanswer-1"
            }
        }
    }

    body = {
        "query": '''
            mutation {
                updateAnswer(data: {id: 3, content:"pytest_updatedanswer-1"}) {
                    answer {
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

def test_delete_answer_without_token(client):
    doc = {
        "title": "401 Unauthorized",
        "description": "토큰이 없는뎁쇼",
    }

    body = {
        "query": '''
            mutation {
                deleteAnswer(data: {id: 3}) {
                    answer {
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

def test_delete_answer_with_invalid_token(client):
    doc = {
        "title": "401 Unauthorized",
        "description": "PERMISSION DENIED",
    }

    body = {
        "query": '''
            mutation {
                deleteAnswer(data: {id: 3}) {
                    answer {
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

def test_delete_answer_with_valid_token(client):
    doc = {
        "deleteAnswer": {
            "answer": {
                "content": "pytest_updatedanswer-1"
            }
        }
    }

    body = {
        "query": '''
            mutation {
                deleteAnswer(data: {id: 3}) {
                    answer {
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

def test_update_answer_by_admin(client):
    doc = {
        "updateAnswer": {
            "answer": {
                "content": "pytest_updatedbyadmin-1"
            }
        }
    }

    body = {
        "query": '''
            mutation {
                updateAnswer(data: {id: 2, content:"pytest_updatedbyadmin-1"}) {
                    answer {
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

def test_delete_answer_by_admin(client):
    doc = {
        "deleteAnswer": {
            "answer": {
                "content": "pytest_updatedbyadmin-1"
            }
        }
    }

    body = {
        "query": '''
            mutation {
                deleteAnswer(data: {id: 2}) {
                    answer {
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

def test_create_question(client):
    doc = {
        "createQuestion": {
            "question": {
                "title": "pytest_cascadetest",
                "content": "pytest_cascadetest's content",
            }
        },
    }

    body = {
        "query": '''
            mutation {
                createQuestion(data: {title:"pytest_cascadetest", content:"pytest_cascadetest's content", tags:"tag1 tag2"}) {
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

def test_create_answer(client):
    doc = {
        "CreateAnswer": {
            "answer": {
                "content": "pytest_cascadetest_answer-1",
            }
        },
        "CreateAnswer2": {
            "answer": {
                "content": "pytest_cascadetest_answer-2",
            }
        },
        "CreateAnswer3": {
            "answer": {
                "content": "pytest_cascadetest_answer-3",
            }
        },
    }

    body = {
        "query": '''
            mutation {
                CreateAnswer: createAnswer(data: {questionId: 4, content:"pytest_cascadetest_answer-1"}) {
                    answer {
                        content
                    }
                }
                CreateAnswer2: createAnswer(data: {questionId: 4, content:"pytest_cascadetest_answer-2"}) {
                    answer {
                        content
                    }
                }
                CreateAnswer3: createAnswer(data: {questionId: 4, content:"pytest_cascadetest_answer-3"}) {
                    answer {
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

def test_delete_answer(client):
    doc = {
        "deleteAnswer": {
            "answer": {
                "content": "pytest_cascadetest_answer-1"
            }
        }
    }

    body = {
        "query": '''
            mutation {
                deleteAnswer(data: {id: 4}) {
                    answer {
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

def test_check_question(client):
    doc = {
        "question": {
            "edges": [{
                "node": {
                    "answers": {
                        "edges": [
                            {
                                "node": {
                                    "content": "pytest_cascadetest_answer-2"
                                }
                            },
                            {
                                "node": {
                                    "content": "pytest_cascadetest_answer-3"
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
                question(filters: {id: 4}) {
                    edges {
                        node {
                            answers {
                                edges {
                                    node {
                                        content
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
                question(filters: {id: 4}) {
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
                deleteQuestion(data: {id: 4}) {
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