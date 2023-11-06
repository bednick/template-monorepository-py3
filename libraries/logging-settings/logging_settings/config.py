import logging
from typing import Literal, Optional

import dotenv
import pydantic
import pydantic_settings

logger = logging.getLogger(__name__)


class FileSettings(pydantic_settings.BaseSettings):
    model_config = pydantic.ConfigDict(populate_by_name=True)

    is_use: bool = pydantic.Field(True, validation_alias="LOGGING_FILE")
    filename: str = pydantic.Field(..., validation_alias="LOGGING_FILE_PATH", min_length=1)
    format: str = pydantic.Field(
        "%(process)d %(threadName)s %(taskName)s %(levelname) %(name)s %(funcName)s %(lineno)d %(message)s",
        validation_alias="LOGGING_FILE_FORMAT",
    )
    level: int = pydantic.Field(logging.INFO, validation_alias="LOGGING_FILE_LEVEL")

    def __bool__(self) -> bool:
        return self.is_use

    @classmethod
    def read(cls) -> Optional["FileSettings"]:
        try:
            return cls()
        except pydantic.ValidationError as exc:
            logger.debug(f"Not load {cls.__name__}", exc_info=exc)
            return None


class Settings(pydantic_settings.BaseSettings):
    """All logging settings"""

    model_config = pydantic.ConfigDict(populate_by_name=True)

    level: int = pydantic.Field(logging.INFO, validation_alias="LOGGING_LEVEL")
    stream: Literal["stderr", "stdout"] = pydantic.Field("stderr", validation_alias="LOGGING_STREAM")
    format: str = pydantic.Field(
        "%(asctime)s %(levelname)-7s %(name)s.%(funcName)s:%(lineno)d %(message)s", validation_alias="LOGGING_FORMAT"
    )

    file: Optional[FileSettings] = pydantic.Field(default_factory=FileSettings.read)


def get_settings(settings: Optional[Settings] = None, *, load_dotenv: bool = False, **kwargs) -> Settings:
    if settings:
        assert isinstance(settings, Settings)
        return settings
    if load_dotenv:
        dotenv.load_dotenv(dotenv.find_dotenv(usecwd=True))
    return Settings(**kwargs)
