import pytest
import os
os.environ["DATABASE_URL"] = "sqlite:///test_todo.db"

from fastapi.testclient import TestClient
from main import app, Base, engine
import time

client = TestClient(app)
Base.metadata.create_all(engine)

# AUTH TESTS

def test_signup_success():
    email = f"user{int(time.time())}@example.com"
    response = client.post("/auth/signup", json={
        "email": email,
        "password": "password123"
    })
    assert response.status_code == 201
    assert response.json()["email"] == email

def test_signup_duplicate_email():
    client.post("/auth/signup", json={
        "email": "duplicate@example.com",
        "password": "password123"
    })
    response = client.post("/auth/signup", json={
        "email": "duplicate@example.com",
        "password": "password123"
    })
    assert response.status_code == 400

def test_login_success():
    client.post("/auth/signup", json={
        "email": "logintest@example.com",
        "password": "password123"
    })
    response = client.post("/auth/login", json={
        "email": "logintest@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    assert "accessToken" in response.json()

def test_login_wrong_password():
    response = client.post("/auth/login", json={
        "email": "logintest@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401

# TASK TESTS


def get_token():
    email = f"taskuser{int(time.time())}@example.com"
    client.post("/auth/signup", json={
        "email": email,
        "password": "password123"
    })
    response = client.post("/auth/login", json={
        "email": email,
        "password": "password123"
    })
    return response.json()["accessToken"]

def test_create_task():
    token = get_token()
    response = client.post("/tasks",
        json={"title": "Test Task", "description": "Test description"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    assert response.json()["title"] == "Test Task"

def test_get_tasks():
    token = get_token()
    client.post("/tasks",
        json={"title": "My Task"},
        headers={"Authorization": f"Bearer {token}"}
    )
    response = client.get("/tasks",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "data" in response.json()

def test_update_task():
    token = get_token()
    create = client.post("/tasks",
        json={"title": "Original Title"},
        headers={"Authorization": f"Bearer {token}"}
    )
    task_id = create.json()["id"]
    response = client.put(f"/tasks/{task_id}",
        json={"completed": True},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["completed"] == True

def test_delete_task():
    token = get_token()
    create = client.post("/tasks",
        json={"title": "Task to delete"},
        headers={"Authorization": f"Bearer {token}"}
    )
    task_id = create.json()["id"]
    response = client.delete(f"/tasks/{task_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 204

def test_get_tasks_without_token():
    response = client.get("/tasks")
    assert response.status_code == 401

def test_create_task_without_title():
    token = get_token()
    response = client.post("/tasks",
        json={"description": "No title here"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 422