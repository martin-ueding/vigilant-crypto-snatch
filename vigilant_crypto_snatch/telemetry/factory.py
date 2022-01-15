from .interface import NullTelemetryCollector
from .interface import TelemetryCollector
from .interface import TelemetryConfig


def make_telemetry_collector(telemetry_config: TelemetryConfig) -> TelemetryCollector:
    if telemetry_config.collect:
        from .sentry_adapter import SentryTelemetryCollector

        return SentryTelemetryCollector()
    else:
        return NullTelemetryCollector()
