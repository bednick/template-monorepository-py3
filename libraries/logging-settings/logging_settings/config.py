import logging
from typing import Optional

import dotenv
import pydantic
import pydantic_settings


class Settings(pydantic_settings.BaseSettings):
    """All logging settings"""

    level: int = pydantic.Field(logging.INFO, alias="LOGGING_LEVEL")

    @pydantic.field_validator("level")
    @classmethod
    def check_correct_level(cls, value: int) -> int:
        if value not in (logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL):
            print(f"Incorrect value log level {value}")
            raise ValueError(f"Incorrect value log level {value}")
        return value


def get_settings(settings: Optional[Settings] = None, *, load_dotenv: bool = False, **kwargs) -> Settings:
    if settings:
        assert isinstance(settings, Settings)
        return settings
    if load_dotenv:
        dotenv.load_dotenv(dotenv.find_dotenv(usecwd=True))
    return Settings(**kwargs)
