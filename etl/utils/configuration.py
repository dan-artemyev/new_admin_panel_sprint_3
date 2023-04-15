"""
Конфигурационные данные.
"""

from pydantic import BaseSettings, Field


class PostgresDSL(BaseSettings):
    """Конфигурация PostgreSQL."""

    host: str = Field(..., env='DB_HOST')
    port: int = Field(..., env='DB_PORT')
    user: str = Field(..., env='DB_USER')
    dbname: str = Field(..., env='DB_NAME')
    password: str = Field(..., env='DB_PASSWORD')


class ElasticDSL(BaseSettings):
    """Конфигурация ElasticSearch."""

    host: str = Field(..., env='ES_HOST')
    port: int = Field(..., env='ES_PORT')
    scheme: str = Field(..., env='ES_SCHEME')


class ExtraConfig(BaseSettings):
    """Дополнительные настройки для переноса данных из PostgreSQL в ElasticSearch."""

    ES_TIMEOUT: int = Field(15, env='ES_TIMEOUT')
    ES_INDEX_NAME: str = Field(..., env='ES_INDEX_NAME')
    ES_INDEX_FILE: str = Field(..., env='ES_INDEX_FILE')
    PSQL_DATA_BLOCK_SIZE: int = Field(100, env='DATA_BLOCK_SIZE')
    ES_DATA_BLOCK_SIZE: int = Field(100., env='ES_DATA_BLOCK_SIZE')
    JSON_STATE_STORAGE_FILE: str = Field(..., env='JSON_STATE_STORAGE_FILE')
