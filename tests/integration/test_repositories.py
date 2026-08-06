from datetime import date, timedelta
from decimal import Decimal

from database.models import Category, Expense
from database.repositories.category_repo import CategoryRepo
from database.repositories.expense_repo import ExpenseRepo


class FakeCursor:
    def __init__(self, fetchone_result=None, fetchall_result=None):
        self.fetchone_result = fetchone_result
        self.fetchall_result = fetchall_result
        self.executed = None

    def execute(self, query, params=()):
        self.executed = (query, params)

    def fetchone(self):
        return self.fetchone_result

    def fetchall(self):
        return self.fetchall_result

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class FakeConnection:
    def __init__(self, cursor):
        self.cursor_obj = cursor

    def cursor(self, row_factory=None):
        return self.cursor_obj

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def test_category_repo_maps_rows_to_categories():
    cursor = FakeCursor(fetchall_result=[{"id": 1, "name": "Food"}])
    repo = CategoryRepo(FakeConnection(cursor))

    categories = repo.get_categories()

    assert categories == [Category(id=1, name="Food")]
    assert cursor.executed[0].strip() == "SELECT * FROM categories"


def test_category_repo_inserts_without_manual_id():
    cursor = FakeCursor()
    repo = CategoryRepo(FakeConnection(cursor))

    repo.create_category(Category(id=99, name="Food"))

    assert cursor.executed == (
        """
            INSERT INTO categories(name)
            VALUES (%s)
        """,
        ("Food",),
    )


def test_expense_repo_builds_open_ended_end_date_query():
    cursor = FakeCursor(fetchall_result=[])
    repo = ExpenseRepo(FakeConnection(cursor))

    repo.get_expenses(
        user_id=6,
        start_date=date(2026, 8, 1),
        end_date=date(2026, 8, 31),
        limit=10,
    )

    query, params = cursor.executed
    assert "created_at < %s" in query
    assert params[-2] == date(2026, 9, 1)
    assert params[-1] == 10


def test_expense_repo_maps_rows_to_expenses():
    cursor = FakeCursor(
        fetchall_result=[
            {
                "id": 1,
                "cost": Decimal("12.50"),
                "description": "Coffee",
                "category_id": 2,
                "user_id": 6,
                "created_at": None,
            }
        ]
    )
    repo = ExpenseRepo(FakeConnection(cursor))

    expenses = repo.get_expenses(user_id=6)

    assert expenses == [
        Expense(
            id=1,
            cost=Decimal("12.50"),
            description="Coffee",
            category_id=2,
            user_id=6,
            created_at=None,
        )
    ]
