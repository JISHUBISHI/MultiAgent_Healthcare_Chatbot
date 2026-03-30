"""Analysis feature service layer."""

from __future__ import annotations

from healthbuddy.core.clients import get_api_keys, initialize_clients
from healthbuddy.features.analysis.workflow import AgentState, create_workflow

_workflow = None
_workflow_error = None


def get_workflow():
    """Initialize and cache the LangGraph workflow."""
    global _workflow, _workflow_error
    if _workflow is not None or _workflow_error is not None:
        return _workflow, _workflow_error

    groq_api_key, tavily_api_key = get_api_keys()
    if not groq_api_key or not tavily_api_key:
        _workflow_error = "Missing GROQ_API_KEY or TAVILY_API_KEY in the environment."
        return None, _workflow_error

    llm, tavily_client, error = initialize_clients()
    if error:
        _workflow_error = error
        return None, _workflow_error

    _workflow = create_workflow(llm, tavily_client)
    return _workflow, None


def run_health_analysis(user_input: str) -> dict:
    """Run the full healthcare workflow for the provided symptoms."""
    workflow, error = get_workflow()
    if error:
        raise RuntimeError(error)

    initial_state: AgentState = {
        "user_input": user_input,
        "symptom_analysis": "",
        "medication_advice": "",
        "home_remedies": "",
        "diet_lifestyle": "",
        "doctor_recommendations": "",
        "error": "",
    }
    return workflow.invoke(initial_state)

