import abc
import asyncio
import dataclasses
import datetime
import logging
import uuid
from typing import Any, Generic, Optional, TypeVar

import croniter
import pydantic

from async_workers import base

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class Task(base.BaseTask):
    start_time: datetime.datetime


class TaskReaderSettings(base.TaskReaderSettings):
    cron_mask: str = pydantic.Field(..., description="Time start in cron format", examples=["* * * * * H/10"])


TaskReaderSettingsObj = TypeVar("TaskReaderSettingsObj", bound="TaskReaderSettings")


class TaskReader(base.TaskReader[TaskReaderSettings, Task], Generic[TaskReaderSettingsObj], metaclass=abc.ABCMeta):
    def __init__(self, settings: TaskReaderSettingsObj, **kwargs):
        super().__init__(settings, **kwargs)
        self._scheduler = croniter.croniter(
            settings.cron_mask,
            start_time=datetime.datetime.now(datetime.timezone.utc),
            ret_type=datetime.datetime,
            hash_id=str(uuid.uuid4()),
        )

    async def __aenter__(self) -> "TaskReader":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def fetch(self) -> Task:
        now = datetime.datetime.now(datetime.timezone.utc)
        next_time: datetime.datetime = self._scheduler.get_next(start_time=now)
        sleep_time = (next_time - now).total_seconds()
        await asyncio.sleep(sleep_time)
        return Task(task_id=str(uuid.uuid4()), traceparent=None, start_time=self._scheduler.get_current())

    async def complete(self, task: Task, result: Optional[Any] = None):
        pass

    async def error(self, task: Task, error_message: str, error_details: Optional[str] = None):
        pass


class HandlerSettings(base.BaseHandlerSettings):
    pass


HandlerSettingsObj = TypeVar("HandlerSettingsObj", bound="HandlerSettings")


class TaskHandler(
    base.TaskHandler[HandlerSettingsObj, TaskReader, Task], Generic[HandlerSettingsObj], metaclass=abc.ABCMeta
):
    pass
