from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from database.models import Expense
from exceptions import AuthorizationError, NotFoundError, ValidationError
from services.expense_service import add_expense, check_ownership, delete_expense, update_expense


def make_expense(**overrides) -> Expense:
    defaults = dict(
        id=1,
        cost=Decimal("25.00"),
        description="Test expense",
        category_id=1,
        user_id=6,
        created_at=None,
    )
    defaults.update(overrides)
    return Expense(**defaults)


def test_check_ownership_raises_not_found_when_expense_missing():
    repo = MagicMock()
    repo.get_expense_owner_id.return_value = None

    with pytest.raises(NotFoundError):
        check_ownership(repo, user_id=6, expense_id=99)


def test_check_ownership_raises_authorization_error_when_not_owner():
    repo = MagicMock()
    repo.get_expense_owner_id.return_value = 42

    with pytest.raises(AuthorizationError):
        check_ownership(repo, user_id=6, expense_id=1)


def test_check_ownership_passes_silently_when_owner_matches():
    repo = MagicMock()
    repo.get_expense_owner_id.return_value = 6

    check_ownership(repo, user_id=6, expense_id=1)


def test_add_expense_success():
    repo = MagicMock()
    expected = make_expense()
    repo.create_expense.return_value = expected

    result = add_expense(
        repo,
        user_id=6,
        cost=Decimal("25.00"),
        description="Test expense",
        category_id=1,
    )

    assert result == expected
    repo.create_expense.assert_called_once()


def test_add_expense_rejects_negative_cost():
    repo = MagicMock()

    with pytest.raises(ValidationError):
        add_expense(
            repo,
            user_id=6,
            cost=Decimal("-5.00"),
            description="Invalid",
            category_id=1,
        )
    repo.create_expense.assert_not_called()


def test_add_expense_rejects_missing_category():
    repo = MagicMock()

    with pytest.raises(ValidationError):
        add_expense(
            repo,
            user_id=6,
            cost=Decimal("10.00"),
            description="No category",
            category_id=None,
        )
    repo.create_expense.assert_not_called()


def test_update_expense_success():
    repo = MagicMock()
    repo.get_expense_owner_id.return_value = 6
    updated = make_expense(cost=Decimal("30.00"))
    repo.update_expense.return_value = updated

    result = update_expense(repo, updated)

    assert result == updated
    repo.update_expense.assert_called_once_with(updated)


def test_update_expense_raises_not_found():
    repo = MagicMock()
    repo.get_expense_owner_id.return_value = None
    expense = make_expense(id=999)

    with pytest.raises(NotFoundError):
        update_expense(repo, expense)
    repo.update_expense.assert_not_called()


def test_update_expense_raises_authorization_error_for_wrong_owner():
    repo = MagicMock()
    repo.get_expense_owner_id.return_value = 42
    expense = make_expense(user_id=6)

    with pytest.raises(AuthorizationError):
        update_expense(repo, expense)
    repo.update_expense.assert_not_called()


def test_update_expense_rejects_invalid_cost():
    repo = MagicMock()
    repo.get_expense_owner_id.return_value = 6
    expense = make_expense(cost=Decimal("-1.00"))

    with pytest.raises(ValidationError):
        update_expense(repo, expense)
    repo.update_expense.assert_not_called()


def test_delete_expense_success():
    repo = MagicMock()
    repo.get_expense_owner_id.return_value = 6

    delete_expense(repo, user_id=6, expense_id=1)

    repo.delete_expense.assert_called_once_with(1)


def test_delete_expense_raises_not_found():
    repo = MagicMock()
    repo.get_expense_owner_id.return_value = None

    with pytest.raises(NotFoundError):
        delete_expense(repo, user_id=6, expense_id=99)
    repo.delete_expense.assert_not_called()


def test_delete_expense_raises_authorization_error():
    repo = MagicMock()
    repo.get_expense_owner_id.return_value = 42

    with pytest.raises(AuthorizationError):
        delete_expense(repo, user_id=6, expense_id=1)
    repo.delete_expense.assert_not_called()
