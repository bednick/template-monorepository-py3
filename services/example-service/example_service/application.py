import functools
import logging

import fastapi.exception_handlers
import urllib3.exceptions

import fastapi_settings
import logging_settings
import trace_settings

from example_service import api, config, dependencies

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)


def get_application(settings: config.Settings | None = None) -> fastapi.FastAPI:
    if settings is None:
        settings = config.get_settings(load_dotenv=True)
        logging_settings.basic_config(settings.logging)
        trace_settings.basic_config(settings.trace)
    return fastapi_settings.get_application(
        settings=settings,
        router=api.router,
        lifespan=functools.partial(dependencies.lifespan, settings=settings),
    )
