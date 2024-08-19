from typing import Optional

import dotenv
import pydantic

import fastapi_settings

from example_service import database as database_


class Settings(fastapi_settings.config.Settings):
    """All service settings"""

    project_name: str = pydantic.Field("example-service", validation_alias="PROJECT_NAME")

    database: database_.config.Settings = pydantic.Field(default_factory=database_.config.Settings)


def get_settings(settings: Optional[Settings] = None, *, load_dotenv: bool = False, **kwargs) -> Settings:
    if settings:
        assert isinstance(settings, Settings)
        return settings
    if load_dotenv:
        dotenv.load_dotenv(dotenv.find_dotenv(usecwd=True))
    return Settings(**kwargs)
