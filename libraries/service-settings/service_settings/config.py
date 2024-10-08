from typing import Optional, Tuple

import pydantic

import logging_settings
import pydantic_base_settings
import trace_settings


class Settings(pydantic_base_settings.BaseSettings):
    """All service settings"""

    project_name: str = pydantic.Field(..., validation_alias="PROJECT_NAME")
    version: str = pydantic.Field(default="latest", validation_alias="VERSION")
    debug: bool = pydantic.Field(default=False, validation_alias="DEBUG")
    allowed_hosts: Tuple[str, ...] = pydantic.Field(default_factory=lambda: ("*",), validation_alias="ALLOWED_HOSTS")

    skip_workers: Tuple[str, ...] = pydantic.Field((), validation_alias="SKIP_WORKERS")

    logging: logging_settings.config.Settings = pydantic.Field(default_factory=logging_settings.config.Settings)
    trace: trace_settings.config.Settings = pydantic.Field(default_factory=trace_settings.config.Settings)


def get_settings(settings: Optional[Settings] = None, **kwargs) -> Settings:
    if settings:
        assert isinstance(settings, Settings)
        return settings
    return Settings(**kwargs)
