import logging

from example_service import config

loger = logging.getLogger(__name__)


async def initialize(settings: config.Settings):
    pass


async def close():
    pass
