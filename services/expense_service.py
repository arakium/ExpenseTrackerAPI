from decimal import Decimal
from typing import cast

from pydantic import ValidationError as PydanticValidationError
from exceptions import ValidationError, format_pydantic_errors, NotFoundError, AuthorizationError
from database.models import Expense
from database.repositories.expense_repo import ExpenseRepo
from utils.validators import ValidateExpenseRequest

def check_ownership(repo: ExpenseRepo, user_id: int, expense_id: int) -> None:
    expense_owner_id = repo.get_expense_owner_id(expense_id)
    if expense_owner_id is None:
        raise NotFoundError("Expense doesn't exist.")
    if expense_owner_id != user_id:
        raise AuthorizationError("Current user doesn't have permission to access this resource.")

def add_expense(repo: ExpenseRepo, cost: Decimal, description: str, category_id: int, user_id: int):
    try:
        ValidateExpenseRequest(
            cost=cost,
            description=description,
            category_id=category_id,
            user_id=user_id
        )
    except PydanticValidationError as e:
        raise ValidationError(format_pydantic_errors(e))
    new_expense = Expense(
        cost = cost,
        description = description,
        category_id = category_id,
        user_id = user_id
    )
    return repo.create_expense(new_expense)

def delete_expense(repo: ExpenseRepo, user_id: int, expense_id: int) -> None:
    check_ownership(repo, user_id, expense_id)
    repo.delete_expense(expense_id)

def update_expense(repo: ExpenseRepo, updated_expense: Expense) -> Expense | None:
    try:
        ValidateExpenseRequest(
            cost=updated_expense.cost,
            description=updated_expense.description,
            category_id=updated_expense.category_id,
            user_id=updated_expense.user_id
        )
    except PydanticValidationError as e:
        raise ValidationError(format_pydantic_errors(e))
    check_ownership(repo, updated_expense.user_id, cast(int, updated_expense.id))
    return repo.update_expense(updated_expense)
