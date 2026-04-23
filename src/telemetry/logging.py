from __future__ import annotations

import logging
import sys
from typing import Dict, Optional

from opentelemetry import trace
from src.telemetry import settings


_loggers: Dict[str, "TelemetryLogger"] = {}
_root_logger_initialized = False


def _get_trace_context() -> Dict[str, str]:
    current_span = trace.get_current_span()
    if current_span and current_span.context.trace_id != 0:
        return {
            "trace_id": format(current_span.context.trace_id, '032x'),
            "span_id": format(current_span.context.span_id, '016x'),
        }
    return {}


def setup_telemetry_logging(level: str = "INFO") -> None:
    global _root_logger_initialized

    if not settings.is_logging_enabled():
        return

    log_level = getattr(logging, level.upper(), logging.INFO)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    handler = TelemetryLogHandler()
    handler.setLevel(log_level)

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    for existing_handler in root_logger.handlers[:]:
        if isinstance(existing_handler, TelemetryLogHandler):
            continue
        root_logger.removeHandler(existing_handler)

    root_logger.addHandler(handler)

    _root_logger_initialized = True
    logging.info("[Telemetry] Logging initialized with trace correlation")


class TelemetryLogHandler(logging.Handler):
    def __init__(self, level: int = logging.NOTSET) -> None:
        super().__init__(level)
        self._formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        )

    def emit(self, record: logging.LogRecord) -> None:
        if not settings.is_logging_enabled():
            return

        try:
            ctx = _get_trace_context()
            if ctx:
                record.msg = f"[trace={ctx.get('trace_id', 'none')}] {record.msg}"
                record.traceId = ctx.get("trace_id", "0")
                record.spanId = ctx.get("span_id", "0")

            msg = self.format(record)
            level = record.levelno

            if level >= logging.ERROR:
                sys.stderr.write(msg + "\n")
            elif level >= logging.WARNING:
                sys.stderr.write(msg + "\n")
            else:
                sys.stdout.write(msg + "\n")

        except Exception:
            self.handleError(record)


class TelemetryLogger:
    def __init__(self, name: str) -> None:
        self._logger = logging.getLogger(name)
        self._name = name

    def debug(self, message: str, **kwargs: str) -> None:
        if not settings.is_logging_enabled():
            return
        self._logger.debug(message, extra=kwargs)

    def info(self, message: str, **kwargs: str) -> None:
        if not settings.is_logging_enabled():
            return
        self._logger.info(message, extra=kwargs)

    def warning(self, message: str, **kwargs: str) -> None:
        if not settings.is_logging_enabled():
            return
        self._logger.warning(message, extra=kwargs)

    def error(self, message: str, **kwargs: str) -> None:
        if not settings.is_logging_enabled():
            return
        self._logger.error(message, extra=kwargs)

    def critical(self, message: str, **kwargs: str) -> None:
        self._logger.critical(message, extra=kwargs)


def get_logger(name: str) -> TelemetryLogger:
    if name not in _loggers:
        _loggers[name] = TelemetryLogger(name)
    return _loggers[name]


def log_with_trace(
    message: str,
    level: str = "INFO",
    **attributes: str,
) -> None:
    if not settings.is_logging_enabled():
        return

    ctx = _get_trace_context()
    combined = {**ctx, **attributes}
    logger = logging.getLogger("game")

    log_method = getattr(logger, level.lower(), logger.info)
    log_method(message, extra=combined)