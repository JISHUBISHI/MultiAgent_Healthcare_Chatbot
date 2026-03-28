"""
Modern Streamlit UI components for HealthBuddy.
"""

import pandas as pd
import streamlit as st

from table_format import build_master_recommendation_rows, segment_markdown_content


SECTION_META = [
    ("symptom_analysis", "Clinical Summary", "Core symptom interpretation and likely patterns.", "SC", "#0f766e"),
    ("medication_advice", "Medication Guidance", "High-level OTC and medication awareness guidance.", "RX", "#0f62fe"),
    ("home_remedies", "Home Care", "Rest, hydration, comfort, and practical at-home support.", "HC", "#b45309"),
    ("diet_lifestyle", "Lifestyle Support", "Food, sleep, movement, and recovery recommendations.", "LS", "#7c3aed"),
    ("doctor_recommendations", "Care Escalation", "When and where to seek professional medical support.", "MD", "#be123c"),
]


def apply_custom_css(theme="dark"):
    """Apply a refined healthcare dashboard theme."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');

        :root {
            --bg: #edf7f7;
            --surface: rgba(255, 255, 255, 0.18);
            --surface-strong: rgba(255, 255, 255, 0.28);
            --surface-soft: rgba(232, 245, 245, 0.18);
            --ink: #0d2230;
            --muted: #48606f;
            --line: rgba(13, 34, 48, 0.10);
            --teal: #0b7285;
            --teal-soft: rgba(11, 114, 133, 0.12);
            --blue: #1d4ed8;
            --blue-soft: rgba(29, 78, 216, 0.12);
            --gold: #a16207;
            --rose: #b91c1c;
            --shadow-lg: 0 26px 64px rgba(13, 34, 48, 0.10);
            --shadow-md: 0 16px 32px rgba(13, 34, 48, 0.08);
            --radius-xl: 28px;
            --radius-lg: 22px;
            --radius-md: 16px;
        }

        html, body, [class*="css"] {
            font-family: 'Manrope', sans-serif;
        }

        .stApp {
            color: var(--ink);
            background:
                radial-gradient(circle at top left, rgba(11, 114, 133, 0.18), transparent 32%),
                radial-gradient(circle at top right, rgba(34, 197, 94, 0.10), transparent 30%),
                linear-gradient(180deg, #eef8f8 0%, #f5fbfb 48%, #edf6fb 100%);
        }

        [data-testid="stAppViewContainer"] {
            background: transparent;
        }

        [data-testid="stHeader"] {
            background: rgba(255, 255, 255, 0.0);
        }

        [data-testid="stSidebar"] {
            background:
                linear-gradient(180deg, rgba(8, 36, 46, 0.84) 0%, rgba(15, 58, 74, 0.76) 100%) !important;
            border-right: 1px solid rgba(255, 255, 255, 0.14);
            backdrop-filter: blur(18px);
        }

        [data-testid="stSidebar"] * {
            color: #e5f1f1;
        }

        section[data-testid="stSidebar"] .stExpander {
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.14);
            border-radius: 16px;
        }

        .block-container {
            max-width: 1220px;
            padding-top: 2.2rem;
            padding-bottom: 2.5rem;
        }

        .html-shell {
            display: flex;
            flex-direction: column;
            gap: 1.15rem;
        }

        .html-grid {
            display: grid;
            grid-template-columns: minmax(0, 1fr);
            gap: 1.15rem;
        }

        .html-section {
            width: 100%;
        }

        @keyframes sectionFadeUp {
            0% {
                opacity: 0;
                transform: translateY(20px);
            }
            100% {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes glassPulse {
            0% {
                box-shadow: 0 26px 64px rgba(13, 34, 48, 0.08);
            }
            50% {
                box-shadow: 0 30px 76px rgba(11, 114, 133, 0.12);
            }
            100% {
                box-shadow: 0 26px 64px rgba(13, 34, 48, 0.08);
            }
        }

        @keyframes shimmerSweep {
            0% {
                transform: translateX(-120%);
            }
            100% {
                transform: translateX(120%);
            }
        }

        .hero-shell {
            position: relative;
            overflow: hidden;
            padding: 2.2rem 2.2rem 2rem 2.2rem;
            margin-bottom: 1.4rem;
            border-radius: var(--radius-xl);
            background:
                linear-gradient(135deg, rgba(255, 255, 255, 0.14) 0%, rgba(235, 248, 248, 0.10) 45%, rgba(232, 242, 250, 0.12) 100%);
            border: 1px solid rgba(255, 255, 255, 0.28);
            box-shadow: var(--shadow-lg);
            backdrop-filter: blur(22px);
            animation: sectionFadeUp 0.8s ease-out both, glassPulse 7s ease-in-out infinite;
        }

        .hero-shell::before {
            content: "";
            position: absolute;
            inset: auto -80px -120px auto;
            width: 280px;
            height: 280px;
            background: radial-gradient(circle, rgba(29, 78, 216, 0.14), transparent 66%);
        }

        .hero-shell::after {
            content: "";
            position: absolute;
            inset: -90px auto auto -80px;
            width: 240px;
            height: 240px;
            background: radial-gradient(circle, rgba(11, 114, 133, 0.14), transparent 68%);
        }

        .hero-shell > * {
            position: relative;
            z-index: 1;
        }

        .eyebrow {
            display: inline-flex;
            align-items: center;
            gap: 0.55rem;
            padding: 0.5rem 0.9rem;
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.16);
            color: var(--teal);
            font-size: 0.84rem;
            font-weight: 800;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .hero-title {
            max-width: 760px;
            margin: 1rem 0 0.75rem 0;
            font-size: clamp(2.4rem, 4vw, 4rem);
            line-height: 0.96;
            letter-spacing: -0.05em;
            font-weight: 800;
            color: #08212b;
        }

        .hero-copy {
            max-width: 700px;
            font-size: 1.02rem;
            line-height: 1.7;
            color: var(--muted);
            margin-bottom: 1.35rem;
        }

        .hero-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.9rem;
            margin-top: 1.25rem;
        }

        .hero-metric {
            background: rgba(255, 255, 255, 0.10);
            border: 1px solid rgba(255, 255, 255, 0.24);
            border-radius: 18px;
            padding: 1rem 1.05rem;
            backdrop-filter: blur(16px);
            transition: transform 0.25s ease, background 0.25s ease, border-color 0.25s ease;
        }

        .hero-metric:hover {
            transform: translateY(-4px);
            background: rgba(255, 255, 255, 0.16);
            border-color: rgba(255, 255, 255, 0.34);
        }

        .hero-metric-label {
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: #64748b;
            margin-bottom: 0.38rem;
        }

        .hero-metric-value {
            font-size: 1.15rem;
            font-weight: 800;
            color: #0f172a;
        }

        .panel {
            background: var(--surface);
            border: 1px solid rgba(255, 255, 255, 0.24);
            border-radius: var(--radius-lg);
            box-shadow: var(--shadow-md);
            padding: 1.5rem;
            backdrop-filter: blur(20px);
            animation: sectionFadeUp 0.9s ease-out both;
            position: relative;
            overflow: hidden;
        }

        .panel::after {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 35%;
            height: 100%;
            background: linear-gradient(90deg, rgba(255,255,255,0.14), rgba(255,255,255,0.04), transparent);
            animation: shimmerSweep 6.5s linear infinite;
            pointer-events: none;
        }

        .panel-title {
            font-size: 1.45rem;
            font-weight: 800;
            color: #0b1b2b;
            letter-spacing: -0.03em;
            margin-bottom: 0.35rem;
        }

        .panel-copy {
            color: var(--muted);
            line-height: 1.65;
            margin-bottom: 0;
        }

        .feature-strip {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.85rem;
            margin-top: 1.1rem;
        }

        .feature-pill {
            background: linear-gradient(180deg, rgba(255,255,255,0.10), rgba(248,250,252,0.06));
            border: 1px solid rgba(255, 255, 255, 0.24);
            border-radius: 18px;
            padding: 0.95rem 1rem;
            backdrop-filter: blur(16px);
            transition: transform 0.24s ease, background 0.24s ease, border-color 0.24s ease;
        }

        .feature-pill:hover {
            transform: translateY(-5px);
            background: linear-gradient(180deg, rgba(255,255,255,0.15), rgba(248,250,252,0.10));
            border-color: rgba(255, 255, 255, 0.34);
        }

        .feature-pill strong {
            display: block;
            font-size: 0.95rem;
            color: #0f172a;
            margin-bottom: 0.25rem;
        }

        .feature-pill span {
            color: #64748b;
            font-size: 0.9rem;
            line-height: 1.5;
        }

        .input-shell {
            background: linear-gradient(180deg, rgba(255,255,255,0.12), rgba(245,249,250,0.08));
            border: 1px solid rgba(255, 255, 255, 0.24);
            border-radius: var(--radius-lg);
            box-shadow: var(--shadow-md);
            padding: 1.5rem;
            margin: 0.4rem 0 1rem 0;
            backdrop-filter: blur(22px);
            animation: sectionFadeUp 1s ease-out both;
        }

        .input-widget-shell {
            padding: 0.15rem 0 0.25rem 0;
        }

        .input-widget-frame {
            background: linear-gradient(180deg, rgba(255,255,255,0.11), rgba(242,247,249,0.07));
            border: 1px solid rgba(255,255,255,0.22);
            border-radius: 22px;
            backdrop-filter: blur(20px);
            box-shadow: var(--shadow-md);
            padding: 1rem;
            animation: sectionFadeUp 1.05s ease-out both;
        }

        .action-shell {
            display: flex;
            justify-content: center;
            animation: sectionFadeUp 1.1s ease-out both;
        }

        .action-copy {
            margin-top: 0.7rem;
            text-align: center;
            color: #5f7380;
            font-size: 0.9rem;
        }

        .input-kicker {
            font-size: 0.8rem;
            font-weight: 800;
            letter-spacing: 0.09em;
            text-transform: uppercase;
            color: var(--teal);
            margin-bottom: 0.4rem;
        }

        .input-title {
            font-size: 1.8rem;
            line-height: 1.08;
            letter-spacing: -0.04em;
            color: #0b1b2b;
            font-weight: 800;
            margin-bottom: 0.45rem;
        }

        .input-copy {
            color: var(--muted);
            line-height: 1.65;
            margin-bottom: 1.1rem;
        }

        .prompt-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.8rem;
            margin-top: 1rem;
        }

        .prompt-card {
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.22);
            background: rgba(255, 255, 255, 0.08);
            padding: 0.9rem 1rem;
            backdrop-filter: blur(16px);
            transition: transform 0.22s ease, border-color 0.22s ease, background 0.22s ease;
        }

        .prompt-card:hover {
            transform: translateY(-4px);
            border-color: rgba(255, 255, 255, 0.30);
            background: rgba(255, 255, 255, 0.12);
        }

        .prompt-card strong {
            display: block;
            color: #0f172a;
            font-size: 0.92rem;
            margin-bottom: 0.18rem;
        }

        .prompt-card span {
            color: #64748b;
            font-size: 0.88rem;
            line-height: 1.5;
        }

        .stTextArea textarea {
            min-height: 230px;
            background: rgba(255, 255, 255, 0.18) !important;
            color: #0f172a !important;
            border-radius: 18px !important;
            border: 1px solid rgba(255, 255, 255, 0.34) !important;
            padding: 1rem 1.05rem !important;
            font-size: 1rem !important;
            line-height: 1.7 !important;
            box-shadow: inset 0 1px 2px rgba(13, 34, 48, 0.05) !important;
            backdrop-filter: blur(18px) !important;
        }

        .stTextArea textarea:focus {
            border-color: rgba(11, 114, 133, 0.50) !important;
            box-shadow: 0 0 0 4px rgba(11, 114, 133, 0.10) !important;
        }

        .stButton > button {
            min-height: 3.35rem;
            border: 1px solid rgba(255, 255, 255, 0.24);
            border-radius: 16px;
            background: linear-gradient(135deg, rgba(11, 114, 133, 0.92) 0%, rgba(29, 78, 216, 0.92) 100%);
            color: #ffffff;
            font-size: 1rem;
            font-weight: 800;
            letter-spacing: 0.01em;
            box-shadow: 0 18px 30px rgba(29, 78, 216, 0.18);
            transition: transform 0.18s ease, box-shadow 0.18s ease, filter 0.18s ease;
        }

        .stButton > button:hover {
            transform: translateY(-1px);
            filter: brightness(1.02);
            box-shadow: 0 20px 34px rgba(15, 98, 254, 0.26);
        }

        .results-head {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            margin: 0.2rem 0 1rem 0;
        }

        .results-shell {
            display: grid;
            grid-template-columns: minmax(0, 1fr) 260px;
            gap: 1rem;
            align-items: stretch;
            margin-bottom: 0.8rem;
        }

        .results-shell-card {
            background: linear-gradient(180deg, rgba(255,255,255,0.12), rgba(245,249,250,0.08));
            border: 1px solid rgba(255,255,255,0.24);
            border-radius: 24px;
            padding: 1.2rem 1.25rem;
            backdrop-filter: blur(20px);
            box-shadow: var(--shadow-md);
            animation: sectionFadeUp 0.9s ease-out both;
        }

        .results-shell-card.cta {
            display: flex;
            flex-direction: column;
            justify-content: center;
        }

        .results-title {
            font-size: 2rem;
            font-weight: 800;
            letter-spacing: -0.04em;
            color: #0b1b2b;
            margin: 0;
        }

        .results-copy {
            color: var(--muted);
            line-height: 1.6;
            margin: 0.35rem 0 0 0;
        }

        .summary-band {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 0.85rem;
            margin: 0.8rem 0 1.1rem 0;
        }

        .summary-tile {
            padding: 1rem 1.05rem;
            border-radius: 18px;
            border: 1px solid rgba(255, 255, 255, 0.24);
            background: rgba(255,255,255,0.10);
            box-shadow: 0 10px 24px rgba(13, 34, 48, 0.05);
            backdrop-filter: blur(16px);
            transition: transform 0.24s ease, background 0.24s ease, border-color 0.24s ease;
            animation: sectionFadeUp 0.8s ease-out both;
        }

        .summary-tile:hover {
            transform: translateY(-4px);
            background: rgba(255,255,255,0.16);
            border-color: rgba(255, 255, 255, 0.30);
        }

        .summary-tile strong {
            display: block;
            margin-bottom: 0.28rem;
            color: #0f172a;
            font-size: 1rem;
        }

        .summary-tile span {
            color: #64748b;
            font-size: 0.9rem;
            line-height: 1.55;
        }

        .section-card {
            background: linear-gradient(180deg, rgba(255,255,255,0.11), rgba(247,250,252,0.07));
            border: 1px solid rgba(255,255,255,0.24);
            border-radius: 24px;
            box-shadow: var(--shadow-md);
            overflow: hidden;
            margin: 1rem 0 1.15rem 0;
            backdrop-filter: blur(22px);
            position: relative;
            animation: sectionFadeUp 0.9s ease-out both;
            transition: transform 0.26s ease, border-color 0.26s ease, background 0.26s ease, box-shadow 0.26s ease;
        }

        .section-card::before {
            content: "";
            position: absolute;
            inset: 0;
            background: linear-gradient(120deg, rgba(255,255,255,0.12), transparent 40%, transparent 60%, rgba(255,255,255,0.10));
            opacity: 0.55;
            pointer-events: none;
        }

        .section-card:hover {
            transform: translateY(-6px);
            border-color: rgba(255,255,255,0.32);
            background: linear-gradient(180deg, rgba(255,255,255,0.15), rgba(247,250,252,0.09));
            box-shadow: 0 22px 50px rgba(13, 34, 48, 0.10);
        }

        .section-top {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            padding: 1.15rem 1.25rem;
            border-bottom: 1px solid rgba(15, 23, 42, 0.07);
            position: relative;
            z-index: 1;
        }

        .section-top-left {
            display: flex;
            align-items: center;
            gap: 0.9rem;
        }

        .section-badge {
            width: 44px;
            height: 44px;
            border-radius: 14px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 0.9rem;
            font-weight: 800;
            color: white;
        }

        .section-title {
            font-size: 1.18rem;
            font-weight: 800;
            color: #0f172a;
            margin-bottom: 0.15rem;
        }

        .section-subtitle {
            color: #64748b;
            font-size: 0.9rem;
            line-height: 1.45;
        }

        .section-rule {
            width: 84px;
            height: 10px;
            border-radius: 999px;
            opacity: 0.2;
        }

        .section-body {
            padding: 1.2rem 1.25rem 1.3rem 1.25rem;
            position: relative;
            z-index: 1;
        }

        .master-table-shell {
            background: rgba(255,255,255,0.10);
            border: 1px solid rgba(255,255,255,0.24);
            border-radius: 22px;
            box-shadow: var(--shadow-md);
            padding: 1.2rem;
            margin-bottom: 1rem;
            backdrop-filter: blur(18px);
            animation: sectionFadeUp 0.85s ease-out both;
        }

        .master-table-title {
            font-size: 1.12rem;
            font-weight: 800;
            color: #0f172a;
            margin-bottom: 0.2rem;
        }

        .master-table-copy {
            color: #64748b;
            margin-bottom: 0.85rem;
        }

        .notice {
            padding: 1rem 1.1rem;
            border-radius: 16px;
            background: rgba(185, 28, 28, 0.10);
            border: 1px solid rgba(185, 28, 28, 0.20);
            color: #881337;
            margin-top: 1rem;
            backdrop-filter: blur(16px);
        }

        div[data-testid="stDataFrame"] {
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.22);
            border-radius: 18px;
            backdrop-filter: blur(18px);
            padding: 0.25rem;
        }

        div[data-testid="stAlert"] {
            background: rgba(255, 255, 255, 0.16);
            border: 1px solid rgba(255, 255, 255, 0.30);
            backdrop-filter: blur(16px);
            border-radius: 16px;
        }

        .footer-shell {
            margin-top: 1.8rem;
            padding: 1rem 0 0.4rem 0;
            text-align: center;
            color: #64748b;
            font-size: 0.92rem;
        }

        .footer-shell strong {
            color: #0f172a;
        }

        @media (max-width: 980px) {
            .results-shell,
            .hero-grid,
            .feature-strip,
            .prompt-grid,
            .summary-band {
                grid-template-columns: 1fr;
            }

            .hero-shell {
                padding: 1.4rem;
            }

            .hero-title {
                font-size: 2.4rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header():
    """Render the hero header."""
    logo_col, text_col = st.columns([0.16, 0.84])
    with logo_col:
        st.image("healthbuddy-logo.jpeg", use_container_width=True)
    with text_col:
        st.markdown(
            """
            <div style="height: 100%; display:flex; align-items:center;">
                <div class="eyebrow">Official HealthBuddy Identity</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <div class="html-shell">
            <section class="hero-shell html-section">
                <div class="eyebrow">HealthBuddy Medical Assistant</div>
                <h1 class="hero-title">HealthBuddy delivers calm, clinical-looking AI guidance for everyday health questions.</h1>
                <p class="hero-copy">
                    Share symptoms in plain language and receive a transparent, well-structured medical-style care brief
                    across symptom analysis, medication awareness, home support, lifestyle guidance, and escalation advice.
                </p>
                <div class="hero-grid">
                    <div class="hero-metric">
                        <div class="hero-metric-label">Clinical workflow</div>
                        <div class="hero-metric-value">Multi-agent triage-inspired reasoning</div>
                    </div>
                    <div class="hero-metric">
                        <div class="hero-metric-label">Interface style</div>
                        <div class="hero-metric-value">Transparent medical dashboard</div>
                    </div>
                    <div class="hero-metric">
                        <div class="hero-metric-label">Designed for</div>
                        <div class="hero-metric-value">A modern digital clinic feel</div>
                    </div>
                </div>
            </section>
            <section class="panel html-section">
                <div class="panel-title">Medical-style guidance, organized clearly</div>
                <p class="panel-copy">
                    HealthBuddy is styled to feel closer to a healthcare platform with transparent panels,
                    restrained colors, cleaner sectioning, and a more clinical visual language.
                </p>
                <div class="feature-strip">
                    <div class="feature-pill">
                        <strong>Symptom overview</strong>
                        <span>Symptoms are summarized into a concise assessment-style overview.</span>
                    </div>
                    <div class="feature-pill">
                        <strong>Care tracks</strong>
                        <span>Guidance is separated into medication, home care, and lifestyle support.</span>
                    </div>
                    <div class="feature-pill">
                        <strong>Escalation clarity</strong>
                        <span>Doctor recommendations stay prominent when professional follow-up matters.</span>
                    </div>
                </div>
            </section>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar():
    """Render the sidebar with refined product copy."""
    with st.sidebar:
        st.markdown("## HealthBuddy")
        st.caption("A transparent, medical-style healthcare analysis workspace.")

        with st.expander("How the workflow runs", expanded=True):
            st.markdown(
                """
                1. Describe the symptoms in your own words.
                2. The agent workflow reviews likely patterns.
                3. Guidance is grouped into medication, home care, lifestyle, and escalation.
                4. Review the results directly in the app.
                """
            )

        with st.expander("Best input quality", expanded=False):
            st.markdown(
                """
                Include:
                - How long symptoms have been happening
                - Pain level or severity
                - Fever, fatigue, or sleep impact
                - Triggers, food changes, or medication use
                """
            )

        with st.expander("Important note", expanded=False):
            st.markdown(
                """
                This tool provides AI-assisted guidance, not a medical diagnosis.
                Seek urgent care immediately for severe breathing trouble, chest pain,
                stroke-like symptoms, or any rapidly worsening condition.
                """
            )

        st.markdown("---")
        st.markdown("### Platform highlights")
        st.markdown(
            """
            - Structured care summary
            - In-app care review
            - Real-time research support
            - Multi-agent recommendation flow
            """
        )

        if "results" in st.session_state and st.session_state.results:
            completed = sum(
                1
                for key, _, _, _, _ in SECTION_META
                if st.session_state.results.get(key)
            )
            st.markdown("---")
            st.markdown("### Analysis progress")
            st.progress(completed / len(SECTION_META))
            st.caption(f"{completed}/{len(SECTION_META)} sections generated")

        st.markdown("---")
        st.caption("HealthBuddy is styled to feel closer to a modern digital health product.")


def render_input_section():
    """Render the premium symptom input panel."""
    st.markdown(
        """
        <div class="html-grid">
            <section class="input-shell html-section">
                <div class="input-kicker">Symptom intake</div>
                <div class="input-title">Describe what you are feeling</div>
                <p class="input-copy">
                    Write naturally. HealthBuddy will turn your symptom description into a cleaner, more
                    medical-style recommendation flow.
                </p>
                <div class="prompt-grid">
                    <div class="prompt-card">
                        <strong>Timeline</strong>
                        <span>When did it start, and is it getting better, worse, or staying the same?</span>
                    </div>
                    <div class="prompt-card">
                        <strong>Intensity</strong>
                        <span>Include severity, pain level, discomfort, or how it affects daily activity.</span>
                    </div>
                    <div class="prompt-card">
                        <strong>Context</strong>
                        <span>Mention fever, nausea, cough, stress, food changes, or medicines already taken.</span>
                    </div>
                </div>
            </section>
            <section class="input-widget-shell html-section">
                <div class="input-widget-frame">
        """,
        unsafe_allow_html=True,
    )

    user_input = st.text_area(
        "Enter your symptoms",
        height=230,
        placeholder=(
            "Example: I have had a sore throat, dry cough, body ache, and mild fever for three days. "
            "The fever is worse at night and I feel tired after walking for a few minutes."
        ),
        label_visibility="collapsed",
    )

    st.markdown(
        """
                </div>
            </section>
        </div>
        """,
        unsafe_allow_html=True,
    )

    return user_input


def render_analyze_button():
    """Render the primary call-to-action."""
    st.markdown(
        """
        <section class="action-shell html-section">
            <div style="width:min(420px, 100%);">
        """,
        unsafe_allow_html=True,
    )
    clicked = st.button(
        "Generate Care Analysis",
        type="primary",
        use_container_width=True,
        help="Run the multi-agent healthcare analysis",
    )
    st.markdown(
        """
                <div class="action-copy">Structured HTML/CSS interface with Streamlit handling the interaction layer.</div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )
    return clicked


def _render_segmented_markdown(content: str) -> None:
    """Show markdown tables as dataframes and other content as markdown."""
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


def _render_results_summary(user_input: str, completed_count: int) -> None:
    """Render summary tiles above the results."""
    preview = (user_input or "").strip()
    if len(preview) > 110:
        preview = preview[:107] + "..."
    preview = preview or "No symptom text captured."

    st.markdown(
        f"""
        <div class="summary-band">
            <div class="summary-tile">
                <strong>Sections completed</strong>
                <span>{completed_count} of {len(SECTION_META)} recommendation streams are available.</span>
            </div>
            <div class="summary-tile">
                <strong>Review format</strong>
                <span>Designed for clean on-screen reading in structured clinical sections.</span>
            </div>
            <div class="summary-tile">
                <strong>Input snapshot</strong>
                <span>{preview}</span>
            </div>
            <div class="summary-tile">
                <strong>Safety reminder</strong>
                <span>Use this as support guidance and escalate urgent symptoms promptly.</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_results(results, user_input=""):
    """Render results in a polished dashboard layout."""
    if not results:
        return

    st.markdown("<div style='height: 0.6rem;'></div>", unsafe_allow_html=True)

    completed_count = sum(1 for key, _, _, _, _ in SECTION_META if results.get(key))

    st.markdown(
        """
        <div class="results-shell">
            <section class="results-shell-card">
                <div class="results-head">
                    <div>
                        <h2 class="results-title">HealthBuddy Care Analysis</h2>
                        <p class="results-copy">
                            Review each recommendation stream below in a more clinical, transparent dashboard layout.
                        </p>
                    </div>
                </div>
            </section>
            <section class="results-shell-card cta">
                <div class="results-copy">
                    Your full HealthBuddy guidance is organized below for direct in-app review.
                </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
            </section>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _render_results_summary(user_input, completed_count)

    master_rows = build_master_recommendation_rows(
        results,
        [(key, label) for key, label, _, _, _ in SECTION_META],
    )
    if master_rows:
        st.markdown(
            """
            <section class="master-table-shell">
                <div class="master-table-title">Unified recommendation table</div>
                <div class="master-table-copy">
                    All extracted recommendations are also available in one structured clinical-style table view.
                </div>
            </section>
            """,
            unsafe_allow_html=True,
        )
        st.dataframe(pd.DataFrame(master_rows), use_container_width=True, hide_index=True)

    for key, title, subtitle, badge, accent in SECTION_META:
        content = results.get(key, "")
        if not content:
            continue

        st.markdown(
            f"""
            <section class="section-card">
                <div class="section-top">
                    <div class="section-top-left">
                        <div class="section-badge" style="background:{accent};">{badge}</div>
                        <div>
                            <div class="section-title">{title}</div>
                            <div class="section-subtitle">{subtitle}</div>
                        </div>
                    </div>
                    <div class="section-rule" style="background:{accent};"></div>
                </div>
                <div class="section-body">
            """,
            unsafe_allow_html=True,
        )
        _render_segmented_markdown(str(content))
        st.markdown("</div></section>", unsafe_allow_html=True)

    if results.get("error"):
        st.markdown(
            f"<div class='notice'><strong>Processing note:</strong> {results['error']}</div>",
            unsafe_allow_html=True,
        )


def render_footer():
    """Render the refined footer."""
    st.markdown(
        """
        <div class="footer-shell">
            <strong>HealthBuddy</strong><br/>
            Transparent medical-style care guidance interface built with Streamlit, LangGraph, Groq, and Tavily.
        </div>
        """,
        unsafe_allow_html=True,
    )
