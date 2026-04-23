from __future__ import annotations

from typing import Dict, Optional

from opentelemetry import _metrics as metrics
from opentelemetry import trace

from src.telemetry import settings


_tracer: Optional[trace.Tracer] = None
_meter: Optional[metrics.Meter] = None


_session_counter: Optional[metrics.Counter] = None
_session_duration_historgram: Optional[metrics.Histogram] = None
_command_counter: Optional[metrics.Counter] = None
_mission_started_counter: Optional[metrics.Counter] = None
_mission_completed_counter: Optional[metrics.Counter] = None
_mission_duration_histogram: Optional[metrics.Histogram] = None
_combat_outcome_counter: Optional[metrics.Counter] = None
_attribute_change_counter: Optional[metrics.Counter] = None
_error_counter: Optional[metrics.Counter] = None
_save_counter: Optional[metrics.Counter] = None
_load_counter: Optional[metrics.Counter] = None
_player_level_gauge: Optional[metrics.UpDownCounter] = None


def create_game_metrics() -> None:
    global _tracer, _meter
    global _session_counter, _session_duration_historgram
    global _command_counter
    global _mission_started_counter, _mission_completed_counter, _mission_duration_histogram
    global _combat_outcome_counter
    global _attribute_change_counter
    global _error_counter
    global _save_counter, _load_counter
    global _player_level_gauge

    if not settings.get_telemetry_enabled():
        return

    _tracer = trace.get_tracer(__name__)
    _meter = metrics.get_meter(__name__)

    _session_counter = _meter.create_counter(
        name="game.session.start",
        description="Number of game sessions started",
        unit="1",
    )

    _session_duration_historgram = _meter.create_histogram(
        name="game.session.duration",
        description="Duration of game sessions in seconds",
        unit="s",
    )

    _command_counter = _meter.create_counter(
        name="game.command.executed",
        description="Commands executed by type",
        unit="1",
    )

    _mission_started_counter = _meter.create_counter(
        name="game.mission.started",
        description="Missions started",
        unit="1",
    )

    _mission_completed_counter = _meter.create_counter(
        name="game.mission.completed",
        description="Missions completed",
        unit="1",
    )

    _mission_duration_histogram = _meter.create_histogram(
        name="game.mission.duration",
        description="Duration of mission completion",
        unit="s",
    )

    _combat_outcome_counter = _meter.create_counter(
        name="game.combat.outcome",
        description="Combat outcomes",
        unit="1",
    )

    _attribute_change_counter = _meter.create_counter(
        name="game.attribute.change",
        description="Player attribute changes",
        unit="1",
    )

    _error_counter = _meter.create_counter(
        name="game.error",
        description="Errors during gameplay",
        unit="1",
    )

    _save_counter = _meter.create_counter(
        name="game.save",
        description="Game saves",
        unit="1",
    )

    _load_counter = _meter.create_counter(
        name="game.load",
        description="Game loads",
        unit="1",
    )

    _player_level_gauge = _meter.create_up_down_counter(
        name="game.player.level",
        description="Player level",
        unit="1",
    )


def record_session_start(player_name: str, character_type: str) -> None:
    if _session_counter and settings.get_telemetry_enabled():
        _session_counter.add(1, {
            "player_name": player_name,
            "character_type": character_type,
        })


def record_session_duration(duration_seconds: float) -> None:
    if _session_duration_historgram and settings.get_telemetry_enabled():
        _session_duration_historgram.record(duration_seconds)


def record_command(command_type: str) -> None:
    if _command_counter and settings.get_telemetry_enabled():
        _command_counter.add(1, {"command": command_type})


def record_mission_start(mission_id: str) -> None:
    if _mission_started_counter and settings.get_telemetry_enabled():
        _mission_started_counter.add(1, {"mission_id": mission_id})


def record_mission_completion(mission_id: str, duration_seconds: float) -> None:
    if _mission_completed_counter and settings.get_telemetry_enabled():
        _mission_completed_counter.add(1, {"mission_id": mission_id})
    if _mission_duration_histogram and settings.get_telemetry_enabled():
        _mission_duration_histogram.record(duration_seconds)


def record_combat_outcome(outcome: str, enemy_type: str) -> None:
    if _combat_outcome_counter and settings.get_telemetry_enabled():
        _combat_outcome_counter.add(1, {
            "outcome": outcome,
            "enemy_type": enemy_type,
        })


def record_attribute_change(
    attribute: str,
    old_value: int,
    new_value: int,
) -> None:
    if _attribute_change_counter and settings.get_telemetry_enabled():
        delta = new_value - old_value
        _attribute_change_counter.add(1, {
            "attribute": attribute,
            "delta": str(delta),
        })


def record_error(error_type: str, message: str) -> None:
    if _error_counter and settings.get_telemetry_enabled():
        _error_counter.add(1, {
            "error_type": error_type,
            "message": message[:100],
        })


def record_save(player_name: str) -> None:
    if _save_counter and settings.get_telemetry_enabled():
        _save_counter.add(1, {"player_name": player_name})


def record_load(player_name: str) -> None:
    if _load_counter and settings.get_telemetry_enabled():
        _load_counter.add(1, {"player_name": player_name})


def set_player_level(level: int) -> None:
    if _player_level_gauge and settings.get_telemetry_enabled():
        _player_level_gauge.set(level, {"level": str(level)})


def trace_operation(
    operation_name: str,
    attributes: Optional[Dict[str, str]] = None,
) -> trace.Span:
    if not _tracer or not settings.get_telemetry_enabled():
        return trace.NoOpTracer().start_span(operation_name)

    return _tracer.start_span(operation_name, attributes=attributes)


def get_tracer() -> trace.Tracer:
    return _tracer or trace.NoOpTracer()