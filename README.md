# The Scroll of Procrastination
A TODO management REST API built with **Django REST Framework**.

## Features
- User registration and JWT authentication.
- Create, retrieve, update, and delete TODOs.
- User-specific TODO management.
- Filter TODOs by completion status.
- Search TODOs by title.
- Sort TODOs by creation date or title.
- Paginated TODO listing.
- Input validation and consistent error responses.
- Request logging.
- Interactive API documentation using Swagger UI.

## Tech Stack
- Python 3.12
- Django 5.2
- Django REST Framework
- Simple JWT
- SQLite
- drf-spectacular
- pytest

## Project Setup

### 1. Clone the repository
```bash
git clone https://github.com/tanvir-005/the-scroll-of-procrastination.git
cd the-scroll-of-procrastination
```

### 2. Create a virtual environment
```bash
python -m venv .venv
```
Activate it:
**Linux/macOS**
```bash
source .venv/bin/activate
```
**Windows**
```bash
.venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Copy the example environment file and update it for your local setup:

```bash
cp .env.example .env
```

Then update your `.env` file:

```env
SECRET_KEY=your-django-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
MAX_REQUESTS=30
```

Generate a Django secret key using:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 5. Apply migrations
```bash
python manage.py migrate
```

### 6. Start the development server
Make sure your `.env` file exists and contains the required values, then run:

```bash
python manage.py runserver
```

### 7. Or run with Docker Compose
```bash
docker compose up --build
```

The API base URL is:
`http://127.0.0.1:8000/api/`

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register/` | Register with `name`, `email`, and `password` |
| POST | `/api/auth/login/` | Obtain JWT access and refresh tokens |
| POST | `/api/auth/refresh/` | Refresh an access token |

### TODO Management

All TODO endpoints require JWT authentication.

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/todos/` | List TODOs |
| POST | `/api/todos/` | Create a TODO |
| GET | `/api/todos/<id>/` | Retrieve a TODO |
| PUT | `/api/todos/<id>/` | Update a TODO |
| PATCH | `/api/todos/<id>/` | Partially update a TODO |
| DELETE | `/api/todos/<id>/` | Delete a TODO |

### JWT Authentication

Include your access token in the request header:

```http
Authorization: Bearer YOUR_ACCESS_TOKEN
```

Register a user with:

```json
{"name":"Your Name","email":"you@example.com","password":"StrongPassword123!"}
```

The API generates a unique username from the email local part (for example, `you` or `you1`). Log in using that generated username and your password:

```json
{"username":"you","password":"StrongPassword123!"}
```

Successful registration returns a status message and the created user summary:

```json
{
  "message": "User registered successfully.",
  "user": {
    "id": 1,
    "username": "you",
    "email": "you@example.com"
  }
}
```

Successful login returns JWT tokens:

```json
{
  "refresh": "YOUR_REFRESH_TOKEN",
  "access": "YOUR_ACCESS_TOKEN"
}
```

When the access token expires, send the `refresh` token to `/api/auth/refresh/`:

```json
{"refresh":"YOUR_REFRESH_TOKEN"}
```

The response returns a fresh access token:

```json
{
  "access": "NEW_ACCESS_TOKEN"
}
```

## Rate Limiting

Requests to `/api/` are limited by client IP over a rolling 60-second window. Set `MAX_REQUESTS` in `.env` to change the number of requests allowed per IP; the example configuration allows 30. Requests above the limit return `429 Too Many Requests` with the standard error shape:

```json
{
  "error": "Too many requests.",
  "code": 429
}
```

The limit is loaded when the server starts, so restart the server after changing `MAX_REQUESTS`. Request counts are held in process memory, reset on restart, and are not shared across multiple server processes; this implementation is intended for local or single-process use, not production-scale rate limiting.

### TODO Query Parameters

The TODO listing endpoint supports:

| Parameter | Example | Description |
|---|---|---|
| `page` | `?page=2` | Select page |
| `limit` | `?limit=10` | Number of results per page |
| `status` | `?status=completed` | Filter by `completed` or `pending` |
| `search` | `?search=groceries` | Search TODO titles |
| `sort_by` | `?sort_by=title` | Sort by `created_at` or `title` |
| `order` | `?order=asc` | Sort direction: `asc` or `desc` |

Example:

```http
GET /api/todos/?status=pending&search=groceries&sort_by=created_at&order=desc&page=1&limit=10
```

## API Documentation

Interactive Swagger documentation:

`http://127.0.0.1:8000/api/docs/`

OpenAPI schema:

`http://127.0.0.1:8000/api/schema/`

## Running Tests

Run the test suite:

```bash
pytest -v
```

Validate the OpenAPI schema:

```bash
python manage.py spectacular --file schema.yml --validate
```

## Error Response Format

API errors follow a consistent structure:

```json
{
  "error": "Validation failed.",
  "code": 400
}
```

This is the same shape returned by validation failures and invalid query parameters.

## Project Structure

```text
the-scroll-of-procrastination/
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── todos/
│   ├── migrations/
│   ├── middleware/
│   ├── utils/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── tests.py
├── manage.py
├── requirements.txt
├── pytest.ini
├── schema.yml
└── README.md
```

## Notes

- Each authenticated user can access and manage only their own TODOs.
- The SQLite database is created locally through Django migrations.
- TODO lists return 10 items per page by default; `limit` can be set up to 50.
- After changing a model, create and apply migrations with `python manage.py makemigrations` and `python manage.py migrate`.
- Request logs are written to `logs/django.log` and include the method, path, status, duration, and username when available.
- Keep `.env` and other secret files out of version control.
