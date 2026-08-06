
from database.models import Category
from database.repositories.base_repo import BaseRepo


class CategoryRepo(BaseRepo):

    def get_categories(self) -> list[Category]:

        rows = self._fetch_all("""
            SELECT * FROM categories
        """)

        return [Category.from_dict(row) for row in rows]


    def create_category(self, new_category: Category) -> None:

        self._execute("""
            INSERT INTO categories(name)
            VALUES (%s)
        """, (new_category.name,))


    def update_category(self, updated_category: Category, initial_category_id: int) -> None:

        self._execute("""
            UPDATE categories
            SET name = %s
            WHERE id = %s
        """, (updated_category.name, initial_category_id))


    def delete_category(self, category_id: int) -> None:

        self._execute("""
            DELETE FROM categories
            WHERE id = %s
        """, (category_id, ))