import falcon
from falcon import testing
import pytest

from look.app import app

@pytest.fixture
def client():
    return testing.TestClient(app)

# pytest will inject the object returned by the "client" function
# as an additional parameter.
def test_root_page(client):
    doc = "codedu"
    
    response = client.simulate_get('/')
    result_doc = response.content.decode()

    assert result_doc == doc
    assert response.status == falcon.HTTP_OK

def test_init_db(client):
    response = client.simulate_delete('/test/db')
    response2 = client.simulate_get('/test/db')

    assert response.status == falcon.HTTP_OK
    assert response2.status == falcon.HTTP_OK