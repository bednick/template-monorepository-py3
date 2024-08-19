import asyncio
import logging

from async_workers import base, cron, rabbitmq

__all__ = ("base", "cron", "rabbitmq")

logger = logging.getLogger(__name__)


class WorkersLifespan:
    def __init__(self, workers_module, **dependencies):
        self.workers_module = workers_module
        self.dependencies = dependencies
        self.started_workers: list[asyncio.Task] = []

    async def __aenter__(self):
        workers_cls = (getattr(self.workers_module, worker_name).Worker for worker_name in self.workers_module.__all__)
        for worker_cls in workers_cls:
            worker_name = worker_cls.get_worker_name()
            logger.info(f"Run worker {worker_name}")
            task = asyncio.create_task(
                worker_cls.run_with_restarts(**self.dependencies), name=f"WORKER::{worker_name}"
            )
            self.started_workers.append(task)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        for task in self.started_workers:
            task.cancel()
