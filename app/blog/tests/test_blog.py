from fastapi.testclient import TestClient

from ...main import app

# client = TestClient(app)

from fastapi.testclient import TestClient
from app.main import app
from app.blog.models import User

client = TestClient(app)

def get_authenticated_client():
    # Create a new user
    test_user = {"name": "Test User", "email": "test@example.com", "password": "password"}
    # Log in with the newly created user
    login_data = {"username": test_user["email"], "password": test_user["password"]}
    response = client.post("/login/", data=login_data)
    assert response.status_code == 200
    access_token = response.json()["access_token"]
    return TestClient(app, headers={"Authorization": f"Bearer {access_token}"})

# Now, use the authenticated client for making requests in your tests
authenticated_client = get_authenticated_client()


def test_get_all_blogs():
    response = authenticated_client.get("/blog/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_blog():
    # Assuming valid request data
    request_data = {"title": "Test Blog", "body": "This is a test blog."}
    response = authenticated_client.post("/blog/", json=request_data)
    assert response.status_code == 201
    assert response.json().get("id") is not None

def test_create_blog_invalid_data():
    # Assuming invalid request data
    request_data = {"title": "Test Blog"}  # Missing 'body' field
    response = authenticated_client.post("/blog/", json=request_data)
    assert response.status_code == 422  # Unprocessable Entity
    assert "detail" in response.json()

def test_delete_blog():
    # Assuming an existing blog id
    blog_id = 1  # Assuming blog with id=1 exists
    response = authenticated_client.delete(f"/blog/{blog_id}")
    assert response.status_code == 204  # No Content

def test_delete_nonexistent_blog():
    # Assuming a non-existing blog id
    blog_id = 9999  # Non-existing blog id
    response = authenticated_client.delete(f"/blog/{blog_id}")
    assert response.status_code == 404  # Not Found

def test_update_blog():
    # Assuming an existing blog id and valid request data
    blog_id = 1  # Assuming blog with id=1 exists
    request_data = {"title": "Updated Title", "body": "Updated body content."}
    response = authenticated_client.put(f"/blog/{blog_id}", json=request_data)
    assert response.status_code == 202  # Accepted
    assert response.json().get("title") == "Updated Title"
    assert response.json().get("body") == "Updated body content."

def test_update_nonexistent_blog():
    # Assuming a non-existing blog id
    blog_id = 9999  # Non-existing blog id
    request_data = {"title": "Updated Title", "body": "Updated body content."}
    response = authenticated_client.put(f"/blog/{blog_id}", json=request_data)
    assert response.status_code == 404  # Not Found

def test_get_blog():
    # Assuming an existing blog id
    blog_id = 1  # Assuming blog with id=1 exists
    response = authenticated_client.get(f"/blog/{blog_id}")
    assert response.status_code == 200
    assert response.json().get("id") == blog_id

def test_get_nonexistent_blog():
    # Assuming a non-existing blog id
    blog_id = 9999  # Non-existing blog id
    response = authenticated_client.get(f"/blog/{blog_id}")
    assert response.status_code == 404  # Not Found
