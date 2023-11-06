from typing import Optional

import dotenv
import pydantic
import pydantic_settings

import logging_settings


class Settings(pydantic_settings.BaseSettings):
    """All service settings"""

    logging: logging_settings.config.Settings = pydantic.Field(default_factory=logging_settings.config.Settings)


def get_settings(settings: Optional[Settings] = None, *, load_dotenv: bool = False, **kwargs) -> Settings:
    if settings:
        assert isinstance(settings, Settings)
        return settings
    if load_dotenv:
        dotenv.load_dotenv(dotenv.find_dotenv(usecwd=True))
    return Settings(**kwargs)
