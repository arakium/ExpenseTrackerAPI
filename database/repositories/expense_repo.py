from datetime import date
from typing import LiteralString, cast, Any

import psycopg

from database.repositories.base_repo import BaseRepo
from database.models import Expense
from exceptions import NotFoundError, ValidationError


class ExpenseRepo(BaseRepo):

    def get_expenses(self,
                     user_id: int,
                     start_date: date | None = None,
                     end_date: date | None = None,
                     limit: int | None = None) -> list[Expense]:

        query = "SELECT * FROM expenses WHERE user_id = %s"
        params: list[Any] = [user_id]

        if start_date is not None:
            query += " AND created_at >= %s"
            params.append(start_date)
        if end_date is not None:
            query += " AND created_at <= %s"
            params.append(end_date)

        query += " ORDER BY created_at DESC"
        if limit is not None:
            query += " LIMIT %s"
            params.append(limit)
        rows = self._fetch_all(cast(LiteralString, query), tuple(params))

        return [Expense.from_dict(row) for row in rows]

    def get_expense_owner_id(self, expense_id) -> int | None:
        owner_id =  self._fetch_one(
            """
            SELECT user_id 
            FROM expenses
            WHERE id = %s
            """,
            (expense_id,)
        )
        return owner_id["user_id"] if owner_id is not None else None

    def create_expense(self, expense: Expense) -> Expense:
        try:
            data = self._fetch_one("""
                    INSERT INTO expenses(cost, description, user_id, category_id)
                    VALUES (%s, %s, %s, %s)
                    RETURNING *
                    """, (
                expense.cost,
                expense.description,
                expense.user_id,
                expense.category_id))

        except psycopg.errors.ForeignKeyViolation as e:
            constraint = e.diag.constraint_name
            if constraint == "fk_category":
                raise ValidationError({"category_id": "The specified category does not exist."})
            elif constraint == "fk_user":
                raise ValidationError({"user_id": "The specified user does not exist."})
            else:
                raise ValidationError("A referenced resource could not be found.")
        except psycopg.errors.CheckViolation as e:
            constraint = e.diag.constraint_name
            if constraint == "expenses_cost_check":
                raise ValidationError({"cost": "Cost must be positive number."})
            else:
                raise ValidationError("A check constraint was violated.")

        if data is None:
            raise RuntimeError("Expense creation failed: no row returned from database")

        return Expense.from_dict(data)

    def update_expense(self, new_expense: Expense) -> Expense | None:
       try:
            data = self._fetch_one("""
                UPDATE expenses
                SET
                    cost = %s,
                    description = %s,
                    category_id = %s
                WHERE id = %s
                RETURNING *
            """, (new_expense.cost, new_expense.description, new_expense.category_id, new_expense.id))
            return Expense.from_dict(data) if data else None

       except psycopg.errors.ForeignKeyViolation:
           raise ValidationError({"category_id": "Specified category doesn't exist."})

    def delete_expense(self, expense_id: int) -> None:
        self._execute("""
            DELETE FROM expenses
            WHERE id = %s
        """, (expense_id,))
