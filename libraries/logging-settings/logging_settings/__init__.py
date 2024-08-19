import functools
import json
import logging
import sys
from typing import Optional

import pythonjsonlogger.jsonlogger

from logging_settings import config

__all__ = ("config", "basic_config")


def basic_config(settings: Optional[config.Settings] = None):
    settings = config.get_settings(settings)
    handlers = [get_stream_handler(settings)]
    if settings.file:
        handlers.append(get_file_handler(settings.file))
    logging.basicConfig(level=settings.level, format=settings.format, handlers=handlers)


def get_stream_handler(settings: config.Settings) -> logging.StreamHandler:
    stream_handler = logging.StreamHandler(sys.stderr if settings.stream == "stderr" else sys.stdout)
    stream_handler.setLevel(settings.level)
    stream_handler.setFormatter(create_formatter(settings.formatter, settings.format))
    return stream_handler


def get_file_handler(settings: config.FileSettings) -> logging.FileHandler:
    file_handler = logging.FileHandler(settings.filename, encoding="utf-8")
    file_handler.setLevel(settings.level)
    file_handler.setFormatter(create_formatter(settings.formatter, settings.format))
    return file_handler


def create_formatter(formatter: config.Formatter, format_: str) -> logging.Formatter:
    if formatter == "default":
        return logging.Formatter(format_)
    if formatter == "json":
        return pythonjsonlogger.jsonlogger.JsonFormatter(
            format_,
            json_serializer=functools.partial(json.dumps, separators=(",", ":")),
            json_ensure_ascii=False,
            timestamp=True,
        )
    raise ValueError(f"Unsupported formatter: {formatter}")
