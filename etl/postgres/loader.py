"""
Загрузчики из PostgreSQL.
"""

import datetime
from uuid import UUID
from abc import ABC, abstractmethod
from functools import cached_property
from typing import Tuple, Generator, List

from psycopg2.sql import SQL, Identifier
from psycopg2 import Error as PostgresError
from psycopg2.extensions import connection as postgres_connection

from utils.logger import logger
from state_storage.state import State
from utils.configuration import PSQL_DATA_BLOCK_SIZE


MIN_DATE_TIME = datetime.datetime.combine(datetime.datetime.min, datetime.time.min)


class Loader(ABC):
    """Абстрактный класс для загрузчиков."""

    data_block_size = PSQL_DATA_BLOCK_SIZE
    scheme = 'content'
    table_name = None

    def __init__(self, connection: postgres_connection, state: State):
        """
        Инициализация переменных
        :param connection: соединение с БД
        :param state: хранилище состояний
        :return:
        """
        self.state = state
        self.connection = connection

    def _execute_sql(self, query: SQL, values: tuple | list):
        """
        Выполнение запроса в БД.
        :param query: шаблон запроса
        :param values: переменные для запроса
        :return: результат запроса
        """
        with self.connection.cursor() as curs:
            try:
                curs.execute(query, values)
            except PostgresError as error:
                logger.error(error)
            while data := curs.fetchmany(size=int(self.data_block_size)):
                yield data

    def get_data(self):
        """
        Получение информации об измененных фильмах.
        :return: полная информация о фильмах
        """
        for row_data in self.get_updated_movies_ids():
            ids = tuple(ids[0] for ids in row_data)
            query = SQL('''
                SELECT
                    fw.id
                    , fw.title
                    , COALESCE(fw.description, '') as description
                    , fw.rating
                    , fw.type
                    , fw.created_at
                    , fw.updated_at
                    , COALESCE (
                       json_agg(
                           DISTINCT jsonb_build_object(
                               'role', pfw.role,
                               'id', p.id,
                               'name', p.full_name
                           )
                       )
                       , '[]'
                    ) as persons
                    , json_agg(DISTINCT g.name) as genre
                FROM content.film_work fw
                JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
                JOIN content.person p ON p.id = pfw.person_id
                JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
                JOIN content.genre g ON g.id = gfw.genre_id
                WHERE fw.id IN %s
                GROUP BY fw.id
                ORDER BY fw.updated_at;
            ''')
            rows = self._execute_sql(query, (ids,))
            yield from rows

    def get_updated_movies_ids(self):
        """
        Получение списка идентификаторов измененных фильмов и сохранение состояния.
        :return: идентификаторы фильмов, у которых обновились данные
        """
        for data in self._get_updated_instance_ids():
            ids = tuple(row[0] for row in data)
            yield from self._get_updated_movies_ids(ids)
            self.save_state(data[-1][1])

    def save_state(self, date: datetime.date) -> None:
        """
        Сохранить последнее состояние в хранилище.
        :param date: Дата обновления данных
        :return:
        """
        self.state.set_state(type(self).__qualname__, str(date))

    @cached_property
    def modified_date(self) -> datetime.datetime:
        """
        :return: Дата последнего обновления данных в хранилище состояний.
        """
        object_name = type(self).__qualname__
        latest_date = self.state.get_state(object_name)
        try:
            latest_date = datetime.datetime.fromisoformat(latest_date)
        except (ValueError, TypeError):
            latest_date = MIN_DATE_TIME
        logger.info(f'{object_name} latest date: {latest_date}')
        return latest_date

    def _get_updated_instance_ids(self) -> Generator[List[Tuple[UUID, datetime.datetime]], None, None]:
        """
        Получение списка идентификатор измененных объектов таблицы класса.
        :return: идентификаторы обновленных сущностей таблицы, принадлежащей данному классу
        """
        query = SQL('''
            SELECT
                id
                , updated_at
            FROM {table}
            WHERE updated_at >= %s
            ORDER BY updated_at, id;
        ''').format(table=Identifier(self.scheme, self.table_name))
        yield from self._execute_sql(query, (self.modified_date, ))

    @abstractmethod
    def _get_updated_movies_ids(self, instance_ids):
        """
        Получение списка идентификаторов измененных фильмов.
        :param instance_ids: идентификаторы обновленных сущностей таблицы, принадлежащей данному классу
        :return: идентификаторы фильмов, у которых обновились данные
        """


class MovieLoader(Loader):
    """Класс для загрузки при измененнии фильмов."""

    table_name = 'film_work'

    def _get_updated_movies_ids(self, instance_ids):
        """
        Получение списка идентификаторов измененных фильмов.
        :param instance_ids: идентификаторы обновленных сущностей таблицы, принадлежащей данному классу
        :return: идентификаторы фильмов, у которых обновились данные
        """
        yield [[_id] for _id in instance_ids]


class GenreLoader(Loader):
    """Класс для загрузки при измененнии жанров."""

    table_name = 'genre'

    def _get_updated_movies_ids(self, instance_ids):
        """
        Получение списка идентификаторов измененных фильмов.
        :param instance_ids: идентификаторы обновленных сущностей таблицы, принадлежащей данному классу
        :return: идентификаторы фильмов, у которых обновились данные
        """
        query = SQL('''
            SELECT fw.id
            FROM content.film_work fw
            LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
            WHERE gfw.genre_id IN %s
            ORDER BY fw.updated_at;
        ''')
        yield from self._execute_sql(query, (instance_ids,))


class PersonLoader(Loader):
    """Класс для загрузки при измененнии жанров."""

    table_name = 'person'

    def _get_updated_movies_ids(self, instance_ids):
        """
        Получение списка идентификаторов измененных фильмов.
        :param instance_ids: идентификаторы обновленных сущностей таблицы, принадлежащей данному классу
        :return: идентификаторы фильмов, у которых обновились данные
        """
        query = SQL('''
            SELECT fw.id
            FROM content.film_work fw
            LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
            WHERE pfw.person_id IN %s
            ORDER BY fw.updated_at;
        ''')
        yield from self._execute_sql(query, (instance_ids,))
