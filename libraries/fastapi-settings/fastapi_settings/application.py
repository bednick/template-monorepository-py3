import logging

import fastapi
import fastapi.exception_handlers
import fastapi.routing
import starlette.exceptions
import starlette.middleware.cors
import starlette_exporter
from starlette.types import Lifespan

from fastapi_settings import config

logger = logging.getLogger(__name__)


def get_application(
    settings: config.Settings,
    router: fastapi.routing.APIRouter,
    lifespan: Lifespan,
) -> fastapi.FastAPI:
    application = fastapi.FastAPI(
        title=settings.project_name,
        debug=settings.debug,
        version=settings.version,
        lifespan=lifespan,
    )
    application.include_router(router)
    application.add_middleware(
        starlette_exporter.PrometheusMiddleware,  # noqa
        app_name=settings.project_name,
        prefix=settings.project_name.replace("-", "_"),
        buckets=[0.1, 0.25, 0.5, 1.0, 10.0],
    )
    application.add_route("/metrics", starlette_exporter.handle_metrics)

    application.add_middleware(
        starlette.middleware.cors.CORSMiddleware,  # noqa
        allow_origins=settings.allowed_hosts,
        allow_credentials=True,
        allow_methods=("*",),
        allow_headers=("*",),
    )

    @application.middleware("http")
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
            logger.exception(f"HTTP error {method=} {path=} {status_code=}: {repr(exc)}", exc_info=exc)
            return fastapi.responses.JSONResponse(status_code=status_code, content={"detail": "Internal Server Error"})

    @application.exception_handler(starlette.exceptions.HTTPException)
    async def http_exception_handler(
        request: fastapi.Request, exc: starlette.exceptions.HTTPException
    ) -> fastapi.responses.Response:
        method, path, status_code = request.scope["method"], request.scope["path"], exc.status_code
        logger.warning(f"HTTP error {method=} {path=} {status_code=}: {repr(exc)}")
        return await fastapi.exception_handlers.http_exception_handler(request, exc)

    @application.exception_handler(fastapi.exceptions.RequestValidationError)
    async def validation_exception_handler(
        request: fastapi.Request, exc: fastapi.exceptions.RequestValidationError
    ) -> fastapi.responses.JSONResponse:
        errors = exc.errors()
        logger.warning(f"Incorrect service request {errors=}")
        return await fastapi.exception_handlers.request_validation_exception_handler(request, exc)

    return application
