import json
import falcon
import hmac
from hashlib import sha256
from cerberus import Validator

from look.app import app
from look.config import Config

from . import client, my_token, others_token, admin_token

v = Validator()

def test_gqlquery(client):
    doc = {
        "post": {
            "edges": [
                {
                    "node": {
                        "content": "post 1",
                        "userId": 1,
                        "comments": {
                            "edges": [
                                {
                                    "node": {
                                        "content": "comment 1",
                                        "childComments": {
                                            "edges": [
                                                {
                                                    "node": {
                                                        "content": "comment 1-1"
                                                    }
                                                },
                                                {
                                                    "node": {
                                                        "content": "comment 1-2"
                                                    }
                                                }
                                            ]
                                        }
                                    }
                                }
                            ]
                        }
                    }
                }
            ]
        }
    }

    body = {
        "query": '''
            query {
                post(filters: {id: 1}) {
                    edges {
                        node {
                            content,
                            userId,
                            comments(filters: {id: 1}) {
                                edges {
                                    node {
                                        content
                                        childComments {
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
                    }
                }
            }
        '''
    }

    response = client.simulate_post('/api/graphql', content_type='application/json', body=json.dumps(body))
    result_doc = json.loads(response.content.decode())

    assert result_doc == doc
    assert response.status == falcon.HTTP_OK