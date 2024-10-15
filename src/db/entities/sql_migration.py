from typing import List

from src.db.entities.base import BaseEntity


class SQLMigrations(BaseEntity):
    sql: str

    @classmethod
    def get_table_columns(cls) -> List[str]:
        return ["id", "sql", "created_at"]

    @classmethod
    def get_table_name(cls) -> str:
        return "sql_migrations"
