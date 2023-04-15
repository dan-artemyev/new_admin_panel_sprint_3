"""
Хранилища состояний.
"""

import abc
import json
from typing import Any, Dict


class BaseStorage(abc.ABC):
    """
    Абстрактное хранилище состояния.
    Позволяет сохранять и получать состояние.
    Способ хранения состояния может варьироваться в зависимости
    от итоговой реализации. Например, можно хранить информацию
    в базе данных или в распределённом файловом хранилище.
    """

    @abc.abstractmethod
    def save_state(self, state: Dict[str, Any]) -> None:
        """
        Сохранить состояние в хранилище.
        :param state: состояние
        :return:
        """

    @abc.abstractmethod
    def retrieve_state(self) -> Dict[str, Any]:
        """
        Получить состояние из хранилища.
        :return: состояние
        """


class JsonFileStorage(BaseStorage):
    """Реализация хранилища, использующего JSON файл."""

    def __init__(self, file_path: str):
        """
        Инициализзация переменных
        :param file_path: путь к файлу
        """
        self.file_path = file_path

    def save_state(self, state: Dict[str, Any]) -> None:
        """
        Сохранить состояние в хранилище.
        :param state: состояние
        :return:
        """
        if not self.file_path:
            return
        with open(self.file_path, 'w+') as state_file:
            json.dump(state, state_file)

    def retrieve_state(self) -> Dict[str, Any]:
        """
        Получить состояние из хранилища.
        :return: состояние
        """
        if not self.file_path:
            return {}
        try:
            with open(self.file_path, 'r') as state_file:
                state = json.load(state_file)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
        return state


class State:
    """Класс для работы с состояниями."""

    def __init__(self, storage: BaseStorage):
        """
        Инициализзация переменных
        :param storage: тип хранилища
        """
        self.storage = storage
        self.state = storage.retrieve_state()

    def set_state(self, key: str, value: Any) -> None:
        """
        Установить состояние для переданного ключа.
        :param key: ключ
        :param value: значение
        :return:
        """
        self.state[key] = value
        self.storage.save_state(self.state)

    def get_state(self, key: str) -> Any:
        """
        Получить состояние для переданного ключа.
        :param key: ключ
        :return: значение
        """
        return self.state.get(key)
