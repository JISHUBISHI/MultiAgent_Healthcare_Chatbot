"""
Streamlit UI Components
Contains all user interface elements and styling
"""

import streamlit as st


def apply_custom_css():
    """Apply custom CSS styling to the Streamlit app"""
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .agent-card {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        margin: 1.5rem 0;
        border-left: 5px solid #1f77b4;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        line-height: 1.8;
    }
    h3 {
        color: #1f77b4;
        margin-top: 2rem;
        margin-bottom: 1rem;
        font-size: 1.5rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
        padding: 0.5rem 1rem;
        border-radius: 5px;
    }
    .stButton>button:hover {
        background-color: #1565c0;
    }
    .disclaimer {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #ffc107;
        margin-top: 2rem;
    }
    [data-testid="stAppViewContainer"] {
        background-color: #ffffff;
    }
    </style>
    """, unsafe_allow_html=True)


def render_header():
    """Render the main header"""
    st.markdown('<div class="main-header">🩺 AI Healthcare Assistant</div>', unsafe_allow_html=True)
    st.markdown("### Multi-Agent System for Comprehensive Health Analysis")


def render_sidebar():
    """Render the sidebar with settings and information"""
    with st.sidebar:
        st.header("⚙️ Settings")
        theme = st.selectbox("Theme", ["Light", "Dark"], index=0)
        st.markdown("---")
        st.info("""
        **How it works:**
        1. Enter your symptoms
        2. AI agents analyze your condition
        3. Get comprehensive health advice
        4. Always consult a doctor for serious conditions
        """)
        st.markdown("---")
        st.caption("Built with LangGraph, Groq LLM, and Tavily API")


def render_input_section():
    """Render the input section for user symptoms"""
    st.markdown("### Describe Your Symptoms")
    user_input = st.text_area(
        "Enter your symptoms, health concerns, or questions:",
        height=150,
        placeholder="e.g., I've been experiencing headaches and fatigue for the past week..."
    )
    return user_input


def render_analyze_button():
    """Render the analyze button"""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        analyze_button = st.button("🔍 Analyze Symptoms", type="primary", use_container_width=True)
    return analyze_button


def render_results(results):
    """Render the analysis results all at once without dropdowns"""
    if not results:
        return
    
    st.markdown("---")
    st.markdown("## 📊 Complete Health Analysis")
    
    # Symptom Analysis
    if results.get("symptom_analysis"):
        st.markdown("### 🧠 Symptom Analysis")
        st.markdown('<div class="agent-card">', unsafe_allow_html=True)
        st.markdown(results["symptom_analysis"])
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("")
    
    # Medication Advice
    if results.get("medication_advice"):
        st.markdown("### 💊 Medication Advice")
        st.markdown('<div class="agent-card">', unsafe_allow_html=True)
        st.markdown(results["medication_advice"])
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("")
    
    # Home Remedies
    if results.get("home_remedies"):
        st.markdown("### 🌿 Home Remedies")
        st.markdown('<div class="agent-card">', unsafe_allow_html=True)
        st.markdown(results["home_remedies"])
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("")
    
    # Diet & Lifestyle
    if results.get("diet_lifestyle"):
        st.markdown("### 🥗 Diet & Lifestyle Recommendations")
        st.markdown('<div class="agent-card">', unsafe_allow_html=True)
        st.markdown(results["diet_lifestyle"])
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("")
    
    # Doctor Recommendations
    if results.get("doctor_recommendations"):
        st.markdown("### 👨‍⚕️ Doctor Recommendations")
        st.markdown('<div class="agent-card">', unsafe_allow_html=True)
        st.markdown(results["doctor_recommendations"])
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("")
    
    # Error handling
    if results.get("error"):
        st.warning(f"⚠️ Some errors occurred: {results['error']}")


def render_disclaimer():
    """Render the disclaimer footer"""
    st.markdown("---")
    st.markdown("""
    <div class="disclaimer">
        <strong>⚠️ Important Disclaimer:</strong><br>
        This AI Healthcare Assistant is designed for informational and educational purposes only. 
        It does not provide medical diagnosis, treatment, or professional medical advice. 
        Always consult with a qualified healthcare provider for any health concerns or before making 
        any medical decisions. In case of a medical emergency, contact your local emergency services immediately.
    </div>
    """, unsafe_allow_html=True)


def render_footer():
    """Render the footer"""
    st.markdown("---")
    st.caption("© 2024 AI Healthcare Assistant | Powered by LangGraph, Groq LLM, and Tavily API")

