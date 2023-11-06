import pydantic

import async_workers_rabbitmq


class TaskReaderSettings(async_workers_rabbitmq.TaskReaderSettings):
    pass


class Settings(async_workers_rabbitmq.HandlerSettings):
    task_reader: TaskReaderSettings = pydantic.Field(default_factory=TaskReaderSettings)
