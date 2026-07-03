from pathlib import Path
from customer_data_platform.load.database import get_connection


def init_db(db_path: str | Path):
    with get_connection(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                customer_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                country TEXT NOT NULL
            )
        """)
