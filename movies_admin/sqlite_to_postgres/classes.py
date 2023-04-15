"""
Классы для представления используемых таблиц.
"""

import uuid
from datetime import date, datetime
from dataclasses import dataclass, field, fields

STR_DEFAULT = ''


@dataclass(frozen=True)
class TimeStampedMixin:
    """Базовый класс для классов с датой создания и изменения."""
    created_at: datetime = field(default=datetime.now())
    updated_at: datetime = field(default=datetime.now())


@dataclass(frozen=True)
class UUIDMixin:
    """Базовый класс для классов с UUID-идентификаторами."""
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass(frozen=True)
class FilmWork(UUIDMixin, TimeStampedMixin):
    """Кинопроизведения."""
    rating: float = field(default=0.0)
    type: str = field(default=STR_DEFAULT)
    title: str = field(default=STR_DEFAULT)
    file_path: str = field(default=STR_DEFAULT)
    description: str = field(default=STR_DEFAULT)
    creation_date: date = field(default=date.today())


@dataclass(frozen=True)
class Person(UUIDMixin, TimeStampedMixin):
    """Персоналии."""
    full_name: str = field(default=STR_DEFAULT)


@dataclass(frozen=True)
class Genre(UUIDMixin, TimeStampedMixin):
    """Жанры."""
    name: str = field(default=STR_DEFAULT)
    description: str = field(default=STR_DEFAULT)


@dataclass(frozen=True)
class GenreFilmWork(UUIDMixin):
    """Вспомогательная таблица для связи жанров  и кинопроизведений."""
    created_at: datetime = field(default=datetime.now())
    genre_id: uuid.UUID = field(default_factory=uuid.uuid4)
    film_work_id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass(frozen=True)
class PersonFilmWork(UUIDMixin):
    """Вспомогательная таблица для связи персоналий и кинопроизведений."""
    role: str = field(default=STR_DEFAULT)
    created_at: datetime = field(default=datetime.now())
    person_id: uuid.UUID = field(default_factory=uuid.uuid4)
    film_work_id: uuid.UUID = field(default_factory=uuid.uuid4)


TABLE_NAMES_TO_DATACLASSES = {
    'genre': Genre,
    'person': Person,
    'film_work': FilmWork,
    'person_film_work': PersonFilmWork,
    'genre_film_work': GenreFilmWork,
}
