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

def test_create_question_without_token(client):
    doc = {
        "title": "401 Unauthorized",
        "description": "토큰이 없는뎁쇼",
    }

    body = {
        "query": '''
            mutation {
                createQuestion(data: {title:"pytest_question-1", content:"pytest_question-1's content"}) {
                    question {
                        title
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

def test_create_question_with_token(client):
    doc = {
        "createQuestion1": {
            "question": {
                "title": "pytest_question-1",
                "content": "pytest_question-1's content",
            }
        },
        "createQuestion2": {
            "question": {
                "title": "pytest_question-2",
                "content": "pytest_question-2's content",
            }
        },
        "createQuestion3": {
            "question": {
                "title": "pytest_question-3",
                "content": "pytest_question-3's content",
            }
        },
    }

    body = {
        "query": '''
            mutation {
                createQuestion1: createQuestion(data: {title:"pytest_question-1", content:"pytest_question-1's content", tags:"tag1 tag2"}) {
                    question {
                        title
                        content
                    }
                }
                createQuestion2: createQuestion(data: {title:"pytest_question-2", content:"pytest_question-2's content", tags:"tag2 tag3"}) {
                    question {
                        title
                        content
                    }
                }
                createQuestion3: createQuestion(data: {title:"pytest_question-3", content:"pytest_question-3's content", tags:"tag1 tag2"}) {
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

def test_check_tag_is_created(client):
    doc = {
        "tag": {
            "edges": [
                {
                    "node": {
                        "id": "dGFnTm9kZTox",
                        "name": "tag1",
                    },
                },
                {
                    "node": {
                        "id": "dGFnTm9kZToy",
                        "name": "tag2",
                    },
                },
                {
                    "node": {
                        "id": "dGFnTm9kZToz",
                        "name": "tag3",
                    },
                },
            ]
        }
    }

    body = {
        "query": '''
            query {
                tag {
                    edges {
                        node {
                            id
                            name
                        }
                    }
                }
            }
        '''
    }

    response = client.simulate_post('/api/graphql', content_type='application/json', body=json.dumps(body))
    result_doc = json.loads(response.content.decode())

    assert result_doc == doc
    assert response.status == falcon.HTTP_OK

def test_check_question_tag_is_associated(client):
    doc = {
        "question": {
            "edges": [
                {
                    "node": {
                        "title": "pytest_question-1",
                        "tags": {
                            "edges": [
                                {
                                    "node": {
                                        "name": "tag1"
                                    },
                                },
                                {
                                    "node": {
                                        "name": "tag2"
                                    },
                                },
                            ]
                        },
                    }
                },
                {
                    "node": {
                        "title": "pytest_question-2",
                        "tags": {
                            "edges": [
                                {
                                    "node": {
                                        "name": "tag2"
                                    },
                                },
                                {
                                    "node": {
                                        "name": "tag3"
                                    },
                                },
                            ]
                        },
                    },
                },
                {
                    "node": {
                        "title": "pytest_question-3",
                        "tags": {
                            "edges": [
                                {
                                    "node": {
                                        "name": "tag1"
                                    },
                                },
                                {
                                    "node": {
                                        "name": "tag2"
                                    },
                                },
                            ]
                        },
                    },
                },
            ]
        }
    }

    body = {
        "query": '''
            query {
                question {
                    edges {
                        node {
                            title
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

    response = client.simulate_post('/api/graphql', content_type='application/json', body=json.dumps(body))
    result_doc = json.loads(response.content.decode())

    assert result_doc == doc
    assert response.status == falcon.HTTP_OK

def test_update_question_without_token(client):
    doc = {
        "title": "401 Unauthorized",
        "description": "토큰이 없는뎁쇼",
    }

    body = {
        "query": '''
            mutation {
                updateQuestion(data: {id: 3, title:"pytest_updatedquestion-1"}) {
                    question {
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

def test_update_question_with_invalid_token(client):
    doc = {
        "title": "401 Unauthorized",
        "description": "PERMISSION DENIED",
    }

    body = {
        "query": '''
            mutation {
                updateQuestion(data: {id: 3, title:"pytest_updatedquestion-1"}) {
                    question {
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

def test_update_question_with_valid_token(client):
    doc = {
        "updateQuestion": {
            "question": {
                "title": "pytest_updatedquestion-1"
            }
        }
    }

    body = {
        "query": '''
            mutation {
                updateQuestion(data: {id: 3, title:"pytest_updatedquestion-1", tags:"tag3 tag4"}) {
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

def test_check_question_tag_is_updated(client):
    doc = {
        "question": {
            "edges":  [{
                "node": {
                    "title": "pytest_updatedquestion-1",
                    "tags": {
                        "edges": [
                            {
                                "node": {
                                    "name": "tag3"
                                },
                            },
                            {
                                "node": {
                                    "name": "tag4"
                                },
                            },
                        ]
                    },
                }
            }],
        }
    }

    body = {
        "query": '''
            query {
                question (filters: {id: 3}){
                    edges {
                        node {
                            title
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

    response = client.simulate_post('/api/graphql', content_type='application/json', body=json.dumps(body))
    result_doc = json.loads(response.content.decode())

    assert result_doc == doc
    assert response.status == falcon.HTTP_OK

def test_delete_question_without_token(client):
    doc = {
        "title": "401 Unauthorized",
        "description": "토큰이 없는뎁쇼",
    }

    body = {
        "query": '''
            mutation {
                deleteQuestion(data: {id: 3}) {
                    question {
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

def test_delete_question_with_invalid_token(client):
    doc = {
        "title": "401 Unauthorized",
        "description": "PERMISSION DENIED",
    }

    body = {
        "query": '''
            mutation {
                deleteQuestion(data: {id: 3}) {
                    question {
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

def test_delete_question_with_valid_token(client):
    doc = {
        "deleteQuestion": {
            "question": {
                "title": "pytest_updatedquestion-1"
            }
        }
    }

    body = {
        "query": '''
            mutation {
                deleteQuestion(data: {id: 3}) {
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

def test_update_question_by_admin(client):
    doc = {
        "updateQuestion": {
            "question": {
                "title": "pytest_updatedbyadmin-1"
            }
        }
    }

    body = {
        "query": '''
            mutation {
                updateQuestion(data: {id: 2, title:"pytest_updatedbyadmin-1"}) {
                    question {
                        title
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

def test_delete_question_by_admin(client):
    doc = {
        "deleteQuestion": {
            "question": {
                "title": "pytest_updatedbyadmin-1"
            }
        }
    }

    body = {
        "query": '''
            mutation {
                deleteQuestion(data: {id: 2}) {
                    question {
                        title
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

# def test_create_question_with_tags(client):
#     doc = {
#         "createQuestion": {
#             "question": {
#                 "title": "pytest_question-1",
#                 "content": "pytest_question-1's content",
#             }
#         },
#     }

#     body = {
#         "query": '''
#             mutation {
#                 createQuestion(data: {title:"pytest_tagtest-1", content:"pytest_tagtest-1's content", tags:"tag1 tag2"}) {
#                     question {
#                         title
#                         content
#                     }
#                 }
#             }
#         '''
#     }

#     response = client.simulate_post('/api/graphql', content_type='application/json', body=json.dumps(body), headers={
#         "Authorization": my_token,
#     })
#     result_doc = json.loads(response.content.decode())

#     assert result_doc == doc
#     assert response.status == falcon.HTTP_OK