"""
Импорт фильмов из PostgreSQL в ElasticSearch.
"""

from time import sleep
from elasticsearch import Elasticsearch

from elastic.saver import ElasticSearchSaver
from postgres.loader import MovieLoader, GenreLoader, PersonLoader
from psycopg2.extensions import connection as postgres_connection

from utils.logger import logger
from state_storage.state import State
from utils.configuration import ES_TIMEOUT
from utils.connections import prepare_connections


def load_data(pg_conn: postgres_connection, el_conn: Elasticsearch, state: State) -> None:
    """
    Импорт фильмов из PostgreSQL в ElasticSearch.
    :param pg_conn: соединение с PostgreSQL
    :param el_conn: соединение с ElasticSearch
    :param state: хранилище состояний
    :return:
    """
    psql_data_loaders = (
        MovieLoader,
        GenreLoader,
        PersonLoader,
    )

    for data_loader in psql_data_loaders:
        loader = data_loader(pg_conn, state)
        saver = ElasticSearchSaver(el_conn)
        logger.info(f'Importing data from {loader.table_name}...')
        saver.load_from_psql(loader.get_data())
        logger.info(f'Successfully imported data from {loader.table_name}...')


if __name__ == '__main__':
    while True:
        with prepare_connections() as connections:
            load_data(*connections)
        sleep(ES_TIMEOUT)
