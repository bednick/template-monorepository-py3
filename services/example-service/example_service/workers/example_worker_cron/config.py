import pydantic

import async_workers.cron


class TaskReaderSettings(async_workers.cron.TaskReaderSettings):
    cron_mask: str = pydantic.Field(
        "* * * * * H/10", validation_alias="EXAMPLE_WORKER_CRON_MASK", description="once a 10 sec"
    )


class Settings(async_workers.cron.HandlerSettings):
    example_sleep: float = pydantic.Field(5, validation_alias="EXAMPLE_SLEEP")

    task_reader: TaskReaderSettings = pydantic.Field(default_factory=TaskReaderSettings)
