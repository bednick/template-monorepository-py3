from typing import Optional

import pydantic

import service_settings

from example_service import database as database_


class Settings(service_settings.config.Settings):
    """All service settings"""

    project_name: str = pydantic.Field("example-service", validation_alias="PROJECT_NAME")

    database: database_.config.Settings = pydantic.Field(default_factory=database_.config.Settings)


def get_settings(settings: Optional[Settings] = None, **kwargs) -> Settings:
    if settings:
        assert isinstance(settings, Settings)
        return settings
    return Settings(**kwargs)
