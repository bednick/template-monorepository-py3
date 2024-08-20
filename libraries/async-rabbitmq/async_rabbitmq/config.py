import logging
import ssl
from typing import Any, Dict, Optional

import pydantic
import yarl

import pydantic_base_settings

logger = logging.getLogger(__name__)


class SslSettings(pydantic_base_settings.BaseSettings):
    is_use: bool = pydantic.Field(True, validation_alias="RABBITMQ_SSL")
    cacerts: Optional[str] = pydantic.Field(None, validation_alias="RABBITMQ_SSL_CAFILE", min_length=1)
    certfile: str = pydantic.Field(..., validation_alias="RABBITMQ_SSL_CERTFILE", min_length=1)
    keyfile: str = pydantic.Field(..., validation_alias="RABBITMQ_SSL_KEYFILE", min_length=1)
    password: Optional[str] = pydantic.Field(None, validation_alias="RABBITMQ_SSL_PASSWORD")

    def __bool__(self) -> bool:
        return self.is_use

    @property
    def ssl_context(self) -> ssl.SSLContext:
        # context = ssl.SSLContext(ssl.PROTOCOL_TLS)
        context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        context.options |= ssl.OP_NO_SSLv2
        context.options |= ssl.OP_NO_SSLv3
        context.verify_mode = ssl.CERT_OPTIONAL
        if self.cacerts:
            context.load_verify_locations(self.cacerts)
            context.verify_mode = ssl.CERT_REQUIRED
            context.check_hostname = True
        else:
            context.load_default_certs()
        if self.certfile and self.keyfile:
            context.load_cert_chain(certfile=self.certfile, keyfile=self.keyfile)
        return context


class Settings(pydantic_base_settings.BaseSettings):
    host: str = pydantic.Field("localhost", validation_alias="RABBITMQ_HOST")
    port: int = pydantic.Field(5672, validation_alias="RABBITMQ_PORT")
    login: Optional[str] = pydantic.Field("guest", validation_alias="RABBITMQ_LOGIN")
    password: Optional[str] = pydantic.Field("guest", validation_alias="RABBITMQ_PASSWORD")
    queue: Optional[str] = pydantic.Field(None, validation_alias="RABBITMQ_QUEUE")
    service_name: str = pydantic.Field("async_rabbitmq")

    ssl_settings: Optional[SslSettings] = pydantic.Field(default_factory=SslSettings.read)

    def generate_url(self) -> yarl.URL:
        scheme = "amqps" if bool(self.ssl_settings) else "amqp"
        kwargs: Dict[str, Any] = {"scheme": scheme, "host": self.host, "port": self.port, "path": "//", "query": {}}
        if self.login and self.password:
            kwargs["query"]["auth"] = "plain"
            kwargs["user"] = self.login
            kwargs["password"] = self.password
        else:
            kwargs["query"]["auth"] = "external"
        url = yarl.URL.build(**kwargs)
        if url.password:
            logger.info(f"Rabbit url: {url.with_password('******')}")
        else:
            logger.info(f"Rabbit url: {url}")
        return url
