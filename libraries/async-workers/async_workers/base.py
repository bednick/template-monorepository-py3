import abc
import asyncio
import concurrent.futures
import dataclasses
import logging
import time
import traceback
from typing import Any, AsyncIterator, Callable, Generic, Optional, Type, TypeVar

import pydantic
from opentelemetry import propagate, trace
from prometheus_client import Counter, Gauge, Histogram

import async_utils
import pydantic_base_settings

tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)


class TaskReaderSettings(pydantic_base_settings.BaseSettings):
    run_once: bool = pydantic.Field(False, validation_alias="TASK_READER_RUN_ONCE")
    sleep_seconds: float = pydantic.Field(0.1, validation_alias="TASK_READER_SLEEP_SECONDS")


@dataclasses.dataclass
class BaseTask:
    task_id: str
    traceparent: Optional[str]


TaskReaderSettingsObj = TypeVar("TaskReaderSettingsObj", bound="TaskReaderSettings")
TaskReaderObj = TypeVar("TaskReaderObj", bound="TaskReader")
TaskObj = TypeVar("TaskObj", bound="BaseTask")


class TaskReader(Generic[TaskReaderSettingsObj, TaskObj], metaclass=abc.ABCMeta):
    """Interface for receiving tasks"""

    def __init__(self, settings: TaskReaderSettingsObj, **kwargs):
        self.settings = settings

    @abc.abstractmethod
    async def __aenter__(self) -> "TaskReader":
        pass

    @abc.abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    @abc.abstractmethod
    async def fetch(self) -> Optional[TaskObj]:
        """Get one task"""
        pass

    @abc.abstractmethod
    async def complete(self, task: TaskObj, result: Optional[Any] = None):
        """Complete the task"""
        pass

    @abc.abstractmethod
    async def error(self, task: TaskObj, error_message: str, error_details: Optional[str] = None):
        """End task with error"""
        pass

    async def receive(self) -> AsyncIterator[TaskObj]:
        while True:
            logger.debug("Start fetch task ...")
            result = await self.fetch()
            logger.debug(f"Fetch task: {result}")
            if result:
                yield result
            else:
                await asyncio.sleep(self.settings.sleep_seconds)
            if self.settings.run_once:
                break


class BaseHandlerSettings(pydantic_base_settings.BaseSettings):
    task_max_time_seconds: float = pydantic.Field(15 * 60, validation_alias="WORKER_TASK_MAX_TIME_SECONDS")
    max_restarts: Optional[int] = pydantic.Field(None, validation_alias="WORKER_MAX_RESTARTS")
    restart_time_seconds: float = pydantic.Field(30, validation_alias="WORKER_RESTART_TIME_SECONDS")

    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))


BaseHandlerSettingsObj = TypeVar("BaseHandlerSettingsObj", bound="BaseHandlerSettings")
TaskHandlerObj = TypeVar("TaskHandlerObj", bound="TaskHandler")

TASK_HANDLERS_RESTART_COUNTER = Counter("task_handlers_restart", "Number of restarts", ["worker_name"])
TASK_HANDLERS_TASK_COUNTER = Counter("task_handlers_task", "Number of tasks", ["worker_name", "status"])
TASK_HANDLERS_TASK_GAUGE = Gauge("task_handlers_task_duration_total_seconds", "", ["worker_name"])
TASK_HANDLERS_TASK_HISTOGRAM = Histogram(
    "task_handlers_task_duration_seconds",
    "",
    ["worker_name"],
    buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 7.5, 10.0, 30.0, 60.0, 300.0, float("inf")),
)


class TaskHandler(Generic[BaseHandlerSettingsObj, TaskReaderObj, TaskObj], metaclass=abc.ABCMeta):
    def __init__(self, settings: BaseHandlerSettingsObj, task_reader: TaskReaderObj, **kwargs):
        self.settings = settings
        self.task_reader = task_reader
        self.worker_name = self.get_worker_name()

    async def __aenter__(self) -> "TaskHandler[BaseHandlerSettingsObj, TaskReaderObj, TaskObj]":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    @classmethod
    @abc.abstractmethod
    def load_settings(cls) -> BaseHandlerSettingsObj:
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    async def initialization(cls: Type[TaskHandlerObj], settings: BaseHandlerSettingsObj, **kwargs) -> TaskHandlerObj:
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def get_worker_name(cls) -> str:
        raise NotImplementedError

    @classmethod
    async def run_with_restarts(cls: Type[TaskHandlerObj], **kwargs):
        worker_name = cls.get_worker_name()
        with async_utils.LogExtraManager(worker_name=worker_name):
            restart_count = 0
            try:
                settings = cls.load_settings()
            except Exception as exc:
                logger.critical(f"Error load TaskHandler settings: {exc}")
                raise
            logger.debug(f"Settings loaded: {settings=}")
            while True:
                try:
                    task_handler = await cls.initialization(settings, **kwargs)
                    async with task_handler:
                        await task_handler.run()
                except Exception as exc:
                    logger.exception(
                        f"Error execute worker {worker_name}, restart after {settings.restart_time_seconds} seconds",
                        exc_info=exc,
                    )
                    TASK_HANDLERS_RESTART_COUNTER.labels(worker_name).inc()
                    restart_count += 1
                    if settings.max_restarts and restart_count >= settings.max_restarts:
                        raise
                    await asyncio.sleep(settings.restart_time_seconds)

    @classmethod
    async def run_in_executor(
        cls,
        function: Callable[..., async_utils.ReturnType],
        *args,
        executor: Optional[concurrent.futures.Executor] = None,
        **kwargs,
    ) -> async_utils.ReturnType:
        return await async_utils.run_in_executor_with_log_extra(executor, function, *args, **kwargs)

    async def run(self):
        """Start reading and processing cycle"""
        async with self.task_reader:
            async for task in self.task_reader.receive():
                await self.process_task(task)

    async def process_task(self, task: TaskObj) -> Any:
        timeout = self.settings.task_max_time_seconds
        with tracer.start_as_current_span(
            self.worker_name, context=propagate.extract({"traceparent": task.traceparent})
        ):
            logger.info(f"Start process_task worker_name={self.worker_name} {task.task_id=}")
            start = time.time()
            try:
                TASK_HANDLERS_TASK_COUNTER.labels(self.worker_name, "process").inc()
                if timeout:
                    result = await asyncio.wait_for(self._process_task(task), timeout=timeout)
                else:
                    result = await self._process_task(task)
                TASK_HANDLERS_TASK_COUNTER.labels(self.worker_name, "complete").inc()
                await self.task_reader.complete(task, result=result)
            except asyncio.TimeoutError as exc:
                error_message = f"Error process_task '{self.worker_name}': Task timeout exceeded ({timeout} sec)"
                logger.error(error_message)
                TASK_HANDLERS_TASK_COUNTER.labels(self.worker_name, "error").inc()
                await self.task_reader.error(
                    task, error_message, "".join(traceback.format_tb(exc.__traceback__)) + str(exc)
                )
            except Exception as exc:
                error_message = f"Error process_task '{self.worker_name}': {str(exc)}"
                logger.error(error_message, exc_info=exc)
                TASK_HANDLERS_TASK_COUNTER.labels(self.worker_name, "error").inc()
                await self.task_reader.error(
                    task, error_message, "".join(traceback.format_tb(exc.__traceback__)) + str(exc)
                )
            finally:
                work_time = time.time() - start
                TASK_HANDLERS_TASK_GAUGE.labels(self.worker_name).inc(work_time)
                TASK_HANDLERS_TASK_HISTOGRAM.labels(self.worker_name).observe(work_time)
                logger.info(f"Processed task {self.worker_name=} {task.task_id=} work_time={round(work_time, 3)}")

    @abc.abstractmethod
    async def _process_task(self, task: TaskObj): ...
