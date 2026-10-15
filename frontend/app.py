import os
import uuid

import requests
import streamlit as st

# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Agentic RAG Platform",
    page_icon="🤖",
    layout="wide",
)

BACKEND_API_URL = os.getenv(
    "BACKEND_API_URL",
    "http://127.0.0.1:8000",
).rstrip("/")

QUERY_ENDPOINT = f"{BACKEND_API_URL}/api/v1/query"
HEALTH_ENDPOINT = f"{BACKEND_API_URL}/"


# --------------------------------------------------
# Session state
# --------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())


# --------------------------------------------------
# Header and sidebar
# --------------------------------------------------

st.title("🤖 Agentic RAG Platform")
st.caption(
    "An LLMOps and AgentOps application powered by "
    "Azure OpenAI, Azure AI Search, and LangGraph."
)

with st.sidebar:
    st.header("Platform")

    st.write("**Backend API**")
    st.code(BACKEND_API_URL, language=None)

    if st.button("Check backend connection", use_container_width=True):
        try:
            response = requests.get(
                HEALTH_ENDPOINT,
                timeout=5,
            )
            response.raise_for_status()

            st.success("Backend is reachable.")
            st.json(response.json())

        except requests.RequestException as exc:
            st.error(f"Backend connection failed: {exc}")

    st.divider()

    st.write("**Conversation**")
    st.caption(f"Session: {st.session_state.session_id[:8]}...")

    if st.button("New conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()

    st.divider()

    st.caption("Powered by FastAPI + LangGraph + Azure services.")


# --------------------------------------------------
# Source display
# --------------------------------------------------


def display_sources(sources):
    if not sources:
        st.info("No source documents were returned.")
        return

    for index, source in enumerate(sources, start=1):
        title = source.get("title") or "Untitled document"
        document_id = source.get("document_id", "unknown")

        with st.expander(f"[{index}] {title} — {document_id}"):
            st.write(source.get("content", ""))

            page_number = source.get("page_number")
            if page_number is not None:
                st.caption(f"Page: {page_number}")

            source_url = source.get("source_url")
            if source_url:
                st.markdown(f"[Open source]({source_url})")


# --------------------------------------------------
# Render previous messages
# --------------------------------------------------

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if message["role"] == "assistant":
            sources = message.get("sources", [])

            if sources:
                with st.expander(f"Sources ({len(sources)})"):
                    display_sources(sources)

            trace_id = message.get("trace_id")
            if trace_id:
                with st.expander("Observability details"):
                    st.code(trace_id, language=None)

            agent_steps = message.get("agent_steps", [])
            if agent_steps:
                with st.expander("Agent execution steps"):
                    for step in agent_steps:
                        st.write(f"- {step}")


# --------------------------------------------------
# Chat input and API request
# --------------------------------------------------

question = st.chat_input("Ask a question about your knowledge base...")

if question:
    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        try:
            with st.spinner("Searching documents and generating an answer..."):
                response = requests.post(
                    QUERY_ENDPOINT,
                    json={
                        "question": question,
                        "session_id": st.session_state.session_id,
                    },
                    timeout=120,
                )

                response.raise_for_status()
                data = response.json()

            answer = data.get(
                "answer",
                "The API returned no answer.",
            )

            sources = data.get("sources", [])
            trace_id = data.get("trace_id")
            agent_steps = data.get("agent_steps", [])

            st.markdown(answer)

            if sources:
                with st.expander(
                    f"Sources ({len(sources)})",
                    expanded=True,
                ):
                    display_sources(sources)

            if trace_id:
                with st.expander("Observability details"):
                    st.code(trace_id, language=None)

            if agent_steps:
                with st.expander("Agent execution steps"):
                    for step in agent_steps:
                        st.write(f"- {step}")

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer,
                    "sources": sources,
                    "trace_id": trace_id,
                    "agent_steps": agent_steps,
                }
            )

        except requests.Timeout:
            error_message = "The request timed out. Please try again."
            st.error(error_message)

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": error_message,
                }
            )

        except requests.HTTPError as exc:
            status_code = (
                exc.response.status_code if exc.response is not None else "unknown"
            )

            error_message = (
                f"The backend returned HTTP {status_code}. "
                "Check the FastAPI terminal for details."
            )
            st.error(error_message)

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": error_message,
                }
            )

        except requests.RequestException:
            error_message = (
                "Cannot reach the backend. Ensure FastAPI "
                "is running and the backend URL is correct."
            )
            st.error(error_message)

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": error_message,
                }
            )
