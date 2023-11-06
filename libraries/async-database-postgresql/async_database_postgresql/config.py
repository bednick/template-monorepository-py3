import logging
import ssl
from typing import Literal, Optional, Sequence, Tuple

import pydantic
import pydantic_settings
import yarl

logger = logging.getLogger(__name__)

DEFAULT_PORT = 5432


class SettingsSSL(pydantic_settings.BaseSettings):
    model_config = pydantic.ConfigDict(populate_by_name=True)

    is_use: bool = pydantic.Field(True, validation_alias="DATABASE_POSTGRESQL_SSL")
    cafile: Optional[str] = pydantic.Field(None, validation_alias="DATABASE_POSTGRESQL_SSL_CAFILE")
    certfile: str = pydantic.Field(..., validation_alias="DATABASE_POSTGRESQL_SSL_CERTFILE")
    keyfile: Optional[str] = pydantic.Field(None, validation_alias="DATABASE_POSTGRESQL_SSL_KEYFILE")
    password: Optional[str] = pydantic.Field(None, validation_alias="DATABASE_POSTGRESQL_SSL_PASSWORD")
    check_hostname: bool = pydantic.Field(True, validation_alias="DATABASE_POSTGRESQL_SSL_CHECK_HOSTNAME")

    def __bool__(self) -> bool:
        return self.is_use

    @classmethod
    def read(cls) -> Optional["SettingsSSL"]:
        try:
            return cls()
        except pydantic.ValidationError as exc:
            logger.debug(f"Not load {cls.__name__}", exc_info=exc)
        return None

    @property
    def ssl_context(self) -> ssl.SSLContext:
        sslctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=self.cafile)  # noqa
        sslctx.check_hostname = self.check_hostname
        sslctx.load_cert_chain(self.certfile, keyfile=self.keyfile, password=self.password)
        return sslctx


class Settings(pydantic_settings.BaseSettings):
    model_config = pydantic.ConfigDict(populate_by_name=True)

    hosts: Tuple[str, ...] = pydantic.Field(validation_alias="DATABASE_POSTGRESQL_HOSTS")
    ports_: Optional[Tuple[int, ...]] = pydantic.Field(None, validation_alias="DATABASE_POSTGRESQL_PORTS")
    username: str = pydantic.Field(..., validation_alias="DATABASE_POSTGRESQL_USERNAME")
    password: str = pydantic.Field(..., validation_alias="DATABASE_POSTGRESQL_PASSWORD")
    database_name: str = pydantic.Field(..., validation_alias="DATABASE_POSTGRESQL_DATABASE_NAME")
    dialect: Literal["asyncpg"] = pydantic.Field("asyncpg", validation_alias="DATABASE_POSTGRESQL_DIALECT")
    isolation_level: str = pydantic.Field("READ COMMITTED", validation_alias="DATABASE_POSTGRESQL_ISOLATION_LEVEL")
    max_overflow: int = pydantic.Field(-1, validation_alias="DATABASE_POSTGRESQL_MAX_OVERFLOW")
    pool_size: int = pydantic.Field(5, validation_alias="DATABASE_POSTGRESQL_POOL_SIZE")
    pool_timeout: float = pydantic.Field(30, validation_alias="DATABASE_POSTGRESQL_POOL_TIMEOUT")
    pool_pre_ping: bool = pydantic.Field(True, validation_alias="DATABASE_POSTGRESQL_POOL_PRE_PING")
    echo: bool = pydantic.Field(False, validation_alias="DATABASE_POSTGRESQL_ECHO")
    statement_timeout: int = pydantic.Field(5000, validation_alias="DATABASE_POSTGRESQL_STATEMENT_TIMEOUT_MS")

    ssl: Optional[SettingsSSL] = pydantic.Field(default_factory=SettingsSSL.read)

    @pydantic.field_validator("ports_")
    @classmethod
    def check_len_ports(cls, v, values):
        if v and values.get("hosts") and len(v) != len(values["hosts"]):
            raise ValueError(f"Incorrect len ports: {len(v)}. Correct len: {len(values['hosts'])}")
        return v

    @property
    def ports(self) -> Sequence[int]:
        return self.ports_ if self.ports_ else (DEFAULT_PORT,) * len(self.hosts)

    @property
    def url(self) -> yarl.URL:
        return yarl.URL.build(
            scheme=f"postgresql+{self.dialect}",
            user=self.username,
            password=self.password,
            path=self.database_name,
            query=dict(
                host=",".join(self.hosts),
                port=",".join(map(str, self.ports)),
            ),
        )

    @property
    def sync_url(self) -> yarl.URL:
        return yarl.URL.build(
            scheme="postgresql",
            user=self.username,
            password=self.password,
            path=self.database_name,
            query=dict(
                host=",".join(self.hosts),
                port=",".join(map(str, self.ports)),
            ),
        )
