import logging
from typing import Any, Type

import async_database_postgresql
import async_workers_cron

from example_workers.workers.example_workers_cron import config

logger = logging.getLogger(__name__)


class Worker(async_workers_cron.TaskHandler[config.Settings]):
    WORKER_NAME = "example-workers-cron"

    def __init__(self, settings: config.Settings, task_reader: async_workers_cron.TaskReader, **kwargs):
        super().__init__(settings, task_reader, **kwargs)
        self.database: async_database_postgresql.storage.Storage = kwargs["database"]

    @classmethod
    def load_settings(cls) -> config.Settings:
        return config.Settings()

    @classmethod
    async def initialization(cls: Type["Worker"], settings: config.Settings, **kwargs) -> "Worker":
        task_reader = async_workers_cron.TaskReader(settings.task_reader)
        return cls(settings, task_reader, **kwargs)

    @classmethod
    def get_worker_name(cls) -> str:
        return cls.WORKER_NAME

    async def _process_task(self, task: async_workers_cron.Task) -> Any:
        logger.info(f"Start example cron worker, {task=} {self.settings.example_message=}")
        results_raw = await self.database.execute("SELECT * FROM information_schema.tables")
        results = results_raw.mappings().all()
        logger.info(f"{len(results)} tables found")
