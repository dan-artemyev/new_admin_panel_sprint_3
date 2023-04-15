"""
Конфигурационные данные.
"""

import os
from dotenv import load_dotenv


load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PORT = int(os.getenv('DB_PORT'))
DB_PASSWORD = os.getenv('DB_PASSWORD')

ES_USER = os.getenv('ES_USER')
ES_HOST = os.getenv('ES_HOST')
ES_SCHEME = os.getenv('ES_SCHEME')
ES_PORT = int(os.getenv('ES_PORT'))
ES_PASSWORD = os.getenv('ES_PASSWORD')
ES_TIMEOUT = int(os.getenv('ES_TIMEOUT'))
ES_INDEX_NAME = os.getenv('ES_INDEX_NAME')
ES_INDEX_FILE = os.getenv('ES_INDEX_FILE')

PSQL_DATA_BLOCK_SIZE = int(os.getenv('DATA_BLOCK_SIZE'))
ES_DATA_BLOCK_SIZE = int(os.getenv('ES_DATA_BLOCK_SIZE'))
JSON_STATE_STORAGE_FILE = os.getenv('JSON_STATE_STORAGE_FILE')
