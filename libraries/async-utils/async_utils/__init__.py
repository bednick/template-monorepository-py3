import asyncio
import concurrent.futures
import contextvars
import copy
import functools
import logging
import random
from typing import (
    Any,
    AsyncGenerator,
    Awaitable,
    Callable,
    Coroutine,
    Dict,
    Generator,
    List,
    Optional,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
)

logger = logging.getLogger(__name__)

# TODO: add description of input parameters
ReturnType = TypeVar("ReturnType")
AsyncFunc = Callable[..., Awaitable[ReturnType]]


def async_retry(
    retry_sleeps: Tuple[Union[float, Tuple[float, float]], ...] = ((0.3, 0.5), (0.5, 1)),
    exceptions: Tuple[Type[Exception], ...] = (),
) -> Callable[[AsyncFunc], AsyncFunc]:
    """Retry async function use decorator"""

    def retry_wrapper(func: AsyncFunc) -> AsyncFunc:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> ReturnType:
            for retry_index in range(len(retry_sleeps) + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as exc:
                    if retry_index < len(retry_sleeps):
                        retry_sleep = retry_sleeps[retry_index]
                        if isinstance(retry_sleep, float):
                            delay = retry_sleep
                        else:
                            delay = round(random.uniform(retry_sleep[0], retry_sleep[1]), 3)
                        logger.warning(f"Error request {func.__name__}: {type(exc)}, {retry_index=} {delay=}")
                        await asyncio.sleep(delay)
                        continue
                    raise
            raise RuntimeError("Void retry_sleeps args")

        return wrapper

    return retry_wrapper


async def run_with_semaphore(future: Coroutine[Any, Any, ReturnType], semaphore: asyncio.Semaphore) -> ReturnType:
    async with semaphore:
        return await future


async def gather(*futures: Coroutine[Any, Any, ReturnType], chunk_size: int) -> List[ReturnType]:
    semaphore = asyncio.Semaphore(chunk_size)
    return await asyncio.gather(*[run_with_semaphore(future, semaphore) for future in futures])  # noqa


_LOG_EXTRA_DATA: contextvars.ContextVar = contextvars.ContextVar("_LOG_EXTRA_DATA", default={})


def _set_log_extra(log_extra: Dict[str, Any]) -> None:
    _LOG_EXTRA_DATA.set(log_extra)


def get_log_extra(should_copy: bool = False) -> Dict[str, Any]:
    extra = _LOG_EXTRA_DATA.get()
    if should_copy:
        return copy.deepcopy(extra)
    return extra


def _update_log_extra(update: Dict[str, Any]) -> None:
    if update:
        current_extra = get_log_extra(should_copy=True)
        _set_log_extra({**current_extra, **update})


def _delete_log_extra(keys: Set[str]) -> None:
    if not keys:
        return
    extra: Dict[str, Any] = _LOG_EXTRA_DATA.get()
    if not extra:
        return
    for key in keys:
        extra.pop(key, None)


class LogExtraManager:
    def __init__(self, **kwargs: Any):
        self._extra: Dict[str, Any] = kwargs
        self._current_extra: Dict[str, Any] = {}

    def __enter__(self) -> "LogExtraManager":
        if self._extra:
            # сохраняем значения, которые были до перезаписи
            current_extra = get_log_extra()
            self._current_extra = {key: value for key, value in current_extra.items() if key in self._extra}
            # перезаписываем
            _update_log_extra(self._extra)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        _delete_log_extra(set(self._extra))
        _update_log_extra(self._current_extra)


def run_with_log_extra(function: Callable[..., ReturnType], *args, log_extra: Dict[str, Any], **kwargs) -> ReturnType:
    with LogExtraManager(**log_extra):
        return function(*args, **kwargs)


async def run_in_executor_with_log_extra(
    executor: Optional[concurrent.futures.Executor], function: Callable[..., ReturnType], *args, **kwargs
) -> ReturnType:
    loop = asyncio.get_running_loop()
    log_extra = get_log_extra(should_copy=True)
    if "log_extra" in kwargs:
        log_extra.update(kwargs.pop("log_extra"))
    return await loop.run_in_executor(
        executor, functools.partial(run_with_log_extra, function, *args, log_extra=log_extra, **kwargs)
    )


async def run_in_executor(
    executor: Optional[concurrent.futures.Executor], function: Callable[..., ReturnType], *args, **kwargs
) -> ReturnType:
    return await run_in_executor_with_log_extra(executor, function, *args, **kwargs)


__END = object()
__EXECUTOR = concurrent.futures.ThreadPoolExecutor(thread_name_prefix="async_generator")

GenObj = TypeVar("GenObj")


def __next(generator: Generator[GenObj, None, None]) -> GenObj:
    try:
        return next(generator)
    except StopIteration:
        return __END  # type: ignore


async def async_generator(
    generator: Generator[GenObj, None, None], executor: Optional[concurrent.futures.Executor] = __EXECUTOR
) -> AsyncGenerator[GenObj, None]:
    while True:
        result = await run_in_executor_with_log_extra(executor, __next, generator)
        if result == __END:
            return
        yield result
