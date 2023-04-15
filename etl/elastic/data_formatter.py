"""
Модель для форматирования данных из PostgreSQL в ElasticSearch.
"""

from uuid import UUID
from typing import List
from pydantic import BaseModel


class Person(BaseModel):
    """Класс для представления персоны."""

    id: UUID
    name: str


class FilmWorkModel(BaseModel):
    """Класс для предствления кинопроизведения."""

    id: UUID
    title: str
    description: str
    genre: list[str]
    imdb_rating: float
    director: list[str]
    actors: list[Person]
    writers: list[Person]
    actors_names: list[str]
    writers_names: list[str]

    @classmethod
    def init_from_sql(cls, **film_info):
        """
        Инициализация из данных PostgreSQL.
        :param film_info: данные о кинопроизведении
        :return:
        """
        def __group_by_role(role, **data) -> List[Person]:
            """
            Поиск всех персоналий, игравших переданную роль в кинопроизведении.
            :param role: роль человека, по которой производится поиск
            :param data: данные о кинопроизведении
            :return: список персоналий
            """
            return [
                Person(id=person.get('id'), name=person.get('name'))
                for person in data.get('persons') or [] if person.get('role') == role
            ]

        actors = __group_by_role('actor', **film_info)
        writers = __group_by_role('writer', **film_info)
        directors = __group_by_role('director', **film_info)
        return cls(
            id=film_info.get('id'),
            title=film_info.get('title'),
            genre=film_info.get('genre'),
            description=film_info.get('description'),
            imdb_rating=film_info['rating'] if film_info.get('rating') else 0,
            actors=actors,
            writers=writers,
            director=[i.name for i in directors],
            actors_names=[i.name for i in actors],
            writers_names=[i.name for i in writers],
        )
