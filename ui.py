"""
Streamlit UI Components
Contains all user interface elements and styling
"""

import streamlit as st


def apply_custom_css(theme="light"):
    """Apply custom CSS styling to the Streamlit app with theme support"""
    if theme == "dark":
        bg_color = "#0e1117"
        card_bg = "#1e2130"
        text_color = "#fafafa"
        border_color = "#4a9eff"
        header_color = "#4a9eff"
        disclaimer_bg = "#2d2a1e"
        input_bg = "#262730"
    else:
        bg_color = "#ffffff"
        card_bg = "#f8f9fa"
        text_color = "#262730"
        border_color = "#1f77b4"
        header_color = "#1f77b4"
        disclaimer_bg = "#fff3cd"
        input_bg = "#ffffff"
    
    st.markdown(f"""
    <style>
    /* Main Theme Variables */
    :root {{
        --bg-color: {bg_color};
        --card-bg: {card_bg};
        --text-color: {text_color};
        --border-color: {border_color};
        --header-color: {header_color};
        --disclaimer-bg: {disclaimer_bg};
        --input-bg: {input_bg};
    }}
    
    /* Global Styles */
    .stApp {{
        background: linear-gradient(135deg, {bg_color} 0%, {card_bg} 100%);
    }}
    
    [data-testid="stAppViewContainer"] {{
        background-color: {bg_color};
        color: {text_color};
    }}
    
    /* Header Styles */
    .main-header {{
        font-size: 2.8rem;
        font-weight: 700;
        color: {header_color};
        text-align: center;
        margin-bottom: 1rem;
        padding: 1rem;
        background: linear-gradient(135deg, {header_color}15 0%, {header_color}05 100%);
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        animation: fadeInDown 0.6s ease-out;
    }}
    
    /* Agent Cards */
    .agent-card {{
        background-color: {card_bg};
        padding: 2rem;
        border-radius: 15px;
        margin: 1.5rem 0;
        border-left: 5px solid {border_color};
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        line-height: 1.8;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        animation: fadeInUp 0.5s ease-out;
    }}
    
    .agent-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.2);
    }}
    
    /* Section Headers */
    h3 {{
        color: {header_color};
        margin-top: 2rem;
        margin-bottom: 1rem;
        font-size: 1.6rem;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }}
    
    /* Button Styles */
    .stButton>button {{
        width: 100%;
        background: linear-gradient(135deg, {border_color} 0%, {header_color} 100%);
        color: white;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        border-radius: 10px;
        border: none;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        font-size: 1.1rem;
    }}
    
    .stButton>button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.2);
        background: linear-gradient(135deg, {header_color} 0%, {border_color} 100%);
    }}
    
    /* Text Area */
    .stTextArea>div>div>textarea {{
        background-color: {input_bg};
        color: {text_color};
        border: 2px solid {border_color}40;
        border-radius: 10px;
        padding: 1rem;
        transition: border-color 0.3s ease;
    }}
    
    .stTextArea>div>div>textarea:focus {{
        border-color: {border_color};
        box-shadow: 0 0 0 3px {border_color}20;
    }}
    
    /* Disclaimer */
    .disclaimer {{
        background-color: {disclaimer_bg};
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #ffc107;
        margin-top: 2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }}
    
    /* Sidebar Enhancements */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {card_bg} 0%, {bg_color} 100%);
    }}
    
    /* Animations */
    @keyframes fadeInDown {{
        from {{
            opacity: 0;
            transform: translateY(-20px);
        }}
        to {{
            opacity: 1;
            transform: translateY(0);
        }}
    }}
    
    @keyframes fadeInUp {{
        from {{
            opacity: 0;
            transform: translateY(20px);
        }}
        to {{
            opacity: 1;
            transform: translateY(0);
        }}
    }}
    
    /* Scrollbar Styling */
    ::-webkit-scrollbar {{
        width: 10px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: {card_bg};
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: {border_color};
        border-radius: 5px;
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: {header_color};
    }}
    
    /* Loading Spinner Enhancement */
    .stSpinner>div {{
        border-color: {border_color} transparent {border_color} transparent;
    }}
    
    /* Info Boxes */
    .stInfo {{
        background-color: {card_bg};
        border-left: 4px solid {border_color};
    }}
    
    /* Markdown Tables */
    table {{
        border-collapse: collapse;
        width: 100%;
        margin: 1rem 0;
        background-color: {card_bg};
        border-radius: 8px;
        overflow: hidden;
    }}
    
    table th {{
        background-color: {border_color};
        color: white;
        padding: 0.75rem;
        text-align: left;
    }}
    
    table td {{
        padding: 0.75rem;
        border-bottom: 1px solid {border_color}30;
    }}
    
    table tr:hover {{
        background-color: {border_color}10;
    }}
    </style>
    """, unsafe_allow_html=True)


def render_header():
    """Render the main header with enhanced styling"""
    st.markdown('<div class="main-header">🩺 AI Healthcare Assistant</div>', unsafe_allow_html=True)
    
    # Subtitle with badges
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <p style="font-size: 1.2rem; color: var(--text-color); margin-bottom: 1rem;">
                Multi-Agent System for Comprehensive Health Analysis
            </p>
            <div style="display: flex; justify-content: center; gap: 1rem; flex-wrap: wrap;">
                <span style="background: linear-gradient(135deg, #1f77b4, #4a9eff); color: white; padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.9rem;">
                    🤖 AI-Powered
                </span>
                <span style="background: linear-gradient(135deg, #28a745, #20c997); color: white; padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.9rem;">
                    🔍 Real-Time Data
                </span>
                <span style="background: linear-gradient(135deg, #ff6b6b, #ee5a6f); color: white; padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.9rem;">
                    ⚡ Fast Analysis
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_sidebar():
    """Render the sidebar with settings and information"""
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        
        # Initialize theme (default to light, no UI controls)
        if "theme" not in st.session_state:
            st.session_state.theme = "light"
        
        st.markdown("---")
        
        # Enhanced Info Section
        with st.expander("ℹ️ How it works", expanded=False):
            st.markdown("""
            **Step-by-step process:**
            1. 📝 Enter your symptoms
            2. 🧠 AI agents analyze your condition
            3. 💊 Get medication recommendations
            4. 🌿 Discover home remedies
            5. 🥗 Receive diet & lifestyle advice
            6. 👨‍⚕️ Find doctor recommendations
            7. ⚠️ Always consult a doctor for serious conditions
            """)
        
        st.markdown("---")
        
        # Features Section
        st.markdown("### ✨ Features")
        st.markdown("""
        - 🧠 **Symptom Analysis**
        - 💊 **Medication Advice**
        - 🌿 **Home Remedies**
        - 🥗 **Diet & Lifestyle**
        - 👨‍⚕️ **Doctor Recommendations**
        """)
        
        st.markdown("---")
        
        # Tech Stack
        st.markdown("### 🔧 Built With")
        st.markdown("""
        - **LangGraph** - Multi-agent workflow
        - **Groq LLM** - AI reasoning
        - **Tavily API** - Real-time data
        - **Streamlit** - Interactive UI
        """)
        
        st.markdown("---")
        
        # Quick Stats (if results exist)
        if "results" in st.session_state and st.session_state.results:
            st.markdown("### 📊 Analysis Status")
            results = st.session_state.results
            completed = sum([
                1 for key in ["symptom_analysis", "medication_advice", 
                             "home_remedies", "diet_lifestyle", "doctor_recommendations"]
                if results.get(key)
            ])
            st.progress(completed / 5)
            st.caption(f"{completed}/5 agents completed")
        
        st.markdown("---")
        st.caption("© 2024 AI Healthcare Assistant")


def render_input_section():
    """Render the input section for user symptoms with enhanced styling"""
    st.markdown("### 📝 Describe Your Symptoms")
    st.markdown("Share your symptoms, health concerns, or questions below:")
    
    user_input = st.text_area(
        "Enter your symptoms:",
        height=180,
        placeholder="e.g., I've been experiencing headaches and fatigue for the past week. I also have a slight fever and body aches...",
        label_visibility="collapsed"
    )
    
    # Helper text
    if not user_input:
        st.caption("💡 Tip: Be as detailed as possible for better analysis results")
    
    return user_input


def render_analyze_button():
    """Render the analyze button with enhanced styling"""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        analyze_button = st.button(
            "🔍 Analyze Symptoms", 
            type="primary", 
            use_container_width=True,
            help="Click to start comprehensive health analysis"
        )
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




def render_footer():
    """Render the footer"""
    st.markdown("---")
    st.caption("© 202 AI Healthcare Assistant | Powered by LangGraph, Groq LLM, and Tavily API")

