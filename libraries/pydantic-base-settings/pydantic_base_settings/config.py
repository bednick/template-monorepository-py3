import logging
from typing import Self

import pydantic
import pydantic_settings

logger = logging.getLogger(__name__)


class BaseSettings(pydantic_settings.BaseSettings):
    model_config = pydantic_settings.SettingsConfigDict(
        env_file=(".env",),
        case_sensitive=True,
        extra="ignore",
    )

    @classmethod
    def read(cls) -> Self | None:
        try:
            return cls()
        except pydantic.ValidationError as exc:
            logger.debug(f"Not load {cls.__name__}", exc_info=exc)
            return None
