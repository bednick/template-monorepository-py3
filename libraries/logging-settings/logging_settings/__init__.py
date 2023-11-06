import logging
from typing import Optional

from logging_settings import config

__all__ = ("config", "basic_config")


def basic_config(settings: Optional[config.Settings] = None):
    settings = config.get_settings(settings)
    logging.basicConfig(level=settings.level)
