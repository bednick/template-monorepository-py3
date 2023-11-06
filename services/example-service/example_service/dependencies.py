import logging
from typing import Any, Dict

from example_service import config

logger = logging.getLogger(__name__)

DEPENDENCIES: Dict[str, Any] = {}


async def initialize(settings_: config.Settings):
    pass


async def close():
    for name, dependence in DEPENDENCIES.items():
        if hasattr(dependence, "__aexit__"):
            try:
                await dependence.__aexit__(None, None, None)
            except Exception as exc:
                logger.warning(f"Error execute {name}.__aexit__: {exc}")
        elif hasattr(dependence, "__exit__"):
            try:
                await dependence.__exit__(None, None, None)
            except Exception as exc:
                logger.warning(f"Error execute {name}.__exit__: {exc}")
