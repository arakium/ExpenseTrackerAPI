
from database.repositories.base_repo import BaseRepo
from database.models import Expense
class ExpenseRepo(BaseRepo):

    def get_expenses(self, user_id: int, limit: int = 10) -> list[Expense]:
        rows = self._fetch_all("""
            SELECT * FROM expenses
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s
        """, (user_id, limit))

        return [Expense(*row) for row in rows]


    def create_expense(self, expense: Expense) -> None:
        self._execute("""
            INSERT INTO expenses(cost, description, user_id, category_id)
            VALUES (%s, %s, %s , %s)
        """, (expense.cost, expense.description, expense.user_id, expense.category_id))

    def update_expense(self, new_expense: Expense, expense_id: int) -> None:
        self._execute("""
            UPDATE expenses
            SET
                cost = %s,
                description = %s,
                category_id = %s,
            WHERE id = %s
        """, (new_expense.cost, new_expense.description, new_expense.category_id, expense_id))

    def delete_expense(self, expense_id: int) -> None:
        self._execute("""
            DELETE FROM expenses
            WHERE id = %s
        """, (expense_id,))