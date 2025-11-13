"""
AI Healthcare Assistant - Main Application
Entry point that orchestrates UI, agents, and workflow
"""

import streamlit as st
from config import initialize_clients, get_api_keys
from agents import AgentState, create_workflow
from ui import (
    apply_custom_css,
    render_header,
    render_sidebar,
    render_input_section,
    render_analyze_button,
    render_results,
    render_footer
)


def main():
    """Main application function"""
    st.set_page_config(
        page_title="AI Healthcare Assistant",
        page_icon="🩺",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Check for API keys
    groq_api_key, tavily_api_key = get_api_keys()
    if not groq_api_key or not tavily_api_key:
        st.error("⚠️ Please set GROQ_API_KEY and TAVILY_API_KEY in your .env file")
        st.info("Create a `.env` file in the project root with:\n```\nGROQ_API_KEY=your_key_here\nTAVILY_API_KEY=your_key_here\n```")
        st.stop()
    
    # Initialize API clients
    llm, tavily_client, error = initialize_clients()
    if error:
        st.error(f"Error initializing clients: {error}")
        st.stop()
    
    # Apply custom CSS with theme support
    theme = st.session_state.get("theme", "light")
    apply_custom_css(theme)
    
    # Render header
    render_header()
    
    # Render sidebar
    render_sidebar()
    
    # Render input section
    user_input = render_input_section()
    
    # Render analyze button
    analyze_button = render_analyze_button()
    
    # Initialize workflow in session state
    if "workflow" not in st.session_state:
        st.session_state.workflow = create_workflow(llm, tavily_client)
    
    if "results" not in st.session_state:
        st.session_state.results = None
    
    # Process analysis
    if analyze_button and user_input:
        with st.spinner("🧠 Analyzing symptoms and gathering information..."):
            try:
                # Initialize state
                initial_state: AgentState = {
                    "user_input": user_input,
                    "symptom_analysis": "",
                    "medication_advice": "",
                    "home_remedies": "",
                    "diet_lifestyle": "",
                    "doctor_recommendations": "",
                    "error": ""
                }
                
                # Run workflow
                result = st.session_state.workflow.invoke(initial_state)
                st.session_state.results = result
                
            except Exception as e:
                st.error(f"Error processing request: {str(e)}")
                st.session_state.results = None
    
    # Display results
    if st.session_state.results:
        render_results(st.session_state.results)
    
    # Render footer
    render_footer()


if __name__ == "__main__":
    main()
