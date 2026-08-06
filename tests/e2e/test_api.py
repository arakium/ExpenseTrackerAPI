from decimal import Decimal

import app as app_module


class FakeUser:
    def __init__(self):
        self.id = 1
        self.username = "alice"
        self.email = "alice@example.com"
        self.first_name = "Alice"
        self.last_name = "Smith"
        self.created_at = None

    def to_public_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "created_at": self.created_at,
        }


class FakeExpense:
    def __init__(self):
        self.id = 7
        self.cost = Decimal("25.00")
        self.description = "Lunch"
        self.category_id = 2
        self.user_id = 1
        self.created_at = None

    def to_dict(self):
        return {
            "id": self.id,
            "cost": str(self.cost),
            "description": self.description,
            "category_id": self.category_id,
            "user_id": self.user_id,
            "created_at": self.created_at,
        }


def test_signup_route_returns_created(monkeypatch):
    monkeypatch.setattr(app_module, "get_connection", lambda: object())
    monkeypatch.setattr(app_module.user_service, "signup", lambda *args, **kwargs: FakeUser())

    client = app_module.app.test_client()
    response = client.post(
        "/signup",
        json={
            "username": "alice",
            "email": "alice@example.com",
            "first_name": "Alice",
            "last_name": "Smith",
            "password": "password123",
        },
    )

    assert response.status_code == 201
    assert response.get_json()["username"] == "alice"


def test_create_expense_route_returns_created(monkeypatch):
    monkeypatch.setattr(app_module, "get_connection", lambda: object())
    monkeypatch.setattr(app_module, "get_current_user_id", lambda auth_header: 1)
    monkeypatch.setattr(app_module, "add_expense", lambda **kwargs: FakeExpense())

    client = app_module.app.test_client()
    response = client.post(
        "/expenses",
        headers={"Authorization": "Bearer token"},
        json={"cost": "25.00", "description": "Lunch", "category_id": 2},
    )

    assert response.status_code == 201
    assert response.get_json()["user_id"] == 1


def test_create_expense_route_rejects_missing_fields(monkeypatch):
    monkeypatch.setattr(app_module, "get_current_user_id", lambda auth_header: 1)

    client = app_module.app.test_client()
    response = client.post(
        "/expenses",
        headers={"Authorization": "Bearer token"},
        json={"description": "Lunch"},
    )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": {
            "cost": "This field is required.",
            "category_id": "This field is required.",
        }
    }


def test_update_expense_route_rejects_missing_body(monkeypatch):
    monkeypatch.setattr(app_module, "get_current_user_id", lambda auth_header: 1)

    client = app_module.app.test_client()
    response = client.put(
        "/expenses/7",
        headers={"Authorization": "Bearer token"},
        data="not-json",
        content_type="application/json",
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "Request body must be a JSON object."}


def test_update_expense_route_rejects_missing_required_fields(monkeypatch):
    monkeypatch.setattr(app_module, "get_current_user_id", lambda auth_header: 1)

    client = app_module.app.test_client()
    response = client.put(
        "/expenses/7",
        headers={"Authorization": "Bearer token"},
        json={"description": "Lunch"},
    )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": {
            "cost": "This field is required.",
            "category_id": "This field is required.",
        }
    }


def test_get_expenses_route_rejects_negative_limit(monkeypatch):
    monkeypatch.setattr(app_module, "get_current_user_id", lambda auth_header: 1)

    client = app_module.app.test_client()
    response = client.get(
        "/expenses?limit=-1",
        headers={"Authorization": "Bearer token"},
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "limit must be greater than 0."}


def test_get_expenses_route_rejects_bad_authorization_header():
    client = app_module.app.test_client()
    response = client.get("/expenses", headers={"Authorization": "token"})

    assert response.status_code == 401
    assert response.get_json() == {"error": "Missing or invalid authorization token."}


def test_get_expenses_route_rejects_non_integer_limit(monkeypatch):
    monkeypatch.setattr(app_module, "get_current_user_id", lambda auth_header: 1)

    client = app_module.app.test_client()
    response = client.get(
        "/expenses?limit=abc",
        headers={"Authorization": "Bearer token"},
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "limit must be a valid integer."}


def test_get_expenses_route_rejects_unknown_filter(monkeypatch):
    monkeypatch.setattr(app_module, "get_current_user_id", lambda auth_header: 1)

    client = app_module.app.test_client()
    response = client.get(
        "/expenses?filter=year",
        headers={"Authorization": "Bearer token"},
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": {"error": "Unsupported filter type: year"}}


def test_get_expenses_route_rejects_custom_filter_without_dates(monkeypatch):
    monkeypatch.setattr(app_module, "get_current_user_id", lambda auth_header: 1)

    client = app_module.app.test_client()
    response = client.get(
        "/expenses?filter=custom",
        headers={"Authorization": "Bearer token"},
    )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": {"error": "Custom filter requires start_date and end_date"}
    }


def test_create_expense_route_rejects_json_array(monkeypatch):
    monkeypatch.setattr(app_module, "get_current_user_id", lambda auth_header: 1)

    client = app_module.app.test_client()
    response = client.post(
        "/expenses",
        headers={"Authorization": "Bearer token"},
        json=["not", "an", "object"],
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "Request body must be a JSON object."}
