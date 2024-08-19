import abc
import dataclasses
import logging
import uuid
from typing import Any, AsyncIterator, Generic, Optional, TypeVar

import pydantic

import async_rabbitmq

from async_workers import base

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class Task(base.BaseTask):
    response: async_rabbitmq.client.Response


class TaskReaderSettings(base.TaskReaderSettings):
    request_timeout: int = pydantic.Field(10, validation_alias="RABBITMQ_REQUEST_TIMEOUT")
    rabbitmq: async_rabbitmq.config.Settings = pydantic.Field(default_factory=async_rabbitmq.config.Settings)


TaskReaderSettingsObj = TypeVar("TaskReaderSettingsObj", bound="TaskReaderSettings")


class TaskReader(base.TaskReader[TaskReaderSettings, Task], Generic[TaskReaderSettingsObj], metaclass=abc.ABCMeta):
    def __init__(self, settings: TaskReaderSettingsObj, **kwargs):
        super().__init__(settings, **kwargs)
        self._rabbitmq = async_rabbitmq.client.Client.from_settings(settings.rabbitmq)

    async def __aenter__(self) -> "TaskReader":
        await self._rabbitmq.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._rabbitmq.__aexit__(exc_type, exc_val, exc_tb)

    async def receive(self) -> AsyncIterator[Task]:
        async for response in self._rabbitmq.receive():
            task_id = response.message.properties.message_id or str(uuid.uuid4())
            yield Task(task_id=task_id, traceparent=response.headers.get("traceparent"), response=response)
            if self.settings.run_once:
                break

    async def fetch(self) -> Optional[Task]:
        response = await self._rabbitmq.fetch(timeout=self.settings.request_timeout)
        if not response:
            return None
        task_id = response.message.properties.message_id or str(uuid.uuid4())
        return Task(task_id=task_id, traceparent=response.headers.get("traceparent"), response=response)

    async def complete(self, task: Task, result: Optional[Any] = None):
        message = task.response.message
        if message.reply_to:
            await self._rabbitmq.send(
                result or "", routing_key=message.reply_to, correlation_id=message.correlation_id
            )
        await task.response.message.ack()

    async def error(self, task: Task, error_message: str, error_details: Optional[str] = None):
        await task.response.message.nack(requeue=False)


class HandlerSettings(base.BaseHandlerSettings):
    pass


HandlerSettingsObj = TypeVar("HandlerSettingsObj", bound="HandlerSettings")


class TaskHandler(
    base.TaskHandler[HandlerSettingsObj, TaskReader, Task], Generic[HandlerSettingsObj], metaclass=abc.ABCMeta
):
    pass
