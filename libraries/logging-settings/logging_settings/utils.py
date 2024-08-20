import functools
import json
import logging
import sys
from typing import Optional

import pythonjsonlogger.jsonlogger
from opentelemetry import trace

import async_utils

from logging_settings import config


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
    stream_handler.addFilter(ContextFilter())
    return stream_handler


def get_file_handler(settings: config.FileSettings) -> logging.FileHandler:
    file_handler = logging.FileHandler(settings.filename, encoding="utf-8")
    file_handler.setLevel(settings.level)
    file_handler.setFormatter(create_formatter(settings.formatter, settings.format))
    file_handler.addFilter(ContextFilter())
    return file_handler


def create_formatter(formatter: config.Formatter, format_: str) -> logging.Formatter:
    if formatter == "default":
        return logging.Formatter(format_)
    if formatter == "json":
        return CustomJsonFormatter(format_)
    raise ValueError(f"Unsupported formatter: {formatter}")


class CustomJsonFormatter(pythonjsonlogger.jsonlogger.JsonFormatter):
    def __init__(self, *args, **kwargs):
        kwargs["json_serializer"] = kwargs.pop("json_serializer", functools.partial(json.dumps, separators=(",", ":")))
        kwargs["json_ensure_ascii"] = kwargs.pop("json_ensure_ascii", False)
        super().__init__(*args, **kwargs)

    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)


class ContextFilter(logging.Filter):
    def filter(self, record):
        async_log_extra = async_utils.get_log_extra()
        for name, value in async_log_extra.items():
            if not hasattr(record, name):
                setattr(record, name, value)
        ctx = trace.get_current_span().get_span_context()
        record.trace_id = ctx.trace_id
        record.span_id = ctx.span_id
        return True
