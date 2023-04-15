"""
Логгер для логирования событий.
"""

import logging

logging.basicConfig(
    encoding='utf-8',
    format='%(levelname)s: %(asctime)s %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
    level=logging.DEBUG,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs.txt', mode='a'),
    ]
)
logger = logging.getLogger()
