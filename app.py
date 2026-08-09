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

    /* ========================================================
       V2 DESIGN SYSTEM — solid navy cards, icon badges, nav pills
       ======================================================== */

    /* Solid panel used by the redesigned Dashboard / AI Detector */
    .panel {
        background: #121A2E;
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 18px;
        padding: 1.4rem 1.5rem;
        margin-bottom: 1.1rem;
    }
    .panel-title { font-size: 1rem; font-weight: 700; color: var(--text) !important; margin-bottom: 0.2rem; }
    .panel-sub { font-size: 0.82rem; color: #64748B !important; margin-bottom: 1rem; }

    /* Icon badges (rounded gradient squares) */
    .icon-badge {
        width: 42px; height: 42px; border-radius: 12px;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.2rem; flex-shrink: 0;
    }
    .icon-badge.blue   { background: linear-gradient(135deg,#2563EB,#3B82F6); box-shadow: 0 4px 16px rgba(37,99,235,0.35); }
    .icon-badge.green  { background: linear-gradient(135deg,#16A34A,#22C55E); box-shadow: 0 4px 16px rgba(34,197,94,0.35); }
    .icon-badge.teal   { background: linear-gradient(135deg,#0D9488,#14B8A6); box-shadow: 0 4px 16px rgba(20,184,166,0.35); }
    .icon-badge.red    { background: linear-gradient(135deg,#DC2626,#EF4444); box-shadow: 0 4px 16px rgba(239,68,68,0.35); }
    .icon-badge.purple { background: linear-gradient(135deg,#7C3AED,#8B5CF6); box-shadow: 0 4px 16px rgba(124,58,237,0.35); }

    /* Stat cards v2 */
    .stat-card-v2 {
        background: #121A2E;
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 18px;
        padding: 1.25rem 1.3rem;
        height: 100%;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .stat-card-v2:hover { transform: translateY(-3px); border-color: rgba(124,92,237,0.35); }
    .stat-card-v2 .stat-v2-top { display: flex; align-items: center; gap: 0.7rem; margin-bottom: 0.9rem; }
    .stat-card-v2 .stat-v2-label { font-size: 0.85rem; font-weight: 600; color: #94A3B8 !important; }
    .stat-card-v2 .stat-v2-big { font-size: 1.85rem; font-weight: 800; color: var(--text) !important; line-height: 1; margin-bottom: 0.3rem; }
    .stat-card-v2 .stat-v2-sub { font-size: 0.78rem; color: #64748B !important; }

    /* Info cards v2 (Objective / Technology / Applications) */
    .info-card-v2 {
        background: #121A2E;
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 18px;
        padding: 1.35rem 1.4rem;
        height: 100%;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .info-card-v2:hover { transform: translateY(-3px); border-color: rgba(37,99,235,0.35); }
    .info-card-v2 .info-v2-head { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.8rem; }
    .info-card-v2 .info-v2-title { font-weight: 700; font-size: 1rem; color: var(--text) !important; }
    .info-card-v2 .info-v2-desc { font-size: 0.85rem; color: #94A3B8 !important; line-height: 1.6; }

    /* Hero shield illustration */
    .hero-shield-wrap { position: relative; display: flex; align-items: center; justify-content: center; height: 230px; }
    .hero-shield-glow {
        position: absolute; width: 200px; height: 200px; border-radius: 50%;
        background: radial-gradient(circle, rgba(59,130,246,0.35), transparent 70%);
        filter: blur(6px);
        animation: shield-breathe 4s ease-in-out infinite;
    }
    @keyframes shield-breathe { 0%,100% { opacity: 0.7; transform: scale(1); } 50% { opacity: 1; transform: scale(1.08); } }
    .hero-shield-icon { position: relative; font-size: 6.2rem; z-index: 2; filter: drop-shadow(0 0 22px rgba(59,130,246,0.55)); }
    .hero-float-chip {
        position: absolute; background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.12);
        border-radius: 10px; padding: 6px 11px; font-size: 0.74rem; color: #E2E8F0 !important;
        backdrop-filter: blur(6px); box-shadow: 0 6px 18px rgba(0,0,0,0.25); z-index: 3;
        animation: chip-float 3.4s ease-in-out infinite;
    }
    @keyframes chip-float { 0%,100% { transform: translateY(0px); } 50% { transform: translateY(-7px); } }
    .hero-float-chip.c1 { top: 4%; right: 2%; animation-delay: 0s; }
    .hero-float-chip.c2 { bottom: 10%; left: 0%; animation-delay: 1.1s; }
    .hero-float-chip.c3 { bottom: 2%; right: 10%; animation-delay: 2s; }

    /* Status pill (AI Detector verdict) */
    .status-pill {
        display: inline-flex; align-items: center; gap: 6px;
        padding: 6px 15px; border-radius: 999px; font-weight: 700; font-size: 0.85rem;
    }
    .status-pill.safe   { background: rgba(34,197,94,0.15); color: #4ADE80 !important; border: 1px solid rgba(34,197,94,0.4); }
    .status-pill.danger { background: rgba(239,68,68,0.15); color: #F87171 !important; border: 1px solid rgba(239,68,68,0.4); }
    .severity-dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; margin-right: 6px; }

    /* Char counter under textarea */
    .char-counter { font-size: 0.76rem; color: #64748B !important; text-align: right; margin-top: -0.4rem; margin-bottom: 0.6rem; }

    /* ---------- MIC ORB + RECORDING ANIMATION ---------- */
    .mic-orb-wrap { display: flex; flex-direction: column; align-items: center; gap: 0.5rem; padding: 0.8rem 0 0.4rem 0; }
    .mic-orb { position: relative; width: 76px; height: 76px; display: flex; align-items: center; justify-content: center; }
    .mic-orb-ring {
        position: absolute; width: 76px; height: 76px; border-radius: 50%;
        border: 2px solid rgba(37,99,235,0.55);
        animation: mic-pulse 2.2s ease-out infinite;
    }
    .mic-orb-ring.r2 { animation-delay: 0.7s; border-color: rgba(124,58,237,0.5); }
    @keyframes mic-pulse { 0% { transform: scale(0.85); opacity: 0.9; } 100% { transform: scale(2); opacity: 0; } }
    .mic-orb-core {
        position: relative; z-index: 2; width: 56px; height: 56px; border-radius: 50%;
        background: linear-gradient(135deg, #2563EB, #7C3AED);
        display: flex; align-items: center; justify-content: center;
        font-size: 1.5rem; box-shadow: 0 6px 22px rgba(37,99,235,0.45);
    }
    .voice-hint { font-size: 0.78rem; color: #64748B !important; text-align: center; margin: 0; }

    .waveform { display: flex; align-items: center; justify-content: center; gap: 4px; height: 34px; margin: 0.5rem 0; }
    .waveform span {
        width: 4px; border-radius: 3px;
        background: linear-gradient(180deg, #2563EB, #7C3AED);
        animation: wave-bounce 0.9s ease-in-out infinite;
        display: inline-block;
    }
    .waveform span:nth-child(1) { height: 10px; animation-delay: 0s; }
    .waveform span:nth-child(2) { height: 22px; animation-delay: 0.1s; }
    .waveform span:nth-child(3) { height: 30px; animation-delay: 0.2s; }
    .waveform span:nth-child(4) { height: 18px; animation-delay: 0.3s; }
    .waveform span:nth-child(5) { height: 12px; animation-delay: 0.4s; }
    @keyframes wave-b
