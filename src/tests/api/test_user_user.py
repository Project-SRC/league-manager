from fastapi.testclient import TestClient
from main import league as app

client = TestClient(app)


# DOC: How to test with Fast API -> https://fastapi.tiangolo.com/tutorial/testing/
def test_base_path():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}
