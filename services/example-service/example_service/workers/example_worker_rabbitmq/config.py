import pydantic

import async_workers.rabbitmq


class TaskReaderSettings(async_workers.rabbitmq.TaskReaderSettings):
    pass


class Settings(async_workers.rabbitmq.HandlerSettings):
    task_reader: TaskReaderSettings = pydantic.Field(default_factory=TaskReaderSettings)
