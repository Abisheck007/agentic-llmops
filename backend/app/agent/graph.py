from langgraph.graph import END, START, StateGraph
from opentelemetry import trace

tracer = trace.get_tracer(__name__)
from backend.app.agent.nodes import (
    evaluate_context_node,
    generate_answer_node,
    no_context_node,
    retrieve_node,
)
from backend.app.agent.state import AgentState


def route_after_evaluation(state: AgentState) -> str:
    """Choose the next node based on the retrieved context."""

    if state.get("context_sufficient", False):
        return "generate_answer"

    return "no_context"


def build_agent_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("evaluate_context", evaluate_context_node)
    workflow.add_node("generate_answer", generate_answer_node)
    workflow.add_node("no_context", no_context_node)

    workflow.add_edge(START, "retrieve")
    workflow.add_edge("retrieve", "evaluate_context")

    workflow.add_conditional_edges(
        "evaluate_context",
        route_after_evaluation,
        {
            "generate_answer": "generate_answer",
            "no_context": "no_context",
        },
    )

    workflow.add_edge("generate_answer", END)
    workflow.add_edge("no_context", END)

    return workflow.compile()


# Compile once and reuse the graph.
agent_graph = build_agent_graph()


async def run_agent(
    question: str,
    session_id: str | None = None,
) -> AgentState:
    """Execute and trace one agent workflow."""

    initial_state: AgentState = {
        "question": question,
        "session_id": session_id,
        "sources": [],
        "context_sufficient": False,
        "answer": "",
        "steps": [],
    }

    with tracer.start_as_current_span("agent.run") as span:
        span.set_attribute("agent.name", "agentic_rag")
        span.set_attribute("agent.framework", "langgraph")

        result = await agent_graph.ainvoke(initial_state)

        span.set_attribute(
            "agent.step_count",
            len(result.get("steps", [])),
        )
        span.set_attribute(
            "agent.source_count",
            len(result.get("sources", [])),
        )
        span.set_attribute(
            "agent.context_sufficient",
            result.get("context_sufficient", False),
        )

        return result
