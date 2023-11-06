import asyncio
import logging

import fastapi
import fastapi.exception_handlers
import starlette.exceptions
import starlette_exporter
import urllib3.exceptions

import logging_settings
import trace_settings

from example_workers import config, dependencies, routers, workers

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
settings = config.get_settings(load_dotenv=True)
logging_settings.basic_config(settings.logging)
trace_settings.basic_config(settings.trace)
logger = logging.getLogger(__name__)

app = routers.app

app.add_middleware(
    starlette_exporter.PrometheusMiddleware,
    app_name="example-workers",
    prefix="example_workers",
    buckets=[0.1, 0.25, 0.5, 1.0, 10.0],
)
app.add_route("/metrics", starlette_exporter.handle_metrics)


@app.on_event("startup")
async def startup_event():
    logger.debug("Starting up...")
    await dependencies.initialize(settings)
    await run_all_workers()


@app.on_event("shutdown")
async def shutdown_event():
    logger.debug("Shutting down...")
    await stop_all_workers()
    await dependencies.close()


@app.middleware("http")
async def generic_exception_handler(request: fastapi.Request, call_next) -> fastapi.responses.JSONResponse:
    """https://github.com/tiangolo/fastapi/issues/4025"""
    try:
        return await call_next(request)
    except Exception as exc:
        method, path, status_code = (
            request.scope["method"],
            request.scope["path"],
            fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
        logger.exception(f"HTTP error {method=} {path=} {status_code=}: {repr(exc)}")
        return fastapi.responses.JSONResponse(status_code=status_code, content={"detail": "Internal Server Error"})


@app.exception_handler(starlette.exceptions.HTTPException)
async def http_exception_handler(
    request: fastapi.Request, exc: starlette.exceptions.HTTPException
) -> fastapi.responses.Response:
    method, path, status_code = request.scope["method"], request.scope["path"], exc.status_code
    logger.warning(f"HTTP error {method=} {path=} {status_code=}: {repr(exc)}")
    return await fastapi.exception_handlers.http_exception_handler(request, exc)


@app.exception_handler(fastapi.exceptions.RequestValidationError)
async def validation_exception_handler(
    request: fastapi.Request, exc: fastapi.exceptions.RequestValidationError
) -> fastapi.responses.JSONResponse:
    errors = exc.errors()
    logger.warning(f"Incorrect service request {errors=}")
    return await fastapi.exception_handlers.request_validation_exception_handler(request, exc)


async def run_all_workers():
    worker_kwargs = dependencies.DEPENDENCIES
    if not hasattr(run_all_workers, "TASKS"):
        run_all_workers.TASKS = []

    workers_cls = (getattr(workers, worker_name).Worker for worker_name in workers.__all__)

    for worker_cls in workers_cls:
        worker_name = worker_cls.get_worker_name()
        if worker_name in settings.skip_workers:
            logger.warning(f"SKIP worker {worker_name}")
            continue
        logger.info(f"Run worker {worker_name}")
        task = asyncio.create_task(worker_cls.run_with_restarts(**worker_kwargs), name=f"WORKER::{worker_name}")
        run_all_workers.TASKS.append(task)


async def stop_all_workers():
    if hasattr(run_all_workers, "TASKS"):
        for task in run_all_workers.TASKS:  # type: asyncio.Task
            task.cancel()
