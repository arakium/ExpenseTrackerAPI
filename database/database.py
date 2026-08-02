"""Setup main database and tables using PostgreSQL."""
from config.db_config import database_config
import psycopg


def get_connection() -> psycopg.Connection:
    """Establish a connection to database and return connection object."""
    params = database_config()
    conn = psycopg.connect(**params)
    return conn


def init_db() -> None:
    """Initializes database with the main schema"""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                    CREATE TABLE IF NOT EXISTS users(
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(30) NOT NULL UNIQUE,
                        email VARCHAR(60) NOT NULL UNIQUE,
                        first_name VARCHAR(40) NOT NULL,
                        last_name VARCHAR(40) NOT NULL,
                        password_hash text NOT NULL,
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                    );
                    CREATE TABLE IF NOT EXISTS categories(
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(30) NOT NULL UNIQUE
                    );
                    CREATE TABLE IF NOT EXISTS expenses(
                        id SERIAL PRIMARY KEY,
                        cost numeric(12,2) NOT NULL CHECK ( cost>0 ),
                        description varchar(255),
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        category_id INTEGER NOT NULL,
                        user_id INTEGER NOT NULL,
                    
                        CONSTRAINT fk_category
                            FOREIGN KEY (category_id)
                            REFERENCES categories(id)
                            ON UPDATE CASCADE
                            ON DELETE RESTRICT,
                    
                        CONSTRAINT fk_user
                            FOREIGN KEY (user_id)
                            REFERENCES users(id)
                            ON UPDATE CASCADE
                            ON DELETE CASCADE
                );
            """)

if __name__ == "__main__":
    init_db()