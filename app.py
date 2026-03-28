"""
HealthBuddy - Main Application
Entry point that orchestrates UI, agents, and workflow
"""

from dotenv import load_dotenv

# Load environment variables early
load_dotenv()

import streamlit as st
from config import initialize_clients, get_api_keys
from agents import AgentState, create_workflow
from ui_modern import (
    apply_custom_css,
    render_header,
    render_sidebar,
    render_input_section,
    render_analyze_button,
    render_results,
    render_footer,
)


def main():
    """Main application function."""
    st.set_page_config(
        page_title="HealthBuddy",
        page_icon="healthbuddy-logo.jpeg",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    groq_api_key, tavily_api_key = get_api_keys()
    if not groq_api_key or not tavily_api_key:
        st.error("Please set GROQ_API_KEY and TAVILY_API_KEY in your .env file")
        st.info(
            "Create a `.env` file in the project root with:\n```\n"
            "GROQ_API_KEY=your_key_here\n"
            "TAVILY_API_KEY=your_key_here\n```"
        )
        st.stop()

    llm, tavily_client, error = initialize_clients()
    if error:
        st.error(f"Error initializing clients: {error}")
        st.stop()

    theme = st.session_state.get("theme", "light")
    apply_custom_css(theme)

    render_header()
    render_sidebar()

    user_input = render_input_section()
    analyze_button = render_analyze_button()

    if "workflow" not in st.session_state:
        st.session_state.workflow = create_workflow(llm, tavily_client)

    if "results" not in st.session_state:
        st.session_state.results = None

    if analyze_button and user_input:
        with st.spinner("Analyzing symptoms and gathering information..."):
            try:
                initial_state: AgentState = {
                    "user_input": user_input,
                    "symptom_analysis": "",
                    "medication_advice": "",
                    "home_remedies": "",
                    "diet_lifestyle": "",
                    "doctor_recommendations": "",
                    "error": "",
                }

                result = st.session_state.workflow.invoke(initial_state)
                st.session_state.results = result
                st.session_state.last_input = user_input

            except Exception as exc:
                st.error(f"Error processing request: {exc}")
                st.session_state.results = None

    if st.session_state.results:
        render_results(st.session_state.results, st.session_state.get("last_input", ""))

    render_footer()


if __name__ == "__main__":
    main()
