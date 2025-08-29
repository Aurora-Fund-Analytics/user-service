import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from main import app
from src.auth import hash_password

client = TestClient(app)


# Replace database.db_users collection with a mock Mongo collection
@pytest.fixture
def mock_users_collection():
    with patch("database.db_users") as mock_collection:
        yield mock_collection


def test_register_success(mock_users_collection):
    # When the app calls users_collection.find_one(...), it will get None (simulating "user does not exist").
    mock_users_collection.find_one.return_value = None
    # When the app calls insert_one(...), it pretends a new Mongo _id was created.
    mock_users_collection.insert_one.return_value.inserted_id = "123" 
    # Now the mock will return this dictionary (simulating the newly created user document).
    mock_users_collection.find_one.return_value = {
        "_id": "123",
        "username": "testuser",
        "full_name": "Test User",
        "password_hash": hash_password("password"),
        "join_date": "2025-01-01T00:00:00Z"
    }

    payload = {"username": "testuser", "full_name": "Test User", "password": "password"}
    response = client.post("/register", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["username"] == "testuser"
    assert body["full_name"] == "Test User"


# def test_register_existing_user(mock_users_collection):
#     mock_users_collection.find_one.return_value = {"username": "testuser"}
#     payload = {"username": "testuser", "full_name": "Test User", "password": "password"}

#     response = client.post("/register", json=payload)
#     assert response.status_code == 400
#     assert response.json()["detail"] == "Username already exists"


# def test_login_success(mock_users_collection):
#     mock_users_collection.find_one.return_value = {
#         "username": "testuser",
#         "password_hash": hash_password("password")
#     }

#     response = client.post("/login", data={"username": "testuser", "password": "password"})

#     assert response.status_code == 200
#     body = response.json()
#     assert "access_token" in body
#     assert body["token_type"] == "bearer"


# def test_login_invalid_password(mock_users_collection):
#     mock_users_collection.find_one.return_value = {
#         "username": "testuser",
#         "password_hash": hash_password("correctpass")
#     }

#     response = client.post("/login", data={"username": "testuser", "password": "wrongpass"})
#     assert response.status_code == 401
#     assert response.json()["detail"] == "Invalid username or password"


# def test_me_authenticated(mock_users_collection):
#     # Setup mock user
#     user_data = {
#         "_id": "123",
#         "username": "testuser",
#         "full_name": "Test User",
#         "password_hash": hash_password("password"),
#         "join_date": "2025-01-01T00:00:00Z"
#     }
#     mock_users_collection.find_one.return_value = user_data

#     # First login to get token
#     client.post("/register", json={"username": "testuser", "full_name": "Test User", "password": "password"})
#     login_response = client.post("/login", data={"username": "testuser", "password": "password"})
#     token = login_response.json()["access_token"]

#     # Call protected endpoint
#     response = client.get("/me", headers={"Authorization": f"Bearer {token}"})
#     assert response.status_code == 200
#     assert response.json()["username"] == "testuser"


# def test_me_unauthenticated():
#     response = client.get("/me")
#     assert response.status_code == 401
