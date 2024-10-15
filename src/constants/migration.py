CREATE_MIGRATIONS_TABLE_SQL = """
create table if not exists sql_migrations(
    id text not null primary key,
    sql text not null,
    created_at timestamptz not null
);
"""

GET_MIGRATIONS_QUERY = "select * from sql_migrations;"
