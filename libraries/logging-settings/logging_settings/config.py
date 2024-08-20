import logging
from typing import Literal, Optional

import pydantic

import pydantic_base_settings

logger = logging.getLogger(__name__)

Formatter = Literal["default", "json"]
FORMAT_SHORT = "%(asctime)s %(levelname)-7s %(name)s.%(funcName)s:%(lineno)d %(message)s"
FORMAT_LONG = "%(process)d %(threadName)s %(taskName)s %(levelname) %(name)s %(funcName)s %(lineno)d %(message)s"


class FileSettings(pydantic_base_settings.BaseSettings):
    is_use: bool = pydantic.Field(True, validation_alias="LOGGING_FILE")
    formatter: Formatter = pydantic.Field("json", validation_alias="LOGGING_FILE_FORMATTER")
    filename: str = pydantic.Field(..., validation_alias="LOGGING_FILE_PATH", min_length=1)
    format: str = pydantic.Field(FORMAT_LONG, validation_alias="LOGGING_FILE_FORMAT")
    level: int = pydantic.Field(logging.INFO, validation_alias="LOGGING_FILE_LEVEL")

    def __bool__(self) -> bool:
        return self.is_use


class Settings(pydantic_base_settings.BaseSettings):
    """All logging settings"""

    level: int = pydantic.Field(logging.INFO, validation_alias="LOGGING_LEVEL")
    formatter: Formatter = pydantic.Field("json", validation_alias="LOGGING_FORMATTER")
    stream: Literal["stderr", "stdout"] = pydantic.Field("stderr", validation_alias="LOGGING_STREAM")
    format: str = pydantic.Field(FORMAT_LONG, validation_alias="LOGGING_FORMAT")

    file: Optional[FileSettings] = pydantic.Field(default_factory=FileSettings.read)


def get_settings(settings: Settings | None = None, **kwargs) -> Settings:
    if settings:
        assert isinstance(settings, Settings)
        return settings
    return Settings(**kwargs)
