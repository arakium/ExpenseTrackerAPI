from typing import LiteralString

import psycopg
from psycopg.rows import dict_row


class BaseRepo:
    def __init__(self, db_connection: psycopg.Connection):
        self.connection = db_connection

    def _execute(self, query: LiteralString, params: tuple = ()) -> None:
        with self.connection:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)

    def _fetch_one(self, query: LiteralString, params: tuple = ()) -> dict | None:
        with self.connection:
            with self.connection.cursor(row_factory=dict_row) as cursor:
                cursor.execute(query, params)
                return cursor.fetchone()

    def _fetch_all(self, query: LiteralString, params: tuple = ()) -> list[dict]:
        with self.connection:
            with self.connection.cursor(row_factory=dict_row) as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()