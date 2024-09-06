import functools
import json
import logging
from typing import Any, Dict, Optional, Sequence, Union

import pydantic.json
from sqlalchemy import Executable, Result, ScalarResult, text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from async_database_postgresql import config

logger = logging.getLogger(__name__)


def with_session(func):
    """Create and reuse session. Designed exclusively for Storage methods!
    Type hints are not used because: https://youtrack.jetbrains.com/issue/PY-57765
    """

    @functools.wraps(func)
    async def wrapper(self: "Storage", *args, **kwargs):
        session: AsyncSession | None = kwargs.pop("session", None)
        if session is not None:
            return await func(self, *args, session=session, **kwargs)
        async with self.session_maker() as new_session:  # type: AsyncSession
            return await func(self, *args, session=new_session, **kwargs)

    return wrapper


class Storage:
    def __init__(self, engine: AsyncEngine, autoflush: bool = False, expire_on_commit: bool = False):
        self.engine = engine
        self.session_maker = sessionmaker(  # noqa
            engine, class_=AsyncSession, autoflush=autoflush, expire_on_commit=expire_on_commit
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    @classmethod
    def from_settings(cls, settings: config.Settings) -> "Storage":
        logger.info(
            f"Create engine database={settings.database_name} ssl={bool(settings.ssl and settings.ssl.ssl_context)}"
        )
        if settings.pool_size < 0:
            pool_settings = {"poolclass": NullPool}
        else:
            pool_settings = {
                "pool_timeout": settings.pool_timeout,
                "pool_size": settings.pool_size,
                "max_overflow": settings.max_overflow,
            }
        return cls(
            engine=create_async_engine(
                str(settings.dsn),
                isolation_level=settings.isolation_level,
                json_serializer=functools.partial(json.dumps, default=pydantic.json.pydantic_encoder),
                json_deserializer=json.loads,
                pool_pre_ping=settings.pool_pre_ping,
                echo=settings.echo,
                connect_args={
                    "server_settings": {"statement_timeout": str(settings.statement_timeout)},
                    "ssl": settings.ssl and settings.ssl.ssl_context,
                },
                **pool_settings,
            )
        )

    async def close(self):
        if self.engine:
            await self.engine.dispose()
            self.session_maker = None
            self.engine = None

    @with_session
    async def execute(
        self,
        stmt: Union[Executable, str],
        parameters: Optional[Dict[str, Any]] = None,
        *,
        session: AsyncSession = ...,
    ) -> Result[Any]:
        if isinstance(stmt, str):
            stmt = text(stmt)
        return await session.execute(stmt, parameters)

    @with_session
    async def scalars(
        self,
        stmt: Executable,
        parameters: Optional[Dict[str, Any]] = None,
        *,
        session: AsyncSession = ...,
    ) -> ScalarResult[Any]:
        return (await session.execute(stmt, parameters)).scalars()

    @with_session
    async def first(
        self,
        stmt: Executable,
        parameters: Optional[Dict[str, Any]] = None,
        *,
        session: AsyncSession = ...,
    ) -> Any | None:
        return (await session.execute(stmt, parameters)).scalars().first()

    @with_session
    async def all(
        self,
        stmt: Executable,
        parameters: Optional[Dict[str, Any]] = None,
        *,
        session: AsyncSession = ...,
    ) -> Sequence[Any]:
        return (await session.execute(stmt, parameters)).scalars().all()
