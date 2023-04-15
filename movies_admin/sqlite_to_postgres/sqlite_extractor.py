"""
Извлечение данных из SQLite.
"""

import os
import sqlite3
from dotenv import load_dotenv

from classes import TABLE_NAMES_TO_DATACLASSES
from logger import logger

load_dotenv()


class SQLiteExtractor:
    """Класс для извлечения данных из SQLite."""

    tables = TABLE_NAMES_TO_DATACLASSES
    data_block_size = os.environ.get('DATA_BLOCK_SIZE', '100')

    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    def extract_movies(self):
        """Основная функция."""
        for table_name in self.tables:
            logger.info(f'Extracting from table: {table_name}')

            try:
                table_content = self.connection.execute('''select * from %s;''' % table_name)
            except sqlite3.OperationalError as error:
                logger.error(error)
                continue

            while data := table_content.fetchmany(size=int(self.data_block_size)):
                yield table_name, data

            logger.info(f'Successfully extracted all data from table: {table_name}')
