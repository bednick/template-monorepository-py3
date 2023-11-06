import logging
from typing import Any, Dict, Optional

import async_database_postgresql

from example_workers import config

logger = logging.getLogger(__name__)

DEPENDENCIES: Dict[str, Any] = {}


async def initialize(settings_: config.Settings):
    database_ = await async_database_postgresql.storage.Storage.from_settings(settings_.database)

    DEPENDENCIES["database"] = database_

    last_name = None
    initialized: Dict[str, Any] = {}
    try:
        for name, dependence in DEPENDENCIES.items():
            last_name = name
            if hasattr(dependence, "__aenter__"):
                await dependence.__aenter__()
            elif hasattr(dependence, "__enter__"):
                await dependence.__enter__()
    except Exception as exc:
        logger.exception(f"Error execute {last_name}.__aenter__: {exc}")
        await close(initialized)
        raise


async def close(dependencies: Optional[Dict[str, Any]] = None):
    for name, dependence in (dependencies or DEPENDENCIES).items():
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
