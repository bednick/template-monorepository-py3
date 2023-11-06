import functools
import json
import logging
from typing import Any, Dict, Optional

import pydantic.json
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from async_database_postgresql import config

logger = logging.getLogger(__name__)


def with_session(func):
    """Create and reuse session. Designed exclusively for Storage methods!"""

    @functools.wraps(func)
    async def wrapper(self: "Storage", *args, **kwargs):
        session: Optional[AsyncSession] = kwargs.pop("session", None)
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
    async def from_settings(cls, settings: config.Settings) -> "Storage":
        logger.info(
            f"Create engine database={settings.database_name} ssl={bool(settings.ssl and settings.ssl.ssl_context)}"
        )
        return cls(
            engine=create_async_engine(
                str(settings.url),
                isolation_level=settings.isolation_level,
                json_serializer=functools.partial(json.dumps, default=pydantic.json.pydantic_encoder),
                json_deserializer=json.loads,
                pool_pre_ping=settings.pool_pre_ping,
                pool_timeout=settings.pool_timeout,
                pool_size=settings.pool_size,
                max_overflow=settings.max_overflow,
                echo=settings.echo,
                connect_args={
                    "server_settings": {"statement_timeout": str(settings.statement_timeout)},
                    "ssl": settings.ssl and settings.ssl.ssl_context,
                },
            )
        )

    async def close(self):
        if self.engine:
            await self.engine.dispose()
            self.session_maker = None
            self.engine = None

    @with_session
    async def execute(
        self, statement, parameters: Optional[Dict[str, Any]] = None, *, session: AsyncSession = ...
    ) -> Any:
        if isinstance(statement, str):
            statement = text(statement)
        return await session.execute(statement, parameters)
