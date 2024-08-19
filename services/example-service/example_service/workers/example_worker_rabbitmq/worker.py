import logging
from typing import Any, Type

import async_workers.rabbitmq

from example_service.workers.example_worker_rabbitmq import config

logger = logging.getLogger(__name__)


class Worker(async_workers.rabbitmq.TaskHandler[config.Settings]):
    WORKER_NAME = "example-worker-rabbitmq"

    def __init__(self, settings: config.Settings, task_reader: async_workers.rabbitmq.TaskReader, **kwargs):
        super().__init__(settings, task_reader, **kwargs)

    @classmethod
    def load_settings(cls) -> config.Settings:
        return config.Settings()

    @classmethod
    async def initialization(cls: Type["Worker"], settings: config.Settings, **kwargs) -> "Worker":
        task_reader = async_workers.rabbitmq.TaskReader(settings.task_reader)
        return cls(settings, task_reader, **kwargs)

    @classmethod
    def get_worker_name(cls) -> str:
        return cls.WORKER_NAME

    async def _process_task(self, task: async_workers.rabbitmq.Task) -> Any:
        logger.info(f"Start example rabbitmq worker, {task=}")
