import datetime
import json
import logging
import ssl
from typing import Any, AsyncGenerator, Dict, NamedTuple, Optional

import aio_pika
import jsons
import yarl
from opentelemetry import propagate
from prometheus_client import Counter

from async_rabbitmq import config

logger = logging.getLogger(__name__)

PRIORITY = 0
DELIVERY_MODE = 2
CONTENT_ENCODING = "utf-8"
CONTENT_TYPE = "application/json"

CONSUME_COUNTER = Counter("async_rabbitmq_consume", "Number of fetch message", ["service_name", "status"])
PRODUCE_COUNTER = Counter("async_rabbitmq_produce", "Number of produce message", ["service_name", "status"])


class Response(NamedTuple):
    data: Dict[str, Any]
    headers: Dict[str, Any]
    message: aio_pika.abc.AbstractIncomingMessage


class Client:
    def __init__(
        self,
        url: yarl.URL,
        queue: Optional[str] = None,
        ssl_context: Optional[ssl.SSLContext] = None,
        service_name: str = "async_rabbitmq",
    ):
        self._url = url
        self._queue = queue
        self._ssl_context = ssl_context
        self._connection: Optional[aio_pika.abc.AbstractRobustConnection] = None
        self._channel: Optional[aio_pika.abc.AbstractRobustChannel] = None
        self._service_name = service_name

    async def __aenter__(self) -> "Client":
        self._connection = await aio_pika.connect_robust(self._url, ssl_context=self._ssl_context)
        self._channel = await self._connection.channel()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._connection.close()
        self._connection = None
        self._channel = None

    @classmethod
    def from_settings(cls, settings: config.Settings) -> "Client":
        return cls(
            url=settings.generate_url(),
            queue=settings.queue,
            ssl_context=settings.ssl_settings and settings.ssl_settings.ssl_context,
            service_name=settings.service_name,
        )

    @classmethod
    def serialize(cls, value: object, encoding: str = "utf-8") -> bytes:
        if value is None:
            raise ValueError("Cannot serialize None value")
        if hasattr(value, "dumps") and callable(value.dumps):
            data: str | bytes = value.dumps()
        elif hasattr(value, "model_dump_json") and callable(value.model_dump_json):
            data = value.model_dump_json(by_alias=True)
        else:
            data = jsons.dumps(value, jdkwargs={"ensure_ascii": False})
        return data if isinstance(data, bytes) else data.encode(encoding)

    async def send(
        self,
        value: object,
        headers: Optional[dict] = None,
        routing_key: Optional[str] = None,
        exchange: Optional[str] = None,
        **kwargs,
    ) -> None:
        await self.send_message(self.serialize(value), headers, routing_key=routing_key, exchange=exchange, **kwargs)

    async def send_message(
        self,
        data: bytes,
        headers: Optional[dict] = None,
        routing_key: Optional[str] = None,
        exchange: Optional[str] = None,
        **kwargs,
    ) -> None:
        if not self._channel:
            raise ValueError("Channel not open")
        if headers:
            headers = dict(headers)
            propagate.inject(headers)
        message = aio_pika.Message(
            data,
            headers=headers,
            delivery_mode=kwargs.pop("delivery_mode", DELIVERY_MODE),  # persistent
            content_type=kwargs.pop("content_type", CONTENT_TYPE),  # MIME-type
            content_encoding=kwargs.pop("content_encoding", CONTENT_ENCODING),
            priority=kwargs.pop("priority", PRIORITY),
            timestamp=kwargs.pop("timestamp", datetime.datetime.now(datetime.timezone.utc)),
            **kwargs,
        )
        if not exchange:
            exchange_ = self._channel.default_exchange
        else:
            exchange_ = await self._channel.get_exchange(exchange, ensure=True)
        routing_key = routing_key or self._queue
        if not routing_key:
            raise RuntimeError("Not set routing_key")
        try:
            await exchange_.publish(message, routing_key)
            PRODUCE_COUNTER.labels(self._service_name, "correct").inc()
        except Exception:
            PRODUCE_COUNTER.labels(self._service_name, "error").inc()
            raise

    async def fetch(
        self, *, queue: Optional[str] = None, no_ack: bool = False, fail: bool = True, timeout: int = 5
    ) -> Optional[Response]:
        queue = queue or self._queue
        if not queue:
            raise RuntimeError("Queue not set")
        if not self._channel:
            raise RuntimeError("Channel not open")
        queue_ = await self._channel.get_queue(queue)
        message = await queue_.get(no_ack=no_ack, fail=fail, timeout=timeout)  # noqa
        if not message:
            return None
        try:
            result = Response(
                data=json.loads(message.body.decode(CONTENT_ENCODING)),
                headers=dict(message.headers),
                message=message,
            )
            CONSUME_COUNTER.labels(self._service_name, "correct").inc()
        except Exception as exc:
            logger.critical(f"Skip rabbitmq message incorrect format {message.headers=}: {exc}")
            CONSUME_COUNTER.labels(self._service_name, "error").inc()
            await message.nack(requeue=False)
            return None
        return result

    async def receive(self) -> AsyncGenerator[Response, None]:
        queue = self._queue
        if not queue:
            raise RuntimeError("Queue not set")
        if not self._channel:
            raise RuntimeError("Channel not open")
        queue_ = await self._channel.get_queue(queue)
        async with queue_.iterator() as queue_iter:
            async for message in queue_iter:  # type: aio_pika.abc.AbstractIncomingMessage
                async with message.process(ignore_processed=True):
                    try:
                        result = Response(
                            data=json.loads(message.body.decode(CONTENT_ENCODING)),
                            headers=dict(message.headers),
                            message=message,
                        )
                        CONSUME_COUNTER.labels(self._service_name, "correct").inc()
                    except Exception as exc:
                        CONSUME_COUNTER.labels(self._service_name, "error").inc()
                        logger.critical(f"Skip rabbitmq message incorrect format {message.headers=}: {exc}")
                        await message.nack(requeue=False)
                        continue
                    yield result
