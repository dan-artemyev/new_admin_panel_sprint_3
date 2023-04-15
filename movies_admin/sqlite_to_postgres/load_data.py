"""
Загрузка данных из SQLite в Postgres.
"""

import os
from dotenv import load_dotenv
from contextlib import contextmanager, closing

import sqlite3
import psycopg2
from psycopg2.extras import DictCursor
from psycopg2.extensions import connection as _connection

from logger import logger
from postgres_saver import PostgresSaver
from sqlite_extractor import SQLiteExtractor


@contextmanager
def get_sqlite_connection(db_path: str):
    """Контекстный менеджер для SQLite."""
    conn = sqlite3.connect(f"file:{db_path}?mode=rw", uri=True)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


def load_from_sqlite(connection: sqlite3.Connection, pg_conn: _connection) -> None:
    """Основной метод загрузки данных из SQLite в Postgres."""
    postgres_saver = PostgresSaver(pg_conn)
    sqlite_extractor = SQLiteExtractor(connection)

    data = sqlite_extractor.extract_movies()
    postgres_saver.save_all_data(data)


if __name__ == '__main__':
    load_dotenv()
    dsl = {
        'host': os.getenv('DB_HOST'),
        'port': os.getenv('DB_PORT'),
        'dbname': os.getenv('DB_NAME'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
    }
    db_path = os.getenv('SQLITE_DB')

    logger.info('Connecting to databases')
    try:
        with get_sqlite_connection(db_path) as sqlite_conn, \
                closing(psycopg2.connect(**dsl, cursor_factory=DictCursor)) as pg_conn:
            load_from_sqlite(sqlite_conn, pg_conn)
    except (psycopg2.OperationalError, sqlite3.OperationalError) as error:
        logger.error(error)
    logger.info('Closing connections to databases')
