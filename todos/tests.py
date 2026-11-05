import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from todos.models import Todo


@pytest.fixture
def user_a(db):
    return User.objects.create_user(
        username="user_a",
        password="StrongPassword123!"
    )

@pytest.fixture
def user_b(db):
    return User.objects.create_user(
        username="user_b",
        password="StrongPassword123!"
    )

@pytest.fixture
def client():
    return APIClient()

@pytest.fixture
def todo(user_a):
    return Todo.objects.create(
        user=user_a,
        title="Test TODO",
        description="Testing API"
    )



@pytest.mark.django_db
def test_register_user(client):
    response = client.post(
        "/api/auth/register/",
        {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "StrongPassword123!"
        },
        format="json"
    )

    assert response.status_code == 201
    assert User.objects.filter(username="newuser").exists()

@pytest.mark.django_db
def test_unauthenticated_user_cannot_list_todos(client):
    response = client.get("/api/todos/")

    assert response.status_code == 401

@pytest.mark.django_db
def test_authenticated_user_can_create_todo(client, user_a):
    client.force_authenticate(user=user_a)

    response = client.post(
        "/api/todos/",
        {
            "title": "New TODO",
            "description": "Created through API"
        },
        format="json"
    )

    assert response.status_code == 201
    assert Todo.objects.filter(
        user=user_a,
        title="New TODO"
    ).exists()



@pytest.mark.django_db
def test_user_can_only_see_own_todos(client, user_a, user_b, todo):
    client.force_authenticate(user=user_b)

    response = client.get("/api/todos/")

    assert response.status_code == 200
    assert response.data["count"] == 0

@pytest.mark.django_db
def test_user_cannot_retrieve_another_users_todo(
    client, user_b, todo
):
    client.force_authenticate(user=user_b)

    response = client.get(f"/api/todos/{todo.id}/")

    assert response.status_code == 404

@pytest.mark.django_db
def test_user_cannot_update_another_users_todo(
    client, user_b, todo
):
    client.force_authenticate(user=user_b)

    response = client.patch(
        f"/api/todos/{todo.id}/",
        {"title": "Hacked"},
        format="json"
    )

    assert response.status_code == 404

@pytest.mark.django_db
def test_user_cannot_delete_another_users_todo(
    client, user_b, todo
):
    client.force_authenticate(user=user_b)

    response = client.delete(f"/api/todos/{todo.id}/")

    assert response.status_code == 404
    assert Todo.objects.filter(id=todo.id).exists()

@pytest.mark.django_db
def test_user_can_retrieve_own_todo(client, user_a, todo):
    client.force_authenticate(user=user_a)

    response = client.get(f"/api/todos/{todo.id}/")

    assert response.status_code == 200
    assert response.data["title"] == "Test TODO"