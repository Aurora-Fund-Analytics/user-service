import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from main import register
from src.auth import hash_password
from src.schemas import UserCreate
import json


def test_register_success():
    with patch('pymongo.MongoClient') as MockMongoClient:
        # Configure the mock db
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = None
        mock_collection.insert_one.return_value = {
            "_id": "123",
            "username": "testuser",
            "full_name": "Test User",
            "password_hash": hash_password("password"),
            "join_date": "2025-01-01T00:00:00Z"
        }
        MockMongoClient.return_value.db_name.collection_name = mock_collection
        
        payload = UserCreate(
            username="testuser",
            full_name="Test User",
            password="password"
        )
        response = register(user=payload, db_users=mock_collection)
        assert response.status_code == 200

def test_register_existing_user():
    with patch('pymongo.MongoClient') as MockMongoClient:
        # Configure the mock db
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = {"username": "testuser"}
        MockMongoClient.return_value.db_name.collection_name = mock_collection
        
        payload = UserCreate(
            username="testuser",
            full_name="Test User",
            password="password"
        )
        response = register(user=payload, db_users=mock_collection)
        body = json.loads(response.body.decode('utf-8'))
        assert response.status_code == 400
        assert body["details"] == "Username already exists"


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
