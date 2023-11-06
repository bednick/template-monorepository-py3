import pydantic

import async_workers_cron


class TaskReaderSettings(async_workers_cron.TaskReaderSettings):
    cron_mask: str = pydantic.Field(
        "* * * * * H/10", validation_alias="EXAMPLE_WORKERS_CRON_MASK", description="once a 10 sec"
    )


class Settings(async_workers_cron.HandlerSettings):
    example_message: str = pydantic.Field("Hello World", validation_alias="EXAMPLE_MESSAGE")
    example_sleep: float = pydantic.Field(5, validation_alias="EXAMPLE_SLEEP")

    task_reader: TaskReaderSettings = pydantic.Field(default_factory=TaskReaderSettings)
