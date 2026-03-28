"""
Streamlit UI Components
Contains all user interface elements and styling
"""

import streamlit as st
import pandas as pd

from pdf_generator import generate_pdf_report
from table_format import build_master_recommendation_rows, segment_markdown_content

def apply_custom_css(theme="dark"):
    """Apply custom CSS styling to the Streamlit app with premium glassmorphic dark theme"""
    
    # Premium Dark Theme Constants
    bg_color = "#030305"
    card_bg = "rgba(22, 22, 28, 0.65)"
    text_color = "#e2e8f0"
    border_color = "#6366f1"
    header_color = "#8b5cf6"
    disclaimer_bg = "rgba(255, 193, 7, 0.08)"
    input_bg = "rgba(0, 0, 0, 0.4)"
    glow_color = "rgba(99, 102, 241, 0.3)"
    
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
        --glow: {glow_color};
    }}
    
    /* Global Styles */
    @keyframes gradientBG {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}
    .stApp {{
        background: linear-gradient(to bottom, rgba(3, 3, 5, 0.85), rgba(17, 15, 28, 0.9)), url('https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?ixlib=rb-4.0.3&auto=format&fit=crop&w=2070&q=80');
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
    }}
    
    [data-testid="stAppViewContainer"] {{
        background-color: transparent;
        color: {text_color};
    }}
    
    /* Header Styles */
    @keyframes textShine {{
        0% {{ background-position: 0% 50%; }}
        100% {{ background-position: 200% 50%; }}
    }}
    .main-header {{
        font-size: 3.2rem;
        font-weight: 800;
        background: linear-gradient(to right, #6366f1, #d946ef, #8b5cf6, #6366f1);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        padding: 1rem;
        animation: fadeInDown 0.8s ease-out, textShine 4s linear infinite;
        letter-spacing: -1px;
    }}
    
    /* Agent Cards (Glassmorphism) */
    .agent-card {{
        background-color: {card_bg};
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        padding: 2.5rem;
        border-radius: 20px;
        margin: 1.5rem 0;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-left: 4px solid {border_color};
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        line-height: 1.8;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        animation: fadeInUp 0.6s ease-out backwards;
    }}
    
    .agent-card:hover {{
        transform: translateY(-5px);
        border-color: rgba(99, 102, 241, 0.4);
        border-left: 4px solid #d946ef;
        box-shadow: 0 15px 40px 0 rgba(0, 0, 0, 0.5), 0 0 20px {glow_color};
    }}
    
    /* Section Headers */
    h3 {{
        color: {text_color};
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
        border-radius: 12px;
        border: none;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px {glow_color};
        font-size: 1.1rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    
    @keyframes pulseGlow {{
        0% {{ box-shadow: 0 4px 15px {glow_color}; }}
        50% {{ box-shadow: 0 8px 25px rgba(217, 70, 239, 0.6); }}
        100% {{ box-shadow: 0 4px 15px {glow_color}; }}
    }}
    .stButton>button:hover {{
        transform: translateY(-2px) scale(1.02);
        animation: pulseGlow 1.5s infinite;
        background: linear-gradient(135deg, {header_color} 0%, {border_color} 100%);
    }}
    
    /* Text Area Animation and Styling */
    .stTextArea {{
        animation: fadeInUp 0.8s ease-out;
    }}
    .stTextArea>div>div>textarea {{
        background-color: rgba(10, 10, 15, 0.5);
        color: white;
        border: 2px solid rgba(99, 102, 241, 0.2);
        border-radius: 16px;
        padding: 1.2rem;
        font-size: 1.1rem;
        backdrop-filter: blur(12px);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: inset 0 2px 10px rgba(0,0,0,0.3);
    }}
    
    .stTextArea>div>div>textarea:focus {{
        border-color: {header_color};
        box-shadow: 0 0 20px {glow_color}, inset 0 2px 10px rgba(0,0,0,0.3);
        background-color: rgba(15, 15, 20, 0.7);
        transform: translateY(-2px);
    }}
    
    /* Disclaimer */
    .disclaimer {{
        background-color: {disclaimer_bg};
        backdrop-filter: blur(5px);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #f59e0b;
        margin-top: 2rem;
        border-top: 1px solid rgba(255, 193, 7, 0.1);
        border-right: 1px solid rgba(255, 193, 7, 0.1);
        border-bottom: 1px solid rgba(255, 193, 7, 0.1);
    }}
    
    /* Sidebar Enhancements */
    [data-testid="stSidebar"] {{
        background: rgba(10, 10, 12, 0.8) !important;
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }}
    
    /* Animations */
    @keyframes fadeInDown {{
        from {{ opacity: 0; transform: translateY(-30px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    
    @keyframes fadeInUp {{
        from {{ opacity: 0; transform: translateY(30px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    
    /* Markdown Tables */
    table {{
        border-collapse: separate;
        border-spacing: 0;
        width: 100%;
        margin: 1.5rem 0;
        background-color: rgba(0, 0, 0, 0.3);
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }}
    
    table th {{
        background-color: rgba(99, 102, 241, 0.15);
        color: #e2e8f0;
        padding: 1rem;
        text-align: left;
        font-weight: 600;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }}
    
    table td {{
        padding: 1rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.03);
        color: #94a3b8;
    }}
    
    table tr:hover td {{
        background-color: rgba(255, 255, 255, 0.02);
        color: #e2e8f0;
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
        <div style="text-align: center; margin-bottom: 2.5rem; animation: fadeInUp 1s ease-out;">
            <p style="font-size: 1.15rem; color: #cbd5e1; margin-bottom: 1.5rem; letter-spacing: 0.5px;">
                Multi-Agent System for Comprehensive Health Analysis
            </p>
            <style>
                @keyframes float {{
                    0%, 100% {{ transform: translateY(0); }}
                    50% {{ transform: translateY(-5px); }}
                }}
                .badge-float-1 {{ animation: float 3s ease-in-out infinite; }}
                .badge-float-2 {{ animation: float 3.5s ease-in-out infinite; animation-delay: 0.2s; }}
                .badge-float-3 {{ animation: float 3.2s ease-in-out infinite; animation-delay: 0.4s; }}
            </style>
            <div style="display: flex; justify-content: center; gap: 1rem; flex-wrap: wrap;">
                <span class="badge-float-1" style="display: inline-block; background: rgba(99, 102, 241, 0.15); border: 1px solid rgba(99, 102, 241, 0.3); color: #818cf8; padding: 0.5rem 1.2rem; border-radius: 30px; font-size: 0.85rem; font-weight: 600; box-shadow: 0 0 15px rgba(99, 102, 241, 0.1); backdrop-filter: blur(5px);">
                    🤖 AI-Powered
                </span>
                <span class="badge-float-2" style="display: inline-block; background: rgba(34, 197, 94, 0.15); border: 1px solid rgba(34, 197, 94, 0.3); color: #4ade80; padding: 0.5rem 1.2rem; border-radius: 30px; font-size: 0.85rem; font-weight: 600; box-shadow: 0 0 15px rgba(34, 197, 94, 0.1); backdrop-filter: blur(5px);">
                    🔍 Real-Time Data
                </span>
                <span class="badge-float-3" style="display: inline-block; background: rgba(236, 72, 153, 0.15); border: 1px solid rgba(236, 72, 153, 0.3); color: #f472b6; padding: 0.5rem 1.2rem; border-radius: 30px; font-size: 0.85rem; font-weight: 600; box-shadow: 0 0 15px rgba(236, 72, 153, 0.1); backdrop-filter: blur(5px);">
                    ⚡ Fast Analysis
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_sidebar():
    """Render the sidebar with settings and information"""
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        
        # Initialize theme (default to dark)
        if "theme" not in st.session_state:
            st.session_state.theme = "dark"
        
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
    st.markdown("""
    <div style="animation: fadeInDown 0.8s ease-out; margin-bottom: 1rem;">
        <h2 style="
            background: linear-gradient(135deg, #818cf8, #c084fc, #f472b6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.2rem;
            font-weight: 800;
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            gap: 12px;
        ">
            ✨ Describe Your Symptoms
        </h2>
        <p style="color: #94a3b8; font-size: 1.1rem; margin-bottom: 0.5rem;">
            Provide as much detail as possible about how you're feeling for a highly accurate multi-agent analysis.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    user_input = st.text_area(
        "Enter your symptoms:",
        height=180,
        placeholder="e.g., I've been experiencing chronic headaches and fatigue for the past week. I also notice a slight fever at night...",
        label_visibility="collapsed"
    )
    
    # Helper text
    if not user_input:
        st.markdown("""
        <div style="animation: fadeInUp 1s ease-out; color: #64748b; font-size: 0.95rem; margin-top: 0.5rem; display: flex; align-items: center; gap: 8px; padding-left: 0.5rem;">
            <span style="font-size: 1.1rem;">💡</span>
            <i>Tip: Mention the duration, severity, and any triggers for your symptoms.</i>
        </div>
        """, unsafe_allow_html=True)
    
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


def _render_segmented_markdown(content: str) -> None:
    """Show each markdown table as a Streamlit dataframe; other blocks as markdown."""
    segments = segment_markdown_content(content)
    if not segments:
        st.markdown(content)
        return
    for seg in segments:
        if seg[0] == "table":
            _, headers, rows = seg
            if not headers:
                continue
            normalized = []
            for row in rows:
                padded = list(row) + [""] * max(0, len(headers) - len(row))
                normalized.append(padded[: len(headers)])
            st.dataframe(
                pd.DataFrame(normalized, columns=headers),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.markdown(seg[1])


def render_results(results, user_input=""):
    """Render the analysis results with section cards, tabular recommendations, and PDF download."""
    if not results:
        return

    st.markdown("---")

    # Section definitions: (key, label, emoji, accent-hex)
    sections = [
        ("symptom_analysis", "Symptom Analysis", "🧠", "#6366f1"),
        ("medication_advice", "Medication Advice", "💊", "#10b981"),
        ("home_remedies", "Home Remedies & Self-Care", "🌿", "#f59e0b"),
        ("diet_lifestyle", "Diet & Lifestyle", "🥗", "#3b82f6"),
        ("doctor_recommendations", "Doctor Recommendations", "👨‍⚕️", "#d946ef"),
    ]
    section_keys_labels = [(k, lbl) for k, lbl, _, _ in sections]

    # ── Title row + PDF download ──────────────────────────────────────────────
    title_col, btn_col = st.columns([3, 1])
    with title_col:
        st.markdown("## 📊 Complete Health Analysis")
    with btn_col:
        try:
            pdf_bytes = generate_pdf_report(results, user_input)
            if pdf_bytes is None:
                raise ValueError("PDF export returned no data")
            st.download_button(
                label="⬇️ Download PDF Report",
                data=pdf_bytes,
                file_name="healthcare_analysis_report.pdf",
                mime="application/pdf",
                use_container_width=True,
                help="Download the full health analysis as a PDF file",
            )
        except Exception as e:
            st.warning(f"PDF generation error: {e}")

    # Master table: every recommendation in one sortable table
    master_rows = build_master_recommendation_rows(results, section_keys_labels)
    if master_rows:
        st.markdown("### 📋 All recommendations (table view)")
        st.caption("One row per table entry, bullet, or note from every section below.")
        st.dataframe(
            pd.DataFrame(master_rows),
            use_container_width=True,
            hide_index=True,
        )

    for key, label, emoji, color in sections:
        content = results.get(key, "")
        if not content:
            continue

        st.markdown(
            f"""
        <div style="
            background: rgba(22,22,28,0.70);
            backdrop-filter: blur(14px);
            border-radius: 18px;
            border: 1px solid rgba(255,255,255,0.07);
            border-left: 5px solid {color};
            margin: 1.6rem 0 0.4rem 0;
            overflow: hidden;
        ">
            <div style="
                background: linear-gradient(90deg, {color}22, transparent);
                padding: 0.9rem 1.6rem;
                border-bottom: 1px solid rgba(255,255,255,0.05);
                display: flex;
                align-items: center;
                gap: 0.6rem;
            ">
                <span style="font-size:1.5rem;">{emoji}</span>
                <span style="
                    font-size: 1.25rem;
                    font-weight: 700;
                    color: {color};
                    letter-spacing: 0.3px;
                ">{label}</span>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        _render_segmented_markdown(str(content))

    # Error handling
    if results.get("error"):
        st.warning(f"⚠️ Some errors occurred: {results['error']}")


def render_footer():
    """Render the footer"""
    st.markdown("---")
    st.caption("© 202 AI Healthcare Assistant | Powered by LangGraph, Groq LLM, and Tavily API")

