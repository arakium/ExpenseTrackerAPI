# ExpenseTracker API

Flask + PostgreSQL expense tracking API with JWT authentication, user-scoped expense CRUD, and pytest test layers (unit, integration, end-to-end).

## Features

- User signup and login
- JWT-based authorization (`Authorization: Bearer <token>`)
- Expense CRUD scoped to the authenticated user
- Expense listing with date filters (`week`, `month`, `3months`, `custom`)
- Defensive input validation for malformed JSON, missing fields, and invalid query params

## Requirements

- Python 3.13+
- PostgreSQL

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration

1. Create `.env` in project root:

```env
SECRET_JWT=your-strong-secret
```

2. Update `config/database.ini` with your PostgreSQL credentials:

```ini
[postgresql]
host=localhost
dbname=mydb
user=your_user
password=your_password
port=5432
```

## Initialize Database

```bash
python database/database.py
```

This creates:
- `users`
- `categories`
- `expenses`

## Run API

```bash
flask --app app run --debug
```

Default local URL: `http://127.0.0.1:5000`

## API Endpoints

### Auth

- `POST /signup`
- `POST /login`
  - Returns: `{"token": "<jwt>"}` on success

JWT usage for protected routes:

```http
Authorization: Bearer <jwt>
```

### Expenses (auth required)

- `GET /expenses`
  - Query params:
    - `filter=week|month|3months|custom`
    - `start_date=YYYY-MM-DD` (custom only)
    - `end_date=YYYY-MM-DD` (custom only)
    - `limit=<positive integer>`
- `POST /expenses`
  - Required JSON fields: `cost`, `category_id`
  - Optional JSON fields: `description`
- `PUT /expenses/<expense_id>`
  - Optional JSON fields: `cost`, `category_id`, `description`
  - Omitted fields keep their existing DB values (partial update behavior)
- `DELETE /expenses/<expense_id>`

## Error Behavior

The API returns structured errors:

```json
{"error": "..."}
```

or field-level details:

```json
{"error": {"field_name": "message"}}
```

Common status codes:
- `400` validation errors
- `401` authentication errors
- `403` authorization errors
- `404` not found
- `409` conflict (e.g., duplicate username/email)

## Tests (pytest)

Test structure:

- `tests/unit` — service and utility logic
- `tests/integration` — repository behavior and query construction
- `tests/e2e` — API route behavior with Flask test client

Run all tests:

```bash
python -m pytest -q
```
