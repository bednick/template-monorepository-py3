import logging
from typing import Any, Type

import async_workers.cron

from example_service import database
from example_service.workers.example_worker_cron import config

logger = logging.getLogger(__name__)


class Worker(async_workers.cron.TaskHandler[config.Settings]):
    WORKER_NAME = "example-worker-cron"

    def __init__(self, settings: config.Settings, task_reader: async_workers.cron.TaskReader, **kwargs):
        super().__init__(settings, task_reader, **kwargs)
        self.storage: database.storage.Storage = kwargs["storage"]

    @classmethod
    def load_settings(cls) -> config.Settings:
        return config.Settings()

    @classmethod
    async def initialization(cls: Type["Worker"], settings: config.Settings, **kwargs) -> "Worker":
        task_reader = async_workers.cron.TaskReader(settings.task_reader)
        return cls(settings, task_reader, **kwargs)

    @classmethod
    def get_worker_name(cls) -> str:
        return cls.WORKER_NAME

    async def _process_task(self, task: async_workers.cron.Task) -> Any:
        current_database = await self.storage.get_current_database()
        logger.info(f"Start example cron worker, {task=}, {current_database=}")
