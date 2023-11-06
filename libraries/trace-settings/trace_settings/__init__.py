from typing import Optional, Type, Union

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider, export

from trace_settings import config

__all__ = ("config", "basic_config")


def basic_config(settings: Optional[config.Settings] = None):
    settings = config.get_settings(settings)
    if not settings.exporter:
        return
    provider = TracerProvider()
    exporter_cls: Type[export.ConsoleSpanExporter] = getattr(export, settings.exporter)
    processor_cls: Type[Union[export.BatchSpanProcessor, export.SimpleSpanProcessor]] = getattr(
        export, settings.processor
    )
    processor = processor_cls(exporter_cls())
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
