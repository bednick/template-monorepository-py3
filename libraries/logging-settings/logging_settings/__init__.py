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
    stream_handler.setFormatter(logging.Formatter(settings.format))
    return stream_handler


def get_file_handler(settings: config.FileSettings) -> logging.FileHandler:
    file_handler = logging.FileHandler(settings.filename, encoding="utf-8")
    file_handler.setLevel(settings.level)
    file_handler.setFormatter(
        pythonjsonlogger.jsonlogger.JsonFormatter(
            settings.format,
            json_serializer=functools.partial(json.dumps, separators=(",", ":")),
            json_ensure_ascii=False,
            timestamp=True,
        )
    )
    return file_handler
