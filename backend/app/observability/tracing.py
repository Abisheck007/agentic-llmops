import logging

from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace

from backend.app.core.config import settings

logger = logging.getLogger(__name__)

_telemetry_configured = False


def configure_telemetry() -> bool:
    """Configure Azure Monitor once, when a connection string is available."""
    global _telemetry_configured

    if _telemetry_configured:
        return True

    connection_string = settings.applicationinsights_connection_string

    if not connection_string or not connection_string.strip():
        logger.warning(
            "Application Insights is not configured. "
            "Telemetry will not be exported to Azure."
        )
        return False

    configure_azure_monitor(
        connection_string=connection_string,
    )

    _telemetry_configured = True
    logger.info("Azure Monitor OpenTelemetry configured.")
    return True


def get_current_trace_id() -> str | None:
    """Return the active trace ID as a 32-character hexadecimal string."""
    span_context = trace.get_current_span().get_span_context()

    if not span_context.is_valid:
        return None

    return f"{span_context.trace_id:032x}"
