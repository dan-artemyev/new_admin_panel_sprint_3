"""
Загрузка данных в Elastic Search.
"""

from typing import Generator
from elasticsearch import Elasticsearch, helpers

from .data_formatter import FilmWorkModel
from utils.configuration import ES_DATA_BLOCK_SIZE, ES_INDEX_NAME
from utils.logger import logger


class ElasticSearchSaver:
    """Загрузчик фильмов в индекс ElasticSearch."""

    data_block_size: int = ES_DATA_BLOCK_SIZE
    index_name: str = ES_INDEX_NAME

    def __init__(self, elastic_connection: Elasticsearch):
        """
        Инициализация переменных
        :param elastic_connection: соединение с ElasticSearch
        """
        self.connection = elastic_connection
        self.__documents = []

    def add(self, document: dict) -> None:
        """
        Добавить новый документ.
        :param document: данные документа
        :return:
        """
        self.__documents.append(document)
        if len(self.__documents) >= self.data_block_size:
            self.save()

    def save(self) -> None:
        """
        Сохранить документы из буфера в ElasticSearch.
        :return:
        """
        def __prepare_docs() -> Generator[dict, None, None]:
            """
            Подготовка документов к индексированию в ElasticSearch.
            :return:
            """
            for document in self.__documents:
                action = {
                    '_index': self.index_name,
                    '_op_type': 'index',
                    '_id': str(document.id),
                    '_source': document.json(),
                }
                yield action
        helpers.bulk(self.connection, __prepare_docs())
        logger.info(f'Inserted {len(self.__documents)} rows...')
        self.__documents = []

    def load_from_psql(self, data: Generator[dict, None, None]) -> None:
        """
        Загрузка данных из PostgreSQL.
        :param data: данные из PostgreSQL
        :return:
        """
        formatter = FilmWorkModel
        for row in data:
            for film in row:
                formatted_row = formatter.init_from_sql(**film)
                self.add(formatted_row)
        self.save()
