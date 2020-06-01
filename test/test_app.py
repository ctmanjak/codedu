import os
import json
import falcon
from falcon import testing
import pytest

from look.app import app

@pytest.fixture
def client():
    return testing.TestClient(app)


# pytest will inject the object returned by the "client" function
# as an additional parameter.
def test_root(client):
    doc = "codedu"
    
    response = client.simulate_get('/')
    result_doc = response.content.decode()

    assert result_doc == doc
    assert response.status == falcon.HTTP_OK

def test_init(client):
    response = client.simulate_delete('/test/db/all')

    assert response.status == falcon.HTTP_OK

def test_insert_user(client):
    doc = {
        "success": True,
        "description": "",
        "data": {},
    }

    body = {
        "username": "testuser2",
        "email": "test@email.com",
        "password": "testpassword",
    }

    response = client.simulate_post('/api/db/user', content_type='application/json', body=json.dumps(body))
    result_doc = json.loads(response.content.decode())

    assert result_doc == doc
    assert response.status == falcon.HTTP_OK

# def test_insert_category(client):
#     doc = {
#         "success": True,
#         "description": "",
#         "data": {},
#     }

#     body = {
#         "username": "testuser2",
#         "email": "test@email.com",
#         "password": "testpassword",
#     }

#     response = client.simulate_post('/api/user', content_type='application/json', body=json.dumps(body))
#     result_doc = json.loads(response.content.decode())

#     assert result_doc == doc
#     assert response.status == falcon.HTTP_OK

def test_final(client):
    response = client.simulate_delete('/test/db/all')

    assert response.status == falcon.HTTP_OK
