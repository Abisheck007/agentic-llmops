import logging

from backend.app.core.config import settings
from backend.app.observability.tracing import configure_telemetry

logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(
    logging.WARNING
)

logging.getLogger("azure.monitor.opentelemetry.exporter").setLevel(logging.WARNING)

logging.getLogger("azure.monitor.opentelemetry.exporter.export").setLevel(
    logging.WARNING
)

# Configure telemetry before importing and using the API routes.
configure_telemetry()

from fastapi import FastAPI
from backend.app.api.routes import router

app = FastAPI(
    title=settings.app_name,
    description=("An Agentic RAG platform combining LLMOps and AgentOps."),
    version="0.2.0",
)

app.include_router(router)


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Agentic RAG Platform API",
        "status": "running",
        "docs": "/docs",
    }
