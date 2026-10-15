from opentelemetry import metrics

meter = metrics.get_meter("agentic_rag_platform", "1.0.0")

# API requests
api_requests = meter.create_counter(
    "agentic_rag.api.requests",
    description="Number of API query requests.",
    unit="{request}",
)

api_request_duration = meter.create_histogram(
    "agentic_rag.api.duration",
    description="API query duration.",
    unit="ms",
)

# Retrieval
retrieval_duration = meter.create_histogram(
    "agentic_rag.retrieval.duration",
    description="Azure AI Search retrieval duration.",
    unit="ms",
)

retrieved_documents = meter.create_histogram(
    "agentic_rag.retrieval.documents",
    description="Number of documents retrieved per query.",
    unit="{document}",
)

# LLM
llm_requests = meter.create_counter(
    "agentic_rag.llm.requests",
    description="Number of LLM requests.",
    unit="{request}",
)

llm_duration = meter.create_histogram(
    "agentic_rag.llm.duration",
    description="LLM request duration.",
    unit="ms",
)

llm_prompt_tokens = meter.create_counter(
    "agentic_rag.llm.prompt_tokens",
    description="Prompt tokens reported by the model API.",
    unit="{token}",
)

llm_completion_tokens = meter.create_counter(
    "agentic_rag.llm.completion_tokens",
    description="Completion tokens reported by the model API.",
    unit="{token}",
)
