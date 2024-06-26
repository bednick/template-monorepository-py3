from typing import Literal, Optional

import dotenv
import pydantic
import pydantic_settings


class Settings(pydantic_settings.BaseSettings):
    """All trace settings"""

    model_config = pydantic.ConfigDict(populate_by_name=True)

    exporter: Optional[Literal["ConsoleSpanExporter"]] = pydantic.Field(None, validation_alias="TRACE_EXPORTER")
    processor: Literal["SimpleSpanProcessor", "BatchSpanProcessor"] = pydantic.Field(
        "BatchSpanProcessor", validation_alias="TRACE_PROCESSOR"
    )


def get_settings(settings: Optional[Settings] = None, *, load_dotenv: bool = False, **kwargs) -> Settings:
    if settings:
        assert isinstance(settings, Settings)
        return settings
    if load_dotenv:
        dotenv.load_dotenv(dotenv.find_dotenv(usecwd=True))
    return Settings(**kwargs)
