# ==============================================================================
# CYBERBULLYING DETECTION SYSTEM
# MODULE: app.py (Main Streamlit Frontend Application)
#
# DESCRIPTION:
# Premium AI SaaS dashboard UI for the Cyberbullying Detection System.
# Connects to the CyberGuard AI FastAPI backend over HTTP via api_client.py -
# it no longer imports model.py or utils.py directly. Provides:
# - A modern project dashboard with live stats (from the backend database)
# - Real-time AI detection with confidence gauges & category chips
# - A social simulator showing real-time content filtering & chat moderation
# - An analytics console with interactive Plotly charts
# - A cyber safety education and legal resource portal
#
# Set BACKEND_URL to point this frontend at your FastAPI backend, e.g.:
#   BACKEND_URL=http://localhost:8000    (local dev)
#   BACKEND_URL=https://your-backend-domain.com   (production)
# ==============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import os
import time
import plotly.graph_objects as go
import plotly.express as px
import api_client
from api_client import ApiError

# --- STEP 1: CONFIGURE PAGE SETTINGS ---
st.set_page_config(
    page_title="CyberGuard AI - Cyberbullying Detection System",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- STEP 2: GLOBAL PREMIUM SAAS STYLING ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root {
        --bg-1: #0F172A;
        --bg-2: #111827;
        --bg-3: #1E293B;
        --primary: #2563EB;
        --secondary: #7C3AED;
        --success: #22C55E;
        --danger: #EF4444;
        --text: #F8FAFC;
        --text-secondary: #CBD5E1;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
    }

    .stApp {
        background: linear-gradient(160deg, #0F172A 0%, #111827 45%, #1E293B 100%) !important;
        color: var(--text) !important;
    }

    p, li, span, label, .stText, .stMarkdown, ol, ul, select, input, textarea {
        font-family: 'Inter', sans-serif !important;
        color: var(--text-secondary) !important;
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', sans-serif !important;
        color: var(--text) !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
    }

    strong, b { color: var(--text) !important; font-weight: 600 !important; }

    code, pre {
        font-family: 'SFMono-Regular', Consolas, monospace !important;
        background-color: rgba(255,255,255,0.06) !important;
        color: #93C5FD !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 6px !important;
    }

    /* ---------- GLASS CARDS ---------- */
    .glass-card {
        background: rgba(255, 255, 255, 0.045);
        border: 1px solid rgba(255, 255, 255, 0.09);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-radius: 20px;
        padding: 1.6rem 1.7rem;
        box-shadow: 0 8px 30px rgba(0,0,0,0.25);
        margin-bottom: 1.4rem;
        transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
    }
    .glass-card:hover {
        transform: translateY(-3px);
        border-color: rgba(124, 92, 237, 0.35);
        box-shadow: 0 14px 40px rgba(37, 99, 235, 0.18);
    }

    .card-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: var(--text) !important;
        margin-bottom: 0.8rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        border-bottom: 1px solid rgba(255,255,255,0.08);
        padding-bottom: 0.6rem;
    }

    .glass-card p, .glass-card span, .glass-card li, .glass-card ol, .glass-card ul, .glass-card div {
        color: var(--text-secondary) !important;
        line-height: 1.65;
    }

    /* ---------- HERO ---------- */
    .hero-wrap {
        padding: 2.6rem 2.2rem;
        border-radius: 24px;
        background: radial-gradient(circle at 20% 20%, rgba(37,99,235,0.20), transparent 55%),
                    radial-gradient(circle at 85% 75%, rgba(124,58,237,0.22), transparent 55%),
                    rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        margin-bottom: 1.8rem;
    }
    .hero-eyebrow {
        display: inline-block;
        padding: 4px 14px;
        border-radius: 999px;
        background: rgba(37,99,235,0.15);
        border: 1px solid rgba(37,99,235,0.4);
        color: #93C5FD !important;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.03em;
        margin-bottom: 1rem;
    }
    .hero-title {
        font-size: 2.6rem;
        font-weight: 800;
        line-height: 1.12;
        background: linear-gradient(90deg, #F8FAFC 20%, #93C5FD 60%, #C4B5FD 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .hero-subtitle {
        font-size: 1.15rem;
        font-weight: 600;
        color: #93C5FD !important;
        margin-bottom: 0.9rem;
    }
    .hero-desc {
        font-size: 1rem;
        color: var(--text-secondary) !important;
        max-width: 520px;
        line-height: 1.6;
        margin-bottom: 1.6rem;
    }
    .hero-illustration {
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 9rem;
        filter: drop-shadow(0 0 40px rgba(37, 99, 235, 0.45));
    }

    /* ---------- STAT CARDS ---------- */
    .stat-card {
        background: rgba(255,255,255,0.045);
        border: 1px solid rgba(255,255,255,0.09);
        border-radius: 20px;
        padding: 1.4rem 1.3rem;
        backdrop-filter: blur(16px);
        transition: transform 0.2s ease, border-color 0.2s ease;
        height: 100%;
    }
    .stat-card:hover {
        transform: translateY(-4px);
        border-color: rgba(124, 92, 237, 0.4);
    }
    .stat-icon { font-size: 1.6rem; margin-bottom: 0.4rem; }
    .stat-number {
        font-size: 2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #2563EB, #7C3AED);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.15rem;
    }
    .stat-label {
        font-size: 0.85rem;
        color: var(--text-secondary) !important;
        font-weight: 500;
    }

    /* ---------- FEATURE CARDS ---------- */
    .feature-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 20px;
        padding: 1.5rem;
        height: 100%;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .feature-card:hover {
        transform: translateY(-4px);
        border-color: rgba(37, 99, 235, 0.4);
    }
    .feature-icon { font-size: 1.8rem; margin-bottom: 0.5rem; }
    .feature-title { font-weight: 700; color: var(--text) !important; margin-bottom: 0.4rem; font-size: 1.02rem; }
    .feature-desc { font-size: 0.88rem; color: var(--text-secondary) !important; line-height: 1.55; }

    /* ---------- BADGES / CHIPS ---------- */
    .badge {
        display: inline-block;
        padding: 5px 14px;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.02em;
    }
    .badge-danger { background: rgba(239,68,68,0.15); border: 1px solid rgba(239,68,68,0.45); color: #FCA5A5 !important; }
    .badge-safe { background: rgba(34,197,94,0.15); border: 1px solid rgba(34,197,94,0.45); color: #86EFAC !important; }
    .chip {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 0.76rem;
        font-weight: 600;
        background: rgba(124,58,237,0.15);
        border: 1px solid rgba(124,58,237,0.4);
        color: #C4B5FD !important;
        margin-right: 6px;
        margin-bottom: 6px;
    }

    /* ---------- BANNERS ---------- */
    .banner-safe {
        background: rgba(34, 197, 94, 0.10);
        border: 1px solid rgba(34, 197, 94, 0.4);
        color: #86EFAC !important;
        padding: 1rem 1.2rem;
        border-radius: 14px;
        font-weight: 500;
    }
    .banner-safe strong, .banner-safe span, .banner-safe b { color: #86EFAC !important; }

    .banner-danger {
        background: rgba(239, 68, 68, 0.10);
        border: 1px solid rgba(239, 68, 68, 0.4);
        color: #FCA5A5 !important;
        padding: 1rem 1.2rem;
        border-radius: 14px;
        font-weight: 500;
    }
    .banner-danger strong, .banner-danger span, .banner-danger b { color: #FCA5A5 !important; }

    /* ---------- CHAT BUBBLES ---------- */
    .chat-row { display: flex; align-items: flex-end; gap: 0.6rem; margin-bottom: 0.9rem; }
    .chat-row.mine { flex-direction: row-reverse; }
    .chat-avatar {
        width: 34px; height: 34px; border-radius: 50%;
        background: linear-gradient(135deg, #2563EB, #7C3AED);
        display: flex; align-items: center; justify-content: center;
        font-size: 0.85rem; font-weight: 700; color: white !important;
        flex-shrink: 0;
    }
    .chat-bubble {
        max-width: 70%;
        padding: 0.65rem 1rem;
        border-radius: 16px;
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.08);
        color: var(--text-secondary) !important;
        font-size: 0.92rem;
        line-height: 1.5;
    }
    .chat-row.mine .chat-bubble {
        background: linear-gradient(135deg, rgba(37,99,235,0.35), rgba(124,58,237,0.35));
        color: var(--text) !important;
        border: 1px solid rgba(124,58,237,0.4);
    }
    .chat-bubble.blurred { filter: blur(5px); user-select: none; }
    .chat-meta { font-size: 0.7rem; color: #64748B !important; margin-top: 2px; }
    .mod-badge {
        font-size: 0.68rem; font-weight: 700; padding: 2px 9px; border-radius: 999px; margin-left: 6px;
    }
    .mod-approved { background: rgba(34,197,94,0.15); color: #86EFAC !important; border: 1px solid rgba(34,197,94,0.4); }
    .mod-blocked { background: rgba(239,68,68,0.15); color: #FCA5A5 !important; border: 1px solid rgba(239,68,68,0.4); }

    /* ---------- SIDEBAR ---------- */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0B1220 0%, #0F172A 100%) !important;
        border-right: 1px solid rgba(255,255,255,0.06) !important;
    }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] li, [data-testid="stSidebar"] strong {
        color: var(--text-secondary) !important;
    }
    .sidebar-logo {
        text-align: center;
        font-size: 1.3rem;
        font-weight: 800;
        color: var(--text) !important;
        padding: 0.6rem 0 0.2rem 0;
    }
    .sidebar-sub {
        text-align: center;
        font-size: 0.75rem;
        color: #64748B !important;
        margin-bottom: 0.8rem;
    }

    /* ---------- BUTTONS ---------- */
    .stButton>button {
        background: linear-gradient(135deg, #2563EB, #7C3AED) !important;
        border: none !important;
        color: white !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        border-radius: 12px !important;
        padding: 0.55rem 1.3rem !important;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.25) !important;
        transition: transform 0.18s ease, box-shadow 0.18s ease !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 22px rgba(124, 58, 237, 0.35) !important;
    }
    .stButton>button:active { transform: translateY(0px); }

    /* Secondary-style button variant via data attribute set through markdown key */
    div[data-testid="stFormSubmitButton"] button {
        background: linear-gradient(135deg, #2563EB, #7C3AED) !important;
        border: none !important;
        border-radius: 12px !important;
        color: white !important;
        font-weight: 600 !important;
    }

    /* Inputs */
    .stTextInput input, .stTextArea textarea, .stNumberInput input {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        border-radius: 14px !important;
        color: var(--text) !important;
        font-family: 'Inter', sans-serif !important;
    }
    .stTextArea textarea { border-radius: 16px !important; }

    [data-testid="stMetricValue"] { color: var(--text) !important; font-weight: 700 !important; }
    [data-testid="stMetricLabel"] { color: var(--text-secondary) !important; }

    hr { border-color: rgba(255,255,255,0.08) !important; }

    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-thumb { background: rgba(124,58,237,0.4); border-radius: 8px; }
</style>
""", unsafe_allow_html=True)


# --- STEP 3: SESSION STATE INITIALIZATION (unchanged keys + additive UI stat counters) ---
if 'model_trained' not in st.session_state:
    try:
        status = api_client.get_model_status()
        st.session_state.model_trained = bool(status.get("model_loaded"))
    except ApiError:
        # Backend unreachable - default to fallback mode until it's back
        st.session_state.model_trained = False

if 'admin_token' not in st.session_state:
    st.session_state.admin_token = None

if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = [
        {"user": "Alice", "msg": "Hey everyone! Did you finish the AI project assignment?", "censored": False, "type": "Neutral"},
        {"user": "Bob", "msg": "Yes! I spent the weekend writing code for TF-IDF. It's actually very cool.", "censored": False, "type": "Neutral"}
    ]

if 'user_warnings' not in st.session_state:
    st.session_state.user_warnings = 0

if 'blocked_simulated_posts' not in st.session_state:
    st.session_state.blocked_simulated_posts = {}

if 'detector_chatbot_messages' not in st.session_state:
    st.session_state.detector_chatbot_messages = [
        {"role": "assistant", "content": "👋 Hello! I am your CyberGuard AI Safety Bot. Type any message below, and I will scan it for cyberbullying in real time!"}
    ]

if 'last_scanned_result' not in st.session_state:
    st.session_state.last_scanned_result = None

# Additive, display-only counters that power the new stat cards. These do not
# touch any prediction/training logic — they simply count outcomes already
# produced by predict_message() so the dashboard has live numbers to show.
if 'stats_total_scanned' not in st.session_state:
    st.session_state.stats_total_scanned = 0
if 'stats_safe_count' not in st.session_state:
    st.session_state.stats_safe_count = 0
if 'stats_bullying_count' not in st.session_state:
    st.session_state.stats_bullying_count = 0
if 'detector_input_key' not in st.session_state:
    st.session_state.detector_input_key = 0


def log_scan_stats(label):
    """Increments the display-only stat counters used by the dashboard cards."""
    st.session_state.stats_total_scanned += 1
    if label == 1:
        st.session_state.stats_bullying_count += 1
    else:
        st.session_state.stats_safe_count += 1


def render_gauge(confidence_pct, is_bullying):
    color = "#EF4444" if is_bullying else "#22C55E"
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=confidence_pct,
        number={'suffix': "%", 'font': {'color': '#F8FAFC', 'size': 34}},
        gauge={
            'axis': {'range': [0, 100], 'tickcolor': '#64748B', 'tickfont': {'color': '#64748B'}},
            'bar': {'color': color},
            'bgcolor': "rgba(255,255,255,0.04)",
            'borderwidth': 0,
            'steps': [
                {'range': [0, 100], 'color': 'rgba(255,255,255,0.05)'}
            ],
        }
    ))
    fig.update_layout(
        height=220,
        margin=dict(l=20, r=20, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        font={'color': "#F8FAFC", 'family': "Inter"}
    )
    return fig


def render_probability_bar(confidence, is_bullying):
    safe_prob = (1 - confidence) if is_bullying else confidence
    bullying_prob = confidence if is_bullying else (1 - confidence)
    fig = go.Figure(go.Bar(
        x=[safe_prob * 100, bullying_prob * 100],
        y=["Safe", "Cyberbullying"],
        orientation='h',
        marker=dict(color=["#22C55E", "#EF4444"]),
        text=[f"{safe_prob*100:.1f}%", f"{bullying_prob*100:.1f}%"],
        textposition="outside",
        textfont=dict(color="#F8FAFC")
    ))
    fig.update_layout(
        height=200,
        margin=dict(l=10, r=30, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(range=[0, 105], showgrid=False, color="#94A3B8"),
        yaxis=dict(color="#F8FAFC"),
        font={'color': "#F8FAFC", 'family': "Inter"}
    )
    return fig


# --- STEP 4: SIDEBAR & ROUTING ---
with st.sidebar:
    st.markdown("<div class='sidebar-logo'>🛡 CyberGuard AI</div>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-sub'>AI-Powered Safety Platform</div>", unsafe_allow_html=True)
    st.markdown("---")

    page = st.radio(
        "Navigation",
        [
            "🏠 Dashboard",
            "🔍 AI Detector",
            "💬 Chat Simulator",
            "📊 Analytics",
            "📚 Safety Guide",
            "ℹ️ About",
            "⚙️ Settings"
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("<p style='font-size:0.78rem; color:#64748B;'>Model Status</p>", unsafe_allow_html=True)
    if st.session_state.model_trained:
        st.markdown("<span class='badge badge-safe'>● Model Active</span>", unsafe_allow_html=True)
    else:
        st.markdown("<span class='badge badge-danger'>● Lexicon Fallback</span>", unsafe_allow_html=True)

# --- STEP 5: RENDER PAGE CONTENTS ---

# ==========================================
# PAGE 1: DASHBOARD (HOME)
# ==========================================
if page == "🏠 Dashboard":
    col_hero_l, col_hero_r = st.columns([7, 5])
    with col_hero_l:
        st.markdown("""
        <div class="hero-wrap">
            <span class="hero-eyebrow">🛡 AI-Powered Detection Engine</span>
            <div class="hero-title">CyberGuard AI</div>
            <div class="hero-subtitle">AI Powered Cyberbullying Detection</div>
            <div class="hero-desc">Detect harmful online messages using Machine Learning and Natural Language Processing — in real time, with explainable results and built-in safety guidance.</div>
        </div>
        """, unsafe_allow_html=True)
        btn_col1, btn_col2, _ = st.columns([2, 2, 3])
        with btn_col1:
            start_clicked = st.button("🚀 Start Detection", use_container_width=True)
        with btn_col2:
            learn_clicked = st.button("📖 Learn More", use_container_width=True)
        if start_clicked:
            st.info("Head to the **🔍 AI Detector** page from the sidebar to scan a message.")
        if learn_clicked:
            st.info("Head to the **📚 Safety Guide** page from the sidebar to learn more.")

    with col_hero_r:
        st.markdown("<div class='hero-illustration'>🛡️✨</div>", unsafe_allow_html=True)

    # --- STAT CARDS (now backed by the database via the backend, not session state) ---
    try:
        dashboard_stats = api_client.get_dashboard_stats()
        accuracy_display = (
            f"{dashboard_stats['model_accuracy'] * 100:.1f}%"
            if dashboard_stats.get('model_accuracy') is not None else "—"
        )
        messages_scanned = dashboard_stats.get('messages_scanned', 0)
        safe_messages = dashboard_stats.get('safe_messages', 0)
        bullying_detected = dashboard_stats.get('cyberbullying_detected', 0)
    except ApiError as e:
        st.warning(f"Could not load live stats from the backend: {e.message}")
        accuracy_display, messages_scanned, safe_messages, bullying_detected = "—", 0, 0, 0

    stat_cols = st.columns(4)
    stats = [
        ("🎯", accuracy_display, "Model Accuracy"),
        ("📨", str(messages_scanned), "Messages Scanned"),
        ("✅", str(safe_messages), "Safe Messages"),
        ("🚨", str(bullying_detected), "Cyberbullying Detected"),
    ]
    for col, (icon, number, label) in zip(stat_cols, stats):
        with col:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-icon">{icon}</div>
                <div class="stat-number">{number}</div>
                <div class="stat-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- FEATURE CARDS ---
    feat_cols = st.columns(3)
    features = [
        ("🎯", "Objective", "Automatically detect and flag cyberbullying in text using an NLP pipeline, protecting students and users from online harassment in real time."),
        ("⚙️", "Technology", "Built with TF-IDF vectorization and a Logistic Regression classifier, trained on a labeled dataset of safe and toxic messages."),
        ("🌍", "Applications", "Applicable to social media moderation, classroom chat platforms, online forums, and any space where user-generated text needs protection."),
    ]
    for col, (icon, title, desc) in zip(feat_cols, features):
        with col:
            st.markdown(f"""
            <div class="feature-card">
                <div class="feature-icon">{icon}</div>
                <div class="feature-title">{title}</div>
                <div class="feature-desc">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns([7, 5])
    with col1:
        st.markdown("""
        <div class="glass-card">
            <div class="card-title">📊 Cyberbullying Incidence by Platform</div>
            <p style="font-size: 0.9rem;">Key findings from child safety research indicating why this AI system is critical today.</p>
        </div>
        """, unsafe_allow_html=True)

        stats_df = pd.DataFrame({
            'Platform': ['Instagram', 'Snapchat', 'WhatsApp', 'YouTube', 'Facebook', 'Twitter/X'],
            'Teenagers Harassed (%)': [42, 37, 33, 28, 22, 19]
        })
        fig = px.bar(
            stats_df, x='Teenagers Harassed (%)', y='Platform', orientation='h',
            color='Teenagers Harassed (%)', color_continuous_scale=['#7C3AED', '#2563EB']
        )
        fig.update_layout(
            height=320,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font={'color': "#F8FAFC", 'family': "Inter"},
            coloraxis_showscale=False,
            margin=dict(l=10, r=20, t=20, b=20),
            yaxis=dict(autorange="reversed")
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("""
        <div class="glass-card">
            <div class="card-title">⚙️ How It Works</div>
            <ol style="font-size: 0.9rem; padding-left: 1.1rem;">
                <li><b>Data Acquisition:</b> A labeled dataset (<code>dataset.csv</code>) teaches the model safe vs. toxic phrases.</li>
                <li><b>Text Cleaning:</b> Input text is standardized — lowercased and stripped of special characters.</li>
                <li><b>TF-IDF Processing:</b> Extracts numerical weight matrices representing vocabulary significance.</li>
                <li><b>Classifier Training:</b> Learns coefficients and saves a binary model file via Pickle.</li>
                <li><b>Inference:</b> Live messages are vectorized and scored in real time.</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.model_trained:
            st.markdown("<div class='banner-safe'>✅ AI model file detected and active (<code>cyberbullying_model.pkl</code>)</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='banner-danger'>⚠️ AI model not trained yet. Visit <b>📊 Analytics</b> to train it — the app is currently running on lexicon fallback rules.</div>", unsafe_allow_html=True)

# ==========================================
# PAGE 2: AI DETECTOR
# ==========================================
elif page == "🔍 AI Detector":
    st.markdown("## 🔍 AI Detector")
    st.markdown("<p>Analyze any message in real time and get an explainable safety verdict.</p>", unsafe_allow_html=True)

    if not st.session_state.model_trained:
        st.markdown("<div class='banner-danger'>⚠️ The AI model has not been trained yet. Operating in <b>Lexicon Fallback Mode</b>. Train the real ML model on the <b>📊 Analytics</b> page.</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([7, 5])

    with col1:
        st.markdown("<div class='glass-card'><div class='card-title'>💬 Analyze a Message</div>", unsafe_allow_html=True)

        text_input = st.text_area(
            "Message",
            key=f"detector_textarea_{st.session_state.detector_input_key}",
            placeholder="Type or paste a message to scan for cyberbullying...",
            height=130,
            label_visibility="collapsed"
        )
        st.markdown(f"<p style='font-size:0.78rem; text-align:right; color:#64748B;'>{len(text_input)} characters</p>", unsafe_allow_html=True)

        act_col1, act_col2 = st.columns([1, 1])
        with act_col1:
            analyze_clicked = st.button("🔎 Analyze", use_container_width=True)
        with act_col2:
            clear_clicked = st.button("🗑️ Clear", use_container_width=True)

        if clear_clicked:
            st.session_state.detector_input_key += 1
            st.rerun()

        if analyze_clicked and text_input.strip():
            with st.spinner("Scanning message with CyberGuard AI..."):
                start_t = time.time()
                try:
                    result = api_client.predict_message(text_input)
                    api_error = None
                except ApiError as e:
                    result, api_error = None, e
                elapsed_ms = (time.time() - start_t) * 1000

            if api_error:
                st.error(f"❌ Backend error: {api_error.message}")
            else:
                log_scan_stats(result['label'])

                st.session_state.last_scanned_result = {
                    "text": text_input,
                    "label": result['label'],
                    "confidence": result['confidence'],
                    "method": result['method'],
                    "matched_words": result['matched_words'],
                    "category": result['category'],
                    "severity": result['severity'],
                    "elapsed_ms": elapsed_ms
                }

                # Keep the chatbot-style history in sync (used by voice input too)
                st.session_state.detector_chatbot_messages.append({"role": "user", "content": text_input})
                if result['label'] == 1:
                    bot_reply = "🚨 This message was flagged as potential cyberbullying. Stay calm, don't reply, take a screenshot, and talk to a trusted adult."
                else:
                    bot_reply = "🟢 This message looks safe and friendly. Thanks for helping keep online spaces positive!"
                st.session_state.detector_chatbot_messages.append({"role": "assistant", "content": bot_reply})

        st.markdown("</div>", unsafe_allow_html=True)

        # --- Voice recorder card (feature preserved) ---
        st.markdown("<div class='glass-card'><div class='card-title'>🎙️ Voice Input Scanner</div>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:0.85rem;'>Click record, speak into your mic, and click stop to scan voice messages.</p>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 0.78rem; color: #FBBF24;'>⚠️ Browsers require a secure context (<code>localhost</code> or <code>https://</code>) to access the microphone.</p>", unsafe_allow_html=True)

        from audiorecorder import audiorecorder
        import speech_recognition as sr
        import io

        if 'recorder_key' not in st.session_state:
            st.session_state.recorder_key = 1

        audio_data_obj = audiorecorder("", "", key=f"recorder_{st.session_state.recorder_key}")

        if len(audio_data_obj) > 0:
            wav_io = io.BytesIO()
            audio_data_obj.export(wav_io, format="wav")
            wav_io.seek(0)

            audio_bytes = wav_io.read()
            audio_id = hash(audio_bytes)
            wav_io.seek(0)

            if 'last_processed_audio_id' not in st.session_state or st.session_state.last_processed_audio_id != audio_id:
                st.session_state.last_processed_audio_id = audio_id

                try:
                    recognizer = sr.Recognizer()
                    with sr.AudioFile(wav_io) as source:
                        audio_data = recognizer.record(source)

                    with st.spinner("Decoding voice message..."):
                        voice_text = recognizer.recognize_google(audio_data)

                        st.session_state.detector_chatbot_messages.append({"role": "user", "content": f"🎤 Voice Message: \"{voice_text}\""})

                        voice_result, voice_api_error = None, None
                        try:
                            voice_result = api_client.predict_message(voice_text)
                        except ApiError as e:
                            voice_api_error = e

                        if voice_api_error:
                            st.session_state.recorder_key += 1
                            st.error(f"❌ Backend error: {voice_api_error.message}")
                        else:
                            log_scan_stats(voice_result['label'])

                            if voice_result['label'] == 1:
                                bot_reply = "🚨 This voice message was flagged as potential cyberbullying. Stay calm, don't reply, and talk to a trusted adult."
                            else:
                                bot_reply = "🟢 This voice message looks safe and friendly!"

                            st.session_state.detector_chatbot_messages.append({"role": "assistant", "content": bot_reply})

                            st.session_state.last_scanned_result = {
                                "text": f"🎤 Voice: \"{voice_text}\"",
                                "label": voice_result['label'],
                                "confidence": voice_result['confidence'],
                                "method": f"{voice_result['method']} (Speech-to-Text)",
                                "matched_words": voice_result['matched_words'],
                                "category": voice_result['category'],
                                "severity": voice_result['severity'],
                                "elapsed_ms": None
                            }
                            st.session_state.recorder_key += 1
                            st.rerun()
                except sr.UnknownValueError:
                    st.session_state.recorder_key += 1
                    st.warning("🎙️ Could not understand the voice audio. Please speak clearly and try again.")
                except sr.RequestError as e:
                    st.session_state.recorder_key += 1
                    st.error(f"🌐 API Connection Error: {e}")
                except Exception as e:
                    st.session_state.recorder_key += 1
                    st.error(f"❌ System Error ({type(e).__name__}): {e}")

        st.markdown("</div>", unsafe_allow_html=True)

        # Recent conversation log
        if len(st.session_state.detector_chatbot_messages) > 1:
            with st.expander("💬 Conversation Log"):
                for m in st.session_state.detector_chatbot_messages:
                    with st.chat_message(m["role"]):
                        st.markdown(m["content"], unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='glass-card'><div class='card-title'>📈 Analysis Result</div>", unsafe_allow_html=True)

        if st.session_state.last_scanned_result is None:
            st.info("💡 Analyze a message to see real-time results here.")
        else:
            res = st.session_state.last_scanned_result
            is_bullying = res['label'] == 1
            confidence_pct = res['confidence'] * 100

            st.write("**Scanned Text:**")
            st.code(res['text'], language="text")

            if is_bullying:
                st.markdown("<span class='badge badge-danger'>🚨 Cyberbullying Detected</span>", unsafe_allow_html=True)
            else:
                st.markdown("<span class='badge badge-safe'>🟢 Safe Message</span>", unsafe_allow_html=True)

            st.plotly_chart(render_gauge(confidence_pct, is_bullying), use_container_width=True, config={'displayModeBar': False})

            chip_col1, chip_col2 = st.columns(2)
            with chip_col1:
                st.markdown(f"<span class='chip'>Category: {res['category']}</span>", unsafe_allow_html=True)
            with chip_col2:
                st.markdown(f"<span class='chip'>Severity: {res['severity']}</span>", unsafe_allow_html=True)

            meta_col1, meta_col2 = st.columns(2)
            with meta_col1:
                st.metric("Method", res['method'])
            with meta_col2:
                if res.get('elapsed_ms') is not None:
                    st.metric("Processing Time", f"{res['elapsed_ms']:.1f} ms")
                else:
                    st.metric("Processing Time", "—")

            st.plotly_chart(render_probability_bar(res['confidence'], is_bullying), use_container_width=True, config={'displayModeBar': False})

            if res['matched_words']:
                try:
                    detox_data = api_client.detox_text(res['text'], res['matched_words'])
                    highlighted = detox_data['highlighted_text']
                except ApiError:
                    highlighted = res['text']
                formatted_html = highlighted.replace("**:", "<span style='background-color:rgba(239,68,68,0.25); color:#FCA5A5; padding:2px 6px; border-radius:4px; font-weight:bold;'>")
                formatted_html = formatted_html.replace(":**", "</span>")
                st.markdown(f"<p style='font-size:0.85rem; margin-top:0.5rem;'><b>Flagged Words</b></p><div style='padding: 10px; border-radius: 10px; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.08); line-height: 1.6;'>{formatted_html}</div>", unsafe_allow_html=True)

            if is_bullying:
                try:
                    detox_data = api_client.detox_text(res['text'], res['matched_words'])
                    detoxified = detox_data['detoxified_text']
                except ApiError:
                    detoxified = res['text']
                st.markdown("<p style='font-size:0.85rem; margin-top:0.8rem;'><b>✨ Detoxified Rewrite</b></p>", unsafe_allow_html=True)
                st.success(detoxified)
                st.markdown("<div class='banner-danger' style='margin-top:0.6rem;'>💡 Stay calm, don't reply, take a screenshot, block the sender, and talk to a trusted adult.</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# PAGE 3: CHAT SIMULATOR
# ==========================================
elif page == "💬 Chat Simulator":
    st.markdown("## 💬 Chat Simulator")
    st.markdown("<p>See how CyberGuard AI moderates content in real social feeds and live chat rooms.</p>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📱 Social Feed", "💬 Live Chatroom"])

    # SUB-TAB 1: SOCIAL FEED
    with tab1:
        st.markdown("<p style='font-size:0.9rem;'>Toxic posts are shielded behind a blur so users aren't exposed to sudden harassment.</p>", unsafe_allow_html=True)

        try:
            simulated_posts = api_client.get_simulated_posts()
        except ApiError as e:
            simulated_posts = []
            st.error(f"❌ Could not load simulated posts from backend: {e.message}")

        for idx, post in enumerate(simulated_posts):
            try:
                res = api_client.predict_message(post['content'])
            except ApiError as e:
                st.error(f"❌ Backend error scanning post: {e.message}")
                continue

            st.markdown(f"""
            <div class="glass-card" style="padding: 1.1rem 1.3rem;">
                <div class="chat-row">
                    <div class="chat-avatar">{post['avatar']}</div>
                    <div>
                        <strong style="color:#F8FAFC;">@{post['username']}</strong>
                        <span class="chat-meta">{post['platform']} • {post['time']}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            if res['label'] == 1:
                post_key = f"post_blur_{idx}"
                if post_key not in st.session_state.blocked_simulated_posts:
                    st.session_state.blocked_simulated_posts[post_key] = True

                if st.session_state.blocked_simulated_posts[post_key] == True:
                    st.markdown("<div class='banner-danger'>⚠️ <b>Flagged for cyberbullying/harassment.</b> Content is hidden.</div>", unsafe_allow_html=True)
                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        if st.button("Reveal Content", key=f"btn_reveal_{idx}"):
                            st.session_state.blocked_simulated_posts[post_key] = False
                            st.rerun()
                    with col_btn2:
                        if st.button("✨ Detoxify Post", key=f"btn_detox_{idx}"):
                            st.session_state.blocked_simulated_posts[post_key] = "detox"
                            st.rerun()
                elif st.session_state.blocked_simulated_posts[post_key] == "detox":
                    try:
                        detoxified_content = api_client.detox_text(post['content'], res['matched_words'])['detoxified_text']
                    except ApiError:
                        detoxified_content = post['content']
                    st.markdown(f"<p style='color:#86EFAC; font-style:italic; background:rgba(34,197,94,0.08); padding:10px; border-radius:10px; border-left:3px solid #22C55E;'>✨ {detoxified_content}</p>", unsafe_allow_html=True)
                    if st.button("Re-Shield Content", key=f"btn_shield_{idx}"):
                        st.session_state.blocked_simulated_posts[post_key] = True
                        st.rerun()
                else:
                    st.markdown(f"<p class='chat-bubble blurred' style='max-width:100%; display:block;'>{post['content']}</p>", unsafe_allow_html=True)
                    if st.button("Re-Shield Content", key=f"btn_shield_{idx}"):
                        st.session_state.blocked_simulated_posts[post_key] = True
                        st.rerun()
            else:
                st.markdown(f"<p style='color:#E2E8F0; margin-top:0.5rem;'>{post['content']}</p>", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

    # SUB-TAB 2: LIVE CHATROOM
    with tab2:
        st.markdown("<p style='font-size:0.9rem;'>Type a message. If flagged, it's automatically censored and a warning is issued.</p>", unsafe_allow_html=True)

        if st.session_state.user_warnings >= 3:
            st.markdown("<div class='banner-danger'>🚫 <b>Account Suspended:</b> 3 cyberbullying attempts detected. Chat privileges restricted.</div>", unsafe_allow_html=True)
            if st.button("Reset Simulator"):
                st.session_state.user_warnings = 0
                st.session_state.chat_messages = [
                    {"user": "Alice", "msg": "Hey everyone! Did you finish the AI project assignment?", "censored": False, "type": "Neutral"},
                    {"user": "Bob", "msg": "Yes! I spent the weekend writing code for TF-IDF. It's actually very cool.", "censored": False, "type": "Neutral"}
                ]
                st.rerun()
        else:
            if st.session_state.user_warnings > 0:
                st.markdown(f"<div class='banner-danger'>⚠️ <b>{st.session_state.user_warnings}/3</b> cyberbullying strikes. 3 strikes locks your chat.</div>", unsafe_allow_html=True)

            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            for msg in st.session_state.chat_messages:
                is_mine = msg['user'] == "You"
                initials = msg['user'][:2].upper()

                if msg['censored']:
                    text_disp = "<i style='color:#94A3B8;'>[Message blocked — toxic content censored]</i>"
                    badge = "<span class='mod-badge mod-blocked'>Censored</span>"
                else:
                    text_disp = msg['msg']
                    badge = "<span class='mod-badge mod-approved'>Approved</span>"

                row_class = "chat-row mine" if is_mine else "chat-row"
                st.markdown(f"""
                <div class="{row_class}">
                    <div class="chat-avatar">{initials}</div>
                    <div>
                        <div class="chat-bubble">{text_disp}{badge}</div>
                        <div class="chat-meta">{msg['user']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            with st.form("chat_form", clear_on_submit=True):
                new_msg = st.text_input("Type your chat message...", placeholder="Keep it clean, nice, and friendly!")
                submit = st.form_submit_button("Send Message")

                if submit and new_msg.strip():
                    try:
                        sim_result = api_client.send_chat_message(new_msg)
                    except ApiError as e:
                        st.error(f"❌ Backend error: {e.message}")
                        st.stop()

                    is_blocked = sim_result.get('blocked', False)
                    log_scan_stats(1 if is_blocked else 0)

                    if is_blocked:
                        st.session_state.user_warnings += 1
                        st.session_state.chat_messages.append({
                            "user": "You", "msg": new_msg, "censored": True, "type": "Flagged Bullying"
                        })
                        st.error("🚨 Message Blocked! CyberGuard AI flagged that comment as toxic.")
                        st.rerun()
                    else:
                        st.session_state.chat_messages.append({
                            "user": "You", "msg": new_msg, "censored": False, "type": "Neutral"
                        })
                        st.success("✅ Message posted successfully!")
                        st.rerun()

# ==========================================
# PAGE 4: ANALYTICS
# ==========================================
elif page == "📊 Analytics":
    st.markdown("## 📊 AI Model Analytics")
    st.markdown("<p>Model training console, evaluation metrics, and dataset insights.</p>", unsafe_allow_html=True)

    col1, col2 = st.columns([5, 7])

    with col1:
        st.markdown("""
        <div class="glass-card">
            <div class="card-title">⚙️ Machine Learning Pipeline</div>
            <p style="font-size: 0.9rem; line-height: 1.6;">
                The model uses <b>TF-IDF Vectorization</b> to measure how unique and critical a word is across documents:
            </p>
            <code style="font-size:0.8rem; display:block; text-align:center; padding: 8px; margin-bottom:10px;">
                TF-IDF = TF(t, d) × IDF(t)
            </code>
            <p style="font-size: 0.9rem; line-height: 1.6;">
                The resulting matrix feeds into a <b>Logistic Regression Classifier</b>, which learns the probability of cyberbullying via a sigmoid function.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div class='glass-card'><div class='card-title'>🛠️ Model Controller</div>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:0.8rem; color:#94A3B8;'>Retraining is admin-only. Log in as an admin account and paste your access token below.</p>", unsafe_allow_html=True)
        st.session_state.admin_token = st.text_input(
            "Admin access token", value=st.session_state.admin_token or "", type="password",
            placeholder="Paste the JWT from /api/v1/auth/login for an admin account"
        )

        if st.button("Retrain Model", type="primary", use_container_width=True):
            if not st.session_state.admin_token:
                st.warning("⚠️ Enter an admin access token first.")
            else:
                with st.spinner("Preprocessing text → Computing TF-IDF matrix → Fitting Logistic Regression..."):
                    try:
                        retrain_result = api_client.retrain_model(st.session_state.admin_token)
                        st.session_state.model_trained = True
                        st.success(f"🎉 Model trained successfully! Accuracy: {retrain_result['accuracy']*100:.2f}%")
                        st.balloons()
                        st.rerun()
                    except ApiError as e:
                        st.error(f"Training failed: {e.message}")

        try:
            model_status = api_client.get_model_status()
        except ApiError:
            model_status = {"model_loaded": False, "accuracy": None}

        if model_status.get("model_loaded") and model_status.get("accuracy") is not None:
            st.metric("Trained Model Accuracy", f"{model_status['accuracy'] * 100:.2f}%", help="Calculated using a standard 20% test-split.")
        else:
            st.info("🧠 Model file not found. Click Retrain above.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        try:
            model_analytics = api_client.get_model_analytics()
        except ApiError:
            model_analytics = {"trained": False}

        if model_analytics.get("trained"):
            st.markdown("<div class='glass-card'><div class='card-title'>🧮 Confusion Matrix</div>", unsafe_allow_html=True)
            cm = np.array(model_analytics['confusion_matrix'])
            labels = ['Predicted Clean', 'Predicted Bullying']
            y_labels = ['Actual Clean', 'Actual Bullying']

            fig_cm = go.Figure(data=go.Heatmap(
                z=cm,
                x=labels,
                y=y_labels,
                colorscale=[[0, "#1E293B"], [1, "#2563EB"]],
                text=cm,
                texttemplate="%{text}",
                textfont={"color": "#F8FAFC", "size": 16},
                showscale=False
            ))
            fig_cm.update_layout(
                height=320,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font={'color': "#F8FAFC", 'family': "Inter"},
                margin=dict(l=10, r=10, t=10, b=10),
                yaxis=dict(autorange="reversed")
            )
            st.plotly_chart(fig_cm, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div class='glass-card'><div class='card-title'>🔥 Top Predictive Words</div>", unsafe_allow_html=True)
            try:
                top_words_data = api_client.get_top_toxic_words(top_n=10)
            except ApiError:
                top_words_data = []

            if top_words_data:
                words = [w['word'] for w in top_words_data]
                weights = [w['weight'] for w in top_words_data]
                fig_words = px.bar(
                    x=weights, y=words, orientation='h',
                    color=weights, color_continuous_scale=['#7C3AED', '#EF4444']
                )
                fig_words.update_layout(
                    height=340,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font={'color': "#F8FAFC", 'family': "Inter"},
                    coloraxis_showscale=False,
                    margin=dict(l=10, r=20, t=10, b=10),
                    yaxis=dict(autorange="reversed", title=""),
                    xaxis=dict(title="Coefficient Weight")
                )
                st.plotly_chart(fig_words, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='banner-danger'>📊 Metric visualizations will load once the model is trained.</div>", unsafe_allow_html=True)

# ==========================================
# PAGE 5: SAFETY GUIDE
# ==========================================
elif page == "📚 Safety Guide":
    st.markdown("## 📚 Safety Guide")
    st.markdown("<p>Cyber safety tips, legal resources, and emergency contacts.</p>", unsafe_allow_html=True)

    col1, col2 = st.columns([7, 5])

    try:
        cyber_laws = api_client.get_cyber_laws()
    except ApiError as e:
        cyber_laws = []
        st.error(f"❌ Could not load cyber laws: {e.message}")

    try:
        helplines = api_client.get_helplines()
    except ApiError as e:
        helplines = []
        st.error(f"❌ Could not load helplines: {e.message}")

    try:
        safety_tips = api_client.get_safety_tips()
    except ApiError as e:
        safety_tips = []
        st.error(f"❌ Could not load safety tips: {e.message}")

    with col1:
        st.markdown("<div class='glass-card'><div class='card-title'>📜 Cyber Laws & Penalties</div>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:0.88rem;'>Cyberbullying is a punishable offense under law:</p>", unsafe_allow_html=True)

        for law in cyber_laws:
            st.markdown(f"""
            <div style='background: rgba(255,255,255,0.04); padding: 1rem; border-radius: 12px; border-left: 3px solid #2563EB; margin-bottom: 0.75rem;'>
                <strong style='color:#F8FAFC; font-size:1rem;'>{law['act']} : {law['name']}</strong>
                <p style='font-size:0.85rem; margin: 0.5rem 0; line-height:1.5;'>{law['desc']}</p>
                <span style='color:#93C5FD; font-size:0.8rem; font-style:italic;'><b>Relevance:</b> {law['relevance']}</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("<p style='font-size:0.75rem; color:#64748B; font-style:italic;'>This information is educational/reference material only and is not personalized legal advice.</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='glass-card'><div class='card-title'>🚨 Emergency Helplines</div>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:0.85rem;'>Reach out immediately if you or a friend face severe online threats:</p>", unsafe_allow_html=True)

        for hp in helplines:
            st.markdown(f"""
            <div style='background: rgba(34,197,94,0.07); padding: 1rem; border-radius: 12px; border-left: 3px solid #22C55E; margin-bottom: 0.75rem;'>
                <strong style='color:#F8FAFC; font-size:0.95rem;'>{hp['agency']}</strong><br>
                <span style='color:#86EFAC; font-size:1.05rem; font-weight:700;'>📞 {hp['contact']}</span>
                <p style='font-size:0.82rem; margin: 0.3rem 0;'>{hp['desc']}</p>
                <a href='{hp['website']}' target='_blank' style='font-size:0.78rem; color:#93C5FD; font-weight:bold;'>Visit Web Portal 🌐</a>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='glass-card'><div class='card-title'>🛡️ Coping Strategies</div>", unsafe_allow_html=True)
        for tip in safety_tips:
            st.markdown(f"<p style='font-size:0.87rem;'>🔹 <b>{tip['title']}</b> — {tip['desc']}</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# PAGE 6: ABOUT
# ==========================================
elif page == "ℹ️ About":
    st.markdown("## ℹ️ About CyberGuard AI")

    st.markdown("""
    <div class="glass-card">
        <div class="card-title">🛡 What is CyberGuard AI?</div>
        <p style="font-size:0.92rem; line-height:1.65;">
            CyberGuard AI is an automated Machine Learning & NLP system that scans text in real time,
            detects offensive vocabulary, classifies severity levels, and censors harmful content instantly —
            protecting people from cyberbullying across social media, chat rooms, and online forums.
        </p>
        <p style="font-size:0.92rem; line-height:1.65;">
            The pipeline includes a text-cleaning stage, TF-IDF vectorization for feature extraction, and a
            Logistic Regression classifier trained on a curated dataset of safe and toxic messages.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="glass-card">
        <div class="card-title">👥 Project Developers</div>
        <p style="font-size:0.92rem;">This application was developed by a team of four:</p>
        <ul style="font-size:0.92rem;">
            <li><b>Vansh Parashar</b></li>
            <li><b>Ruth</b></li>
            <li><b>Shivani</b></li>
            <li><b>Shafqat</b></li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# PAGE 7: SETTINGS
# ==========================================
elif page == "⚙️ Settings":
    st.markdown("## ⚙️ Settings")
    st.markdown("<p>Manage session data and view system information.</p>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<div class='glass-card'><div class='card-title'>🧹 Session Data</div>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:0.88rem;'>Reset chat history, warnings, and scan statistics for this session.</p>", unsafe_allow_html=True)
        if st.button("Reset Session Data", use_container_width=True):
            st.session_state.chat_messages = [
                {"user": "Alice", "msg": "Hey everyone! Did you finish the AI project assignment?", "censored": False, "type": "Neutral"},
                {"user": "Bob", "msg": "Yes! I spent the weekend writing code for TF-IDF. It's actually very cool.", "censored": False, "type": "Neutral"}
            ]
            st.session_state.user_warnings = 0
            st.session_state.blocked_simulated_posts = {}
            st.session_state.detector_chatbot_messages = [
                {"role": "assistant", "content": "👋 Hello! I am your CyberGuard AI Safety Bot. Type any message below, and I will scan it for cyberbullying in real time!"}
            ]
            st.session_state.last_scanned_result = None
            st.session_state.stats_total_scanned = 0
            st.session_state.stats_safe_count = 0
            st.session_state.stats_bullying_count = 0
            st.success("Session data reset.")
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='glass-card'><div class='card-title'>🧠 System Information</div>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size:0.88rem;'><b>Model Status:</b> {'Active' if st.session_state.model_trained else 'Lexicon Fallback'}</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size:0.88rem;'><b>Messages Scanned This Session:</b> {st.session_state.stats_total_scanned}</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size:0.88rem;'><b>Chat Warnings Issued:</b> {st.session_state.user_warnings}</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("---")
st.markdown("<p style='text-align: center; color: #64748B; font-size: 0.8rem;'>© CyberGuard AI • AI-Powered Cyberbullying Detection Platform. Built with Streamlit.</p>", unsafe_allow_html=True)
