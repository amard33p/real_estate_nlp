import sqlite3
from typing import List, Dict

KA_PROJECTS_DB_PATH = "karnataka_projects.db"


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
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()

            table_info = []
            for table in tables:
                table_name = table[0]
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = cursor.fetchall()
                column_names = [column[1] for column in columns]
                table_info.append(f"{table_name} ({', '.join(column_names)})")

            return "\n".join(table_info)


def get_db_connection() -> SQLiteDatabase:
    return SQLiteDatabase(KA_PROJECTS_DB_PATH)
