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
Create a `.env` file in the project root:

```env
SECRET_KEY=your-django-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
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
```bash
python manage.py runserver
```

The API will be available at:
`http://127.0.0.1:8000/`

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/register/` | Register a new user |
| POST | `/api/token/` | Obtain JWT access and refresh tokens |
| POST | `/api/token/refresh/` | Refresh an access token |

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
- Keep `.env` and other secret files out of version control.
