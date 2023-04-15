"""
Сохранение данных в PostgreSQL.
"""

from dataclasses import asdict
from typing import Generator, Tuple
from psycopg2 import sql, Error as PostgresError
from psycopg2.extensions import connection as _connection

from logger import logger
from classes import TABLE_NAMES_TO_DATACLASSES


class PostgresSaver:
    """Класс для сохранения данных в PostgreSQL."""

    tables = TABLE_NAMES_TO_DATACLASSES
    scheme = 'content'

    def __init__(self, connection: _connection):
        self.connection = connection

    def save_all_data(self, data: Generator[Tuple[str, list], None, None]) -> None:
        """Основная функция."""
        for rows_info in data:
            table_name, table_rows = rows_info
            rows = [self.tables[table_name](**row) for row in table_rows]
            field_names = asdict(rows[0]).keys()

            insert_query = sql.SQL('''
                insert into {table} ({fields}) values ({values}) on conflict do nothing;
            ''').format(
                table=sql.Identifier(self.scheme, table_name),
                fields=sql.SQL(', ').join(map(sql.Identifier, field_names)),
                values=sql.SQL(', ').join(sql.Placeholder() * len(field_names))
            )
            with self.connection.cursor() as curs:
                try:
                    curs.executemany(insert_query, [tuple(asdict(row).values()) for row in rows])
                    self.connection.commit()
                except PostgresError as error:
                    logger.error(error)
                else:
                    block_size = len(rows)
                    logger.info(f'Successfully inserted {block_size} rows in table: {table_name}')
