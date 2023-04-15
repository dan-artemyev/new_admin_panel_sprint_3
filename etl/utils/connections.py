"""
Рвбота с соединениями
"""
import json
from typing import Tuple
from http import HTTPStatus
from contextlib import contextmanager

import psycopg2
from psycopg2.extras import DictCursor
from elastic_transport import ConnectionTimeout
from psycopg2.extensions import connection as postgres_connection
from elasticsearch import Elasticsearch, ConnectionError

from utils import configuration
from utils.logger import logger
from utils.backoff import backoff
from state_storage.state import State, JsonFileStorage


@backoff((psycopg2.OperationalError,))
def get_postgres_conn() -> postgres_connection:
    """
    Установка соединения с PostgreSql.
    :return: соединение с PostgreSql
    """
    dsl = {
        'host': configuration.DB_HOST,
        'port': configuration.DB_PORT,
        'user': configuration.DB_USER,
        'dbname': configuration.DB_NAME,
        'password': configuration.DB_PASSWORD,
    }
    logger.info('Connecting to Postgres...')
    connection = psycopg2.connect(**dsl, cursor_factory=DictCursor)
    connection.set_session(autocommit=True)
    return connection


@backoff((ConnectionError, ConnectionTimeout))
def get_elastic_conn() -> Elasticsearch:
    """
    Установка соединения с ElasticSearch.
    :return: соединение с ElasticSearch
    """
    hosts = [{
        'scheme': configuration.ES_SCHEME,
        'host': configuration.ES_HOST,
        'port': configuration.ES_PORT,
    }]
    http_auth = (configuration.ES_USER, configuration.ES_PASSWORD)
    logger.info('Connecting to ElasticSearch...')
    connection = Elasticsearch(retry_on_timeout=True, hosts=hosts, http_auth=http_auth)
    set_elastic_index(connection)
    return connection


def set_elastic_index(connection: Elasticsearch) -> Elasticsearch:
    """
    Загрузка индекса в ElasticSearch.
    :param connection: соединение с ElasticSearch
    :return:
    """
    with open(configuration.ES_INDEX_FILE, 'r') as index_file:
        mapping = json.load(index_file)
    if not connection.indices.exists(index=configuration.ES_INDEX_NAME):
        connection.indices.create(index=configuration.ES_INDEX_NAME, ignore=HTTPStatus.BAD_REQUEST, body=mapping)
        logger.info('Creating Elastic index...')
    else:
        logger.info('Elastic index already exists...')
    return connection


def get_state_storage() -> State:
    """
    Загрузка хранилища состояний.
    :return: хранилище состояний
    """
    logger.info('Connecting to state storage...')
    state = State(JsonFileStorage(configuration.JSON_STATE_STORAGE_FILE))
    return state


@contextmanager
def prepare_connections() -> Tuple[postgres_connection, Elasticsearch, State]:
    """
    Инициализация подключений к хранилищам.
    :return: соединение с PostgreSql, соединение с ElasticSearch, хранилище состояний
    """
    logger.info(f'Connecting to dbs and storage...')
    postgres_conn = get_postgres_conn()
    elastic_conn = get_elastic_conn()
    state = get_state_storage()
    logger.info('Successfully connected to dbs and storage...')
    yield postgres_conn, elastic_conn, state

    postgres_conn.close()
    logger.info('Closed PostgreSQL connection...')
    elastic_conn.close()
    logger.info('Closed ElasticSearch connection...')
