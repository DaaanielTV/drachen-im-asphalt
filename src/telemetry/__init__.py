from __future__ import annotations

import atexit
import os
import sys
from typing import Optional

from opentelemetry import _metrics as metrics
from opentelemetry import trace
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc import OTLPSpanExporter
from opentelemetry.sdk._metrics.view import View
from opentelemetry.sdk._metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc._metric_exporter import OTLPMetricExporter

from src.telemetry import settings
from src.telemetry.metrics import create_game_metrics
from src.telemetry.logging import setup_telemetry_logging


_service_name = "drachen-im-asphalt"
_otel_endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
_otel_endpoint_insecure = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT_INSECURE", "true").lower() == "true"

_provider_initialized = False
_tracer_provider: Optional[TracerProvider] = None
_meter_provider: Optional[MeterProvider] = None


def initialize_telemetry(
    service_version: str = "1.0.0",
    enabled: bool = True,
) -> None:
    global _provider_initialized, _tracer_provider, _meter_provider

    if _provider_initialized:
        return

    user_settings = settings.load_user_settings()
    telemetry_enabled = enabled and user_settings.get("telemetry_enabled", True)

    if not telemetry_enabled:
        print("[Telemetry] Telemetry disabled by user settings.", file=sys.stderr)
        _provider_initialized = True
        return

    resource = Resource.create({
        SERVICE_NAME: _service_name,
        "service.version": service_version,
        "service.instance.id": os.environ.get("OTEL_SERVICE_INSTANCE_ID", "local"),
        "deployment.environment": os.environ.get("OTEL_DEPLOYMENT_ENVIRONMENT", "development"),
    })

    _tracer_provider = TracerProvider(resource=resource)
    try:
        span_exporter = OTLPSpanExporter(
            endpoint=_otel_endpoint,
            insecure=_otel_endpoint_insecure,
        )
        _tracer_provider.add_span_processor(
            BatchSpanProcessor(span_exporter)
        )
    except Exception as e:
        print(f"[Telemetry] Failed to create span exporter: {e}", file=sys.stderr)

    trace.set_tracer_provider(_tracer_provider)

    try:
        metric_reader = PeriodicExportingMetricReader(
            OTLPMetricExporter(
                endpoint=_otel_endpoint,
                insecure=_otel_endpoint_insecure,
            ),
            export_interval_millis=10000,
        )
        _meter_provider = MeterProvider(
            resource=resource,
            metric_readers=[metric_reader],
            views=[
                View(metric_name="game.*"),
            ],
        )
    except Exception as e:
        print(f"[Telemetry] Failed to create metric exporter: {e}", file=sys.stderr)
        _meter_provider = MeterProvider(resource=resource)

    metrics.set_meter_provider(_meter_provider)

    create_game_metrics()

    if user_settings.get("logging_enabled", True):
        log_level = user_settings.get("log_level", "INFO")
        setup_telemetry_logging(log_level)

    print(f"[Telemetry] Initialized successfully (endpoint: {_otel_endpoint})", file=sys.stderr)
    _provider_initialized = True

    atexit.register(shutdown_telemetry)


def shutdown_telemetry() -> None:
    global _tracer_provider, _meter_provider

    if _tracer_provider:
        _tracer_provider.shutdown()

    if _meter_provider:
        _meter_provider.shutdown()

    print("[Telemetry] Shutdown complete.", file=sys.stderr)


def get_tracer(name: str = __name__) -> trace.Tracer:
    return trace.get_tracer(name)


def get_meter(name: str = __name__) -> metrics.Meter:
    return metrics.get_meter(name)


def is_enabled() -> bool:
    user_settings = settings.load_user_settings()
    return user_settings.get("telemetry_enabled", True)


def reload_settings() -> None:
    global _provider_initialized
    if _provider_initialized:
        user_settings = settings.load_user_settings()
        current_enabled = user_settings.get("telemetry_enabled", True)
        if current_enabled:
            print("[Telemetry] Settings reloaded, telemetry active.", file=sys.stderr)
        else:
            print("[Telemetry] Telemetry disabled by user settings.", file=sys.stderr)