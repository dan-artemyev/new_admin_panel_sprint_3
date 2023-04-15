"""
Реализация отказоустойчивости сервиса.
"""

from time import sleep
from functools import wraps
from typing import Callable, Union

from .logger import logger


def backoff(
        exceptions: tuple,
        start_sleep_time: Union[int, float] = 0.1,
        factor: Union[int, float] = 2,
        border_sleep_time: Union[int, float] = 10
) -> Callable:
    """
    Функция для повторного выполнения функции, если возникла ошибка.
    :param exceptions: Исключения, которые обрабатываем
    :param start_sleep_time: Начальное время ожидания
    :param factor: Во сколько раз нужно увеличить время ожидания
    :param border_sleep_time: Максимальное время ожидания
    :return: Результат выполнения функции
    """

    def func_wrapper(func: Callable) -> Callable:
        @wraps(func)
        def inner(*args, **kwargs):
            sleep_time = start_sleep_time
            while True:
                try:
                    return func(*args, **kwargs)
                except exceptions as error:
                    logger.error(error)
                    sleep_time = sleep_time * factor
                    if sleep_time > border_sleep_time:
                        sleep_time = border_sleep_time
                    sleep(sleep_time)
        return inner
    return func_wrapper
