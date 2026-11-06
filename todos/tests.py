import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient, APITestCase
from rest_framework import status

from django.urls import reverse
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
            "name": "New User",
            "email": "newuser@example.com",
            "password": "StrongPassword123!"
        },
        format="json"
    )

    assert response.status_code == 201

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

@pytest.mark.django_db
def test_update_own_todo(client, user_a, todo):
    client.force_authenticate(user=user_a)

    response = client.patch(
        f"/api/todos/{todo.id}/",
        {"title": "Updated title"},
        format="json"
    )

    assert response.status_code == 200
    assert response.data["title"] == "Updated title"


@pytest.mark.django_db
def test_delete_own_todo(client, user_a, todo):
    client.force_authenticate(user=user_a)

    response = client.delete(f"/api/todos/{todo.id}/")

    assert response.status_code == 204


@pytest.mark.django_db
def test_register_duplicate_email(client, user_a):
    response = client.post(
        "/api/auth/register/",
        {
            "name": "Another User",
            "email": user_a.email,
            "password": "StrongPassword123!"
        },
        format="json"
    )

    assert response.status_code == 400


class TodoQueryTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='queryuser',
            password='StrongPassword123!'
        )

        self.client.force_authenticate(user=self.user)

        Todo.objects.create(
            user=self.user,
            title='Django tutorial',
            is_completed=False
        )

        Todo.objects.create(
            user=self.user,
            title='Python programming',
            is_completed=True
        )

        Todo.objects.create(
            user=self.user,
            title='Django REST framework',
            is_completed=True
        )

        self.url = '/api/todos/'

    def test_search_by_title(self):
        response = self.client.get(
            self.url,
            {'search': 'django'}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_filter_completed(self):
        response = self.client.get(
            self.url,
            {'status': 'completed'}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_filter_pending(self):
        response = self.client.get(
            self.url,
            {'status': 'pending'}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_sort_by_title_ascending(self):
        response = self.client.get(
            self.url,
            {'sort_by': 'title', 'order': 'asc'}
        )

        titles = [
            todo['title']
            for todo in response.data['results']
        ]

        self.assertEqual(
            titles,
            ['Django REST framework', 'Django tutorial', 'Python programming']
        )

    def test_sort_by_title_descending(self):
        response = self.client.get(
            self.url,
            {'sort_by': 'title', 'order': 'desc'}
        )

        titles = [
            todo['title']
            for todo in response.data['results']
        ]

        self.assertEqual(
            titles,
            [
                'Python programming',
                'Django tutorial',
                'Django REST framework'
            ]
        )

    def test_invalid_sort_field(self):
        response = self.client.get(
            self.url,
            {'sort_by': 'invalid'}
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_invalid_sort_order(self):
        response = self.client.get(
            self.url,
            {'order': 'random'}
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    
    def test_invalid_status(self):
        response = self.client.get(
            self.url,
            {'status': 'invalid'}
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertEqual(response.data['code'], 400)
        self.assertIn('error', response.data)

    def test_pagination(self):
        response = self.client.get(
            self.url,
            {'page': 1, 'limit': 2}
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(response.data['count'], 3)
        self.assertEqual(len(response.data['results']), 2)

    def test_second_page_pagination(self):
        response = self.client.get(
            self.url,
            {'page': 2, 'limit': 2}
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(len(response.data['results']), 1)

    def test_error_response_structure_for_invalid_sort(self):
        response = self.client.get(
            self.url,
            {'sort_by': 'invalid'}
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(
            set(response.data.keys()),
            {'error', 'code'}
        )

    def test_search_returns_no_results_for_unknown_title(self):
        response = self.client.get(
            self.url,
            {'search': 'nonexistent'}
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(response.data['results'], [])
