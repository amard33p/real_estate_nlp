import sqlite3
from typing import List, Dict

from langchain_community.utilities.sql_database import SQLDatabase

PROJECTS_DB_PATH = "rera_projects.db"


class SQLiteDatabase:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.dialect = "sqlite"

    def run(self, query: str) -> List[Dict[str, any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query)
            results = [dict(row) for row in cursor.fetchall()]
        return results

    def get_table_info(self) -> str:
        return SQLDatabase.from_uri(f"sqlite:///{self.db_path}").get_table_info()


def get_db_connection() -> SQLiteDatabase:
    return SQLiteDatabase(PROJECTS_DB_PATH)
