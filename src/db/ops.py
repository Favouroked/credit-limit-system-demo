import json
import os
from typing import List, Literal, Type, TypeVar

import psycopg
from psycopg.rows import dict_row

from src.config import get_logger
from src.config.errors import NotFoundError
from src.constants.migration import (
    CREATE_MIGRATIONS_TABLE_SQL,
    GET_MIGRATIONS_QUERY,
)
from src.db.entities.base import BaseEntity
from src.db.entities.sql_migration import SQLMigrations

T = TypeVar("T", bound=BaseEntity)


class DBOps:
    def __init__(self, db_url: str):
        self.db_url = db_url
        self._logger = get_logger(__name__)

    def get_connection(self):
        return psycopg.connect(self.db_url, row_factory=dict_row)

    def _execute_sql(
        self,
        exec_type: Literal["all", "one", "many", "run"],
        *args,
        cursor=None,
    ):
        res = None
        if not cursor:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                if exec_type == "all":
                    res = cursor.execute(*args).fetchall()
                elif exec_type == "one":
                    res = cursor.execute(*args).fetchone()
                elif exec_type == "many":
                    cursor.executemany(*args)
                else:
                    cursor.execute(*args)
                cursor.close()
        else:
            if exec_type == "all":
                res = cursor.execute(*args).fetchall()
            elif exec_type == "one":
                res = cursor.execute(*args).fetchone()
            else:
                cursor.execute(*args)
        return res

    def insert_entity(self, entity: T, cursor=None) -> T:
        entity_dict = entity.model_dump()
        params = {
            column: (
                json.dumps(entity_dict[column])
                if type(entity_dict[column]) is dict
                else entity_dict[column]
            )
            for column in entity.get_table_columns()
        }
        columns = list(params.keys())
        insert_columns = [f'"{column}"' for column in columns]

        sql = (
            f'INSERT INTO {entity.get_table_name()}({", ".join(insert_columns)}) '
            f'VALUES ({", ".join([f"%({column})s" for column in columns])}) RETURNING *'
        )
        result = self._execute_sql("one", sql, params, cursor=cursor)
        return entity.__class__.model_validate(result)

    def insert_entities(self, entities: List[T], cursor=None):
        table_name = entities[0].get_table_name()
        data_list = [entity.model_dump() for entity in entities]
        columns = entities[0].get_table_columns()
        params = [(data[column] for column in columns) for data in data_list]
        insert_columns = [f'"{column}"' for column in columns]

        sql = (
            f'INSERT INTO {table_name}({", ".join(insert_columns)}) '
            f'VALUES ({", ".join(["%s"] * len(columns))}) ON CONFLICT (id) DO NOTHING'
        )
        self._execute_sql("many", sql, params, cursor=cursor)

    def update_entity(self, entity: T, cursor=None) -> T:
        entity_dict = entity.model_dump(mode="json")
        params = {
            column: (
                json.dumps(entity_dict[column])
                if type(entity_dict[column]) is dict
                else entity_dict[column]
            )
            for column in entity.get_table_columns()
        }
        set_sql = [f"{key} = %({key})s" for key in entity_dict if key != "id"]
        sql = f"UPDATE {entity.get_table_name()} SET {', '.join(set_sql)} WHERE id = %(id)s RETURNING *"
        result = self._execute_sql("one", sql, params, cursor=cursor)
        return entity.__class__.model_validate(result)

    def get_entity_by_id(
        self,
        _id: str,
        entity_cls: Type[T],
        cursor=None,
    ) -> T:
        table = entity_cls.get_table_name()
        sql = f"SELECT * FROM {table} WHERE id = %(id)s LIMIT 1"
        result = self._execute_sql("one", sql, {"id": _id}, cursor=cursor)
        if not result:
            raise NotFoundError(f"entity with id [{_id}] not found in {table}")
        return entity_cls.model_validate(result)

    def run_query(self, *args, has_response=True, cursor=None) -> List:
        return self._execute_sql(
            "all" if has_response else "run", *args, cursor=cursor
        )

    def get_migrations(self, cursor=None) -> List[SQLMigrations]:
        results = self.run_query(GET_MIGRATIONS_QUERY, cursor=cursor)
        return [SQLMigrations.model_validate(r) for r in results]

    def run_migrations(self):
        self._logger.info("Checking migrations")
        migrations_directory = "src/db/migrations"
        migration_files = os.listdir(migrations_directory)
        migration_files = sorted(migration_files)
        with self.get_connection() as conn:
            cursor = conn.cursor()
            self.run_query(
                CREATE_MIGRATIONS_TABLE_SQL, has_response=False, cursor=cursor
            )
            existing_migrations = self.get_migrations(cursor=cursor)
            existing_migrations_set = set([m.id for m in existing_migrations])
            new_migrations = set(migration_files) - set(
                [m.id for m in existing_migrations]
            )
            self._logger.info(f"New migrations: {list(new_migrations)}")
            for filename in migration_files:
                if filename in existing_migrations_set:
                    continue
                file_path = os.path.join(migrations_directory, filename)
                with open(file_path, "r") as f:
                    sql_statements = f.read()
                    self.run_query(
                        sql_statements, has_response=False, cursor=cursor
                    )
                    insert_data = SQLMigrations(
                        id=filename, sql=sql_statements
                    )
                    self.insert_entity(insert_data, cursor=cursor)
                self._logger.info(f"Executed migration: {filename}")
