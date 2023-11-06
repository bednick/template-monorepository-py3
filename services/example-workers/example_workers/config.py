from typing import Optional, Tuple

import dotenv
import pydantic
import pydantic_settings

import async_database_postgresql
import logging_settings
import trace_settings


class Settings(pydantic_settings.BaseSettings):
    """All service settings"""

    model_config = pydantic.ConfigDict(populate_by_name=True)

    skip_workers: Tuple[str, ...] = pydantic.Field((), validation_alias="SKIP_WORKERS")

    database: async_database_postgresql.config.Settings = pydantic.Field(
        default_factory=async_database_postgresql.config.Settings
    )
    logging: logging_settings.config.Settings = pydantic.Field(default_factory=logging_settings.config.Settings)
    trace: trace_settings.config.Settings = pydantic.Field(default_factory=trace_settings.config.Settings)


def get_settings(settings: Optional[Settings] = None, *, load_dotenv: bool = False, **kwargs) -> Settings:
    if settings:
        assert isinstance(settings, Settings)
        return settings
    if load_dotenv:
        dotenv.load_dotenv(dotenv.find_dotenv(usecwd=True))
    return Settings(**kwargs)
