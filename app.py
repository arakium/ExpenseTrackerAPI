from flask import Flask, request, jsonify
from database.database import get_connection
from database.models import Expense
from database.repositories.expense_repo import ExpenseRepo
from database.repositories.user_repo import UserRepo
from exceptions import AppError, ValidationError
from services import user_service, expense_service
from services.auth_service import login, get_current_user_id
from services.expense_service import add_expense
from utils.date_filter import filter_date

app = Flask(__name__)


def _require_json_object():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ValidationError("Request body must be a JSON object.")
    return data


def _require_fields(data: dict, fields: tuple[str, ...]) -> None:
    missing = [field for field in fields if field not in data]
    if missing:
        raise ValidationError({field: "This field is required." for field in missing})

@app.errorhandler(AppError)
def handle_app_error(e: AppError):
    """Catches ANY AppError raised anywhere in the app and formats it."""
    return jsonify({"error": e.errors}), e.status_code

@app.route("/signup", methods=["POST"])
def signup_route():
    data = _require_json_object()
    repo = UserRepo(get_connection())
    user = user_service.signup(
        repo,
        username=data.get("username"),
        email=data.get("email"),
        firstname=data.get("first_name"),
        lastname=data.get("last_name"),
        plain_password=data.get("password"),
    )
    return jsonify(user.to_public_dict()), 201

@app.route("/login", methods=["POST"])
def login_route():
    data = _require_json_object()
    repo = UserRepo(get_connection())
    token = login(repo, data.get("identifier"), data.get("password"))
    return jsonify({"token": token}), 200

@app.route ("/expenses", methods=["GET"])
def get_expenses_route():
    auth_header = request.headers.get("Authorization")
    user_id = get_current_user_id(auth_header)
    filter_type = request.args.get("filter")
    start_date, end_date = None, None
    if filter_type is not None:
        start_date, end_date = filter_date(request, filter_type)
    limit_str = request.args.get("limit")
    limit = None
    if limit_str is not None:
        try:
            limit = int(limit_str)
        except ValueError:
            raise ValidationError("limit must be a valid integer.")
        if limit < 1:
            raise ValidationError("limit must be greater than 0.")
    repo = ExpenseRepo(get_connection())
    expenses = repo.get_expenses(user_id, start_date, end_date, limit)
    return jsonify([expense.to_dict() for expense in expenses]), 200

@app.route ("/expenses", methods=["POST"])
def create_expense_route():
    auth_header = request.headers.get("Authorization")
    user_id = get_current_user_id(auth_header)
    data = _require_json_object()
    _require_fields(data, ("cost", "category_id"))
    repo = ExpenseRepo(get_connection())
    expense = add_expense(
        repo=repo,
        cost = data.get("cost"),
        description = data.get("description"),
        category_id= data.get("category_id"),
        user_id = user_id
    )
    return jsonify(expense.to_dict()), 201

@app.route ("/expenses/<int:expense_id>", methods=["DELETE"])
def delete_expense_route(expense_id):
    auth_header = request.headers.get("Authorization")
    user_id = get_current_user_id(auth_header)
    repo = ExpenseRepo(get_connection())
    expense_service.delete_expense(repo, user_id, expense_id)
    return "", 204

@app.route("/expenses/<int:expense_id>", methods=["PUT"])
def update_expense_route(expense_id):
    auth_header = request.headers.get("Authorization")
    user_id = get_current_user_id(auth_header)
    data = _require_json_object()
    _require_fields(data, ("cost", "category_id"))

    repo = ExpenseRepo(get_connection())
    updated_expense = Expense(
        id=expense_id,
        user_id=user_id,
        cost=data["cost"],
        description=data.get("description"),
        category_id=data["category_id"],
    )

    result = expense_service.update_expense(repo, updated_expense)
    return jsonify(result.to_dict()), 200
