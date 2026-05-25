import streamlit as st
import time
import re
import json
import os
from openai import OpenAI

## ── PAGE CONFIG ─────────────────────────────────────────────
st.set_page_config(
    page_title="BrainBlitz · Quiz App",
    page_icon="🧠",
    layout="centered"
)

# ── API KEYS ─────────────────────────────────────────────────────────────────
xai_api_key = (
    os.getenv("XAI_API_KEY")
    or st.secrets.get("XAI_API_KEY", None)
)
openrouter_api_key = (
    os.getenv("OPENROUTER_API_KEY")
    or st.secrets.get("OPENROUTER_API_KEY", None)
)

if not xai_api_key and not openrouter_api_key:
    st.error("No API keys found. Add XAI_API_KEY and/or OPENROUTER_API_KEY to .env or Streamlit secrets.")
    st.stop()

# ── CLIENTS ───────────────────────────────────────────────────────────────────
@st.cache_resource
def _build_groq_client(key):
    return OpenAI(api_key=key, base_url="https://api.groq.com/openai/v1")

@st.cache_resource
def _build_openrouter_client(key):
    return OpenAI(api_key=key, base_url="https://openrouter.ai/api/v1")

groq_client       = _build_groq_client(xai_api_key)       if xai_api_key       else None
openrouter_client = _build_openrouter_client(openrouter_api_key) if openrouter_api_key else None

GROK_MODEL       = "llama-3.1-8b-instant"
OPENROUTER_MODEL = "openai/gpt-4o-mini"
NUM_QUESTIONS    = 5
MAX_TOKENS       = 900

# ══════════════════════════════════════════════════════════════════════════════
# GLOBAL CSS  –  injected ONCE via st.cache_data so it never re-fires
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=None)
def _css_block():
    """Return the full CSS string. Cached so it is computed only once."""
    return '''
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800;900&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>

/* ─── Base ───────────────────────────────────────────────────────────── */
#MainMenu, footer, header { visibility: hidden; }
* { box-sizing: border-box; }
html, body, .stApp {
    background: #04060d !important;
    font-family: 'Inter', sans-serif;
    color: #dde3f0;
}
.block-container {
    max-width: 740px !important;
    padding: 2.5rem 1.5rem 5rem !important;
}

/* ─── Orbs ───────────────────────────────────────────────────────────── */
.orb-a {
    position: fixed; width: 600px; height: 600px;
    top: -200px; right: -200px;
    background: radial-gradient(circle, rgba(99,102,241,.16) 0%, transparent 60%);
    border-radius: 50%; pointer-events: none; z-index: 0;
}
.orb-b {
    position: fixed; width: 500px; height: 500px;
    bottom: -150px; left: -150px;
    background: radial-gradient(circle, rgba(236,72,153,.11) 0%, transparent 60%);
    border-radius: 50%; pointer-events: none; z-index: 0;
}

/* ─── Brand ──────────────────────────────────────────────────────────── */
.brand-wrap { text-align: center; margin-bottom: 4px; }
.brand-logo {
    display: inline-block;
    font-family: 'Syne', sans-serif;
    font-weight: 900; font-size: 52px; letter-spacing: -2px; line-height: 1;
    background: linear-gradient(135deg, #818cf8 0%, #c084fc 45%, #f472b6 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
}
.brand-tag {
    text-align: center; letter-spacing: 4px; font-size: 11px;
    text-transform: uppercase; color: #2d3748; font-weight: 600;
    margin-bottom: 28px;
}

/* ─── Step bar ────────────────────────────────────────────────────────── */
.stepbar {
    display: flex; align-items: center; justify-content: center;
    gap: 0; margin: 0 auto 32px; max-width: 340px;
}
.step-item {
    display: flex; flex-direction: column; align-items: center; gap: 6px;
    flex: 1;
}
.step-circle {
    width: 32px; height: 32px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 13px; font-weight: 700;
    transition: all .3s ease;
}
.step-circle.done   { background: rgba(99,102,241,.25); color: #818cf8; border: 2px solid #6366f1; }
.step-circle.active { background: linear-gradient(135deg,#6366f1,#a855f7); color: #fff; border: 2px solid transparent; box-shadow: 0 0 18px rgba(99,102,241,.5); }
.step-circle.idle   { background: rgba(255,255,255,.04); color: #2d3748; border: 2px solid rgba(255,255,255,.08); }
.step-label { font-size: 10px; letter-spacing: 1px; text-transform: uppercase; font-weight: 600; }
.step-label.done   { color: #6366f1; }
.step-label.active { color: #c084fc; }
.step-label.idle   { color: #1e2535; }
.step-line      { flex: 1; height: 2px; background: rgba(255,255,255,.07); margin-top: -22px; }
.step-line.done { background: linear-gradient(90deg,#6366f1,#a855f7); }

/* ─── Login card ───────────────────────────────────────────────────── */
.login-header {
    background: linear-gradient(145deg, rgba(22,30,50,.95), rgba(10,15,28,.98));
    border: 1px solid rgba(99,102,241,.22); border-radius: 24px;
    padding: 36px 40px 8px; margin-bottom: -10px; position: relative; overflow: hidden;
}
.login-header::before {
    content:""; position:absolute; top:0; left:0; right:0; height:3px;
    background: linear-gradient(90deg,#6366f1,#a855f7,#ec4899); border-radius: 24px 24px 0 0;
}
.login-footer {
    background: linear-gradient(145deg, rgba(22,30,50,.95), rgba(10,15,28,.98));
    border: 1px solid rgba(99,102,241,.22); border-top: none;
    border-radius: 0 0 24px 24px; padding: 8px 40px 32px;
}
.section-chip {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(99,102,241,.12); border: 1px solid rgba(99,102,241,.3);
    color: #818cf8; font-size: 11px; font-weight: 700; letter-spacing: 1.5px;
    text-transform: uppercase; padding: 5px 14px; border-radius: 99px; margin-bottom: 14px;
}
.login-title { font-family: 'Syne', sans-serif; font-size: 26px; font-weight: 800; color: #f1f5f9; margin-bottom: 6px; }
.login-sub { color: #3d4f6e; font-size: 14px; margin-bottom: 22px; line-height: 1.6; }
.divider-line { height: 1px; background: linear-gradient(90deg,transparent,rgba(99,102,241,.35),transparent); margin: 22px 0; }

/* ─── Inputs & Buttons ──────────────────────────────────────────────── */
div[data-testid="stTextInput"] label, div[data-testid="stPasswordInput"] label {
    font-size: 11px !important; font-weight: 700 !important; letter-spacing: 2px;
    text-transform: uppercase; color: #3d5070 !important; margin-bottom: 6px;
}
div[data-testid="stTextInput"] input, div[data-testid="stPasswordInput"] input {
    background: rgba(255,255,255,.04) !important; border: 1.5px solid rgba(255,255,255,.09) !important;
    border-radius: 12px !important; color: #dde3f0 !important; font-size: 15px !important; padding: 13px 16px !important;
}
div[data-testid="stTextInput"] input:focus, div[data-testid="stPasswordInput"] input:focus {
    border-color: rgba(99,102,241,.7) !important; box-shadow: 0 0 0 3px rgba(99,102,241,.13) !important;
    background: rgba(99,102,241,.04) !important;
}
div[data-testid="stButton"] > button {
    width: 100%; background: linear-gradient(135deg, #5a5fdb 0%, #9b44e8 100%);
    color: white; font-family: 'Syne', sans-serif; font-size: 15px; font-weight: 700;
    letter-spacing: .8px; border: none; border-radius: 14px; padding: 14px 28px; height: auto;
    box-shadow: 0 4px 24px rgba(99,102,241,.38); transition: all .2s ease;
}
div[data-testid="stButton"] > button:hover {
    background: linear-gradient(135deg, #4548c7 0%, #8226d4 100%);
    box-shadow: 0 8px 32px rgba(99,102,241,.55); transform: translateY(-2px);
}
div[data-testid="stButton"] > button:active { transform: translateY(0); }

.logout-area div[data-testid="stButton"] > button {
    background: rgba(255,255,255,.05) !important; border: 1px solid rgba(255,255,255,.1) !important;
    color: #4a5878 !important; font-size: 13px !important; box-shadow: none !important;
    letter-spacing: 0 !important; width: auto !important; padding: 8px 20px !important;
}

/* ─── Small Test-API button (login page only) ─────────────────────── */
.test-api-wrap div[data-testid="stButton"] > button {
    width: auto !important;
    padding: 5px 14px !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    letter-spacing: 0.5px !important;
    border-radius: 8px !important;
    box-shadow: none !important;
    background: rgba(99,102,241,.18) !important;
    border: 1px solid rgba(99,102,241,.35) !important;
    color: #818cf8 !important;
    height: auto !important;
    min-height: unset !important;
    line-height: 1.4 !important;
}
.test-api-wrap div[data-testid="stButton"] > button:hover {
    background: rgba(99,102,241,.3) !important;
    transform: none !important;
    box-shadow: none !important;
}

/* ─── Refresh button on subject cards ────────────────────────────── */
.refresh-btn-wrap div[data-testid="stButton"] > button {
    width: auto !important;
    padding: 3px 10px !important;
    font-size: 10px !important;
    font-weight: 600 !important;
    letter-spacing: 0.3px !important;
    border-radius: 6px !important;
    box-shadow: none !important;
    background: rgba(16,185,129,.12) !important;
    border: 1px solid rgba(16,185,129,.3) !important;
    color: #34d399 !important;
    height: auto !important;
    min-height: unset !important;
    line-height: 1.3 !important;
    margin-top: 4px !important;
}
.refresh-btn-wrap div[data-testid="stButton"] > button:hover {
    background: rgba(16,185,129,.25) !important;
    border-color: rgba(16,185,129,.6) !important;
    transform: none !important;
    box-shadow: none !important;
}
.refresh-btn-wrap.refreshed div[data-testid="stButton"] > button {
    background: rgba(99,102,241,.15) !important;
    border-color: rgba(99,102,241,.4) !important;
    color: #818cf8 !important;
}

/* ─── Subject cards & Difficulty Panel ───────────────────────────────── */
.s-card {
    background: rgba(255,255,255,.03); border: 1.5px solid rgba(255,255,255,.08);
    border-radius: 18px; padding: 22px 14px; text-align: center; transition: all .25s ease;
}
.s-card:hover {
    border-color: rgba(99,102,241,.5); background: rgba(99,102,241,.07);
    transform: translateY(-4px); box-shadow: 0 10px 32px rgba(99,102,241,.18);
}
.s-card.sel {
    border-color: rgba(168,85,247,.75); background: rgba(168,85,247,.1);
    box-shadow: 0 0 0 3px rgba(168,85,247,.2), 0 10px 32px rgba(168,85,247,.15);
}
.s-icon { font-size: 38px; line-height: 1; margin-bottom: 10px; }
.s-name { font-family: 'Syne', sans-serif; font-size: 15px; font-weight: 800; color: #e2e8f0; margin-bottom: 4px; }
.s-desc { font-size: 11px; color: #3d5070; font-weight: 500; }

.diff-panel {
    background: linear-gradient(145deg, rgba(18,26,48,.6), rgba(8,12,22,.8));
    border: 1px solid rgba(168,85,247,.3); border-radius: 16px;
    padding: 24px; margin-top: 16px; text-align: center; animation: fadeIn .4s ease;
}
@keyframes fadeIn { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }
.diff-title { font-family: 'Syne', sans-serif; font-size: 18px; font-weight: 700; color: #f0f4ff; margin-bottom: 16px; }

/* ─── User badge ────────────────────────────────────────────────────── */
.ubadge {
    display: flex; align-items: center; gap: 12px; background: rgba(255,255,255,.03);
    border: 1px solid rgba(255,255,255,.07); border-radius: 14px; padding: 11px 18px; margin-bottom: 22px;
}
.uavatar {
    width: 36px; height: 36px; border-radius: 50%; flex-shrink: 0;
    background: linear-gradient(135deg,#6366f1,#a855f7); display: flex; align-items: center;
    justify-content: center; font-family: 'Syne', sans-serif; font-weight: 900; font-size: 14px; color: white;
}
.uname  { font-weight: 600; font-size: 14px; color: #dde3f0; }
.uemail { font-size: 12px; color: #2d3e5a; }
.uxp    { color: #fbbf24; font-weight: 700; font-size: 11px; letter-spacing: 0.5px; }

/* ─── Timer & Progress ─────────────────────────────────────────────────── */
.stProgress > div > div { background: rgba(255,255,255,.05) !important; border-radius: 99px !important; height: 5px !important; }
.stProgress > div > div > div > div { background: linear-gradient(90deg,#6366f1,#a855f7,#ec4899) !important; }

.tmr {
    border-radius: 14px; padding: 11px 20px; text-align: center; font-family: 'Syne', sans-serif;
    font-size: 20px; font-weight: 800; margin-bottom: 16px; border: 1.5px solid;
    display: flex; align-items: center; justify-content: center; gap: 10px;
}
.t-safe   { background:rgba(16,185,129,.08); border-color:rgba(16,185,129,.3); color:#34d399; }
.t-warn   { background:rgba(245,158,11,.08); border-color:rgba(245,158,11,.3); color:#fbbf24; }
.t-danger { background:rgba(239,68,68,.1);   border-color:rgba(239,68,68,.4);  color:#f87171; }

/* ─── Score spill ───────────────────────────────────────────────────── */
.spill {
    font-family: 'Syne', sans-serif; font-size: 14px; font-weight: 800;
    color: #fbbf24; text-align: right; padding-top: 4px;
}

/* ─── Subject pill ──────────────────────────────────────────────────── */
.subj-pill {
    display: inline-block; background: rgba(168,85,247,.12);
    border: 1px solid rgba(168,85,247,.3); border-radius: 99px;
    padding: 5px 16px; font-size: 12px; font-weight: 700; letter-spacing: 0.5px;
    color: #c084fc; margin-bottom: 14px;
}

/* ─── H-divider ─────────────────────────────────────────────────────── */
.h-divider { height: 1px; background: linear-gradient(90deg,transparent,rgba(99,102,241,.3),transparent); margin: 28px 0; }

/* ─── Question card ─────────────────────────────────────────────────── */
.qcard {
    background: linear-gradient(155deg, rgba(18,26,48,.95), rgba(8,12,22,.98));
    border: 1.5px solid rgba(99,102,241,.2); border-radius: 22px; padding: 28px 30px;
    margin: 12px 0 20px; position: relative; overflow: hidden;
}
.qcard::before {
    content:""; position:absolute; top:0; left:0; right:0; height:3px;
    background: linear-gradient(90deg,#6366f1,#a855f7,#ec4899);
}
.qnum { font-size: 10px; font-weight: 700; letter-spacing: 3px; text-transform: uppercase; color: #5a5fdb; margin-bottom: 12px; }
.qtxt { font-family: 'Syne', sans-serif; font-size: 20px; font-weight: 700; color: #f0f4ff; line-height: 1.5; }

/* ─── Radio options ──────────────────────────────────────────────────── */
div[data-testid="stRadio"] > label { display: none; }
div[data-testid="stRadio"] > div { gap: 10px !important; flex-direction: column; }
div[data-testid="stRadio"] > div > label {
    background: rgba(255,255,255,.03) !important; border: 1.5px solid rgba(255,255,255,.08) !important;
    border-radius: 13px !important; padding: 13px 18px !important; color: #8899b8 !important; font-size: 14px !important;
}
div[data-testid="stRadio"] > div > label:hover {
    background: rgba(99,102,241,.1) !important; border-color: rgba(99,102,241,.45) !important;
    color: #dde3f0 !important; transform: translateX(6px);
}
div[data-testid="stRadio"] > div > label[data-checked="true"] {
    background: rgba(99,102,241,.15) !important; border-color: rgba(99,102,241,.7) !important; color: #a5b4fc !important;
}

/* ─── Mistake cards & Explanations ──────────────────────────────────── */
.mk { background:rgba(239,68,68,.07); border:1px solid rgba(239,68,68,.22); border-radius:12px; padding:16px 18px; margin:10px 0; }
.mk-q  { color:#64748b; font-size:14px; margin-bottom:6px; line-height:1.5; font-weight: 600;}
.mk-u  { color:#fca5a5; font-size:13px; margin-bottom:4px; }
.mk-c  { color:#86efac; font-size:13px; font-weight:700; margin-bottom: 8px;}
.mk-e  { color:#94a3b8; font-size:13px; margin-top:8px; line-height: 1.6; border-top: 1px dashed rgba(255,255,255,0.1); padding-top: 10px;}

/* ─── Result UI & Badges ────────────────────────────────────────────── */
.res-hero { text-align:center; padding:16px 0 12px; }
.res-emoji { font-size:72px; line-height:1; margin-bottom:10px; }
.res-grade { font-family:'Syne',sans-serif; font-size:34px; font-weight:900; margin-bottom:6px; }
.res-msg { color:#8899b8; font-size:16px; margin-bottom: 24px;}
.badge-card {
    display: inline-block; background: rgba(0,0,0,.3); border: 1px solid;
    border-radius: 18px; padding: 14px 28px; font-family: 'Syne', sans-serif;
    font-size: 22px; font-weight: 800; margin-bottom: 16px;
    box-shadow: 0 10px 30px rgba(0,0,0,.5);
}

/* ─── YouTube Resources Section ──────────────────────────────────── */
.yt-section-title {
    font-family: 'Syne', sans-serif; font-size: 20px; font-weight: 800;
    color: #f0f4ff; margin-bottom: 6px; display: flex; align-items: center; gap: 10px;
}
.yt-section-sub {
    font-size: 13px; color: #3d5070; margin-bottom: 18px; line-height: 1.5;
}
.yt-grid {
    display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 12px; margin-bottom: 8px;
}
.yt-card {
    background: linear-gradient(145deg, rgba(18,26,48,.9), rgba(8,12,22,.95));
    border: 1.5px solid rgba(255,0,0,.2); border-radius: 14px; padding: 16px 14px;
    text-decoration: none; transition: all .22s ease; display: block; position: relative;
    overflow: hidden;
}
.yt-card::before {
    content:""; position:absolute; top:0; left:0; right:0; height:2px;
    background: linear-gradient(90deg, #ff0000, #ff6b6b);
}
.yt-card:hover {
    border-color: rgba(255,0,0,.55); background: rgba(255,0,0,.07);
    transform: translateY(-3px); box-shadow: 0 8px 24px rgba(255,0,0,.15);
}
.yt-icon { font-size: 28px; margin-bottom: 8px; line-height: 1; }
.yt-title { font-family: 'Syne', sans-serif; font-size: 13px; font-weight: 700; color: #e2e8f0; margin-bottom: 4px; line-height: 1.4; }
.yt-desc  { font-size: 11px; color: #3d5070; line-height: 1.4; }
.yt-tag {
    display: inline-block; background: rgba(255,0,0,.12); border: 1px solid rgba(255,0,0,.25);
    color: #ff6b6b; font-size: 10px; font-weight: 700; letter-spacing: 0.5px;
    border-radius: 6px; padding: 2px 8px; margin-top: 6px;
}
.ai-tip-box {
    background: linear-gradient(135deg, rgba(99,102,241,.08) 0%, rgba(168,85,247,.06) 100%);
    border: 1px solid rgba(99,102,241,.22); border-radius: 16px; padding: 18px 22px;
    margin: 12px 0 20px; position: relative;
}
.ai-tip-box::before {
    content:""; position:absolute; top:0; left:0; right:0; height:2px;
    background: linear-gradient(90deg,#6366f1,#a855f7,#ec4899); border-radius:16px 16px 0 0;
}
.ai-tip-label {
    font-size: 10px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase;
    color: #6366f1; margin-bottom: 8px;
}
.ai-tip-text { font-size: 14px; color: #94a3b8; line-height: 1.7; }

/* ─── Back button override ────────────────────────────────────────── */
.back-btn-wrap div[data-testid="stButton"] > button {
    background: rgba(255,255,255,.04) !important;
    border: 1px solid rgba(255,255,255,.10) !important;
    color: #5a6a88 !important;
    box-shadow: none !important;
    font-size: 12px !important;
    padding: 9px 14px !important;
    letter-spacing: 0 !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    border-radius: 10px !important;
}
.back-btn-wrap div[data-testid="stButton"] > button:hover {
    background: rgba(99,102,241,.10) !important;
    border-color: rgba(99,102,241,.35) !important;
    color: #818cf8 !important;
    box-shadow: none !important;
    transform: none !important;
}

/* ─── Custom Subject Card & Panel ────────────────────────────────── */
.s-card.custom-card {
    border-color: rgba(236,72,153,.35);
    background: rgba(236,72,153,.05);
}
.s-card.custom-card:hover {
    border-color: rgba(236,72,153,.7);
    background: rgba(236,72,153,.1);
    box-shadow: 0 10px 32px rgba(236,72,153,.18);
}
.s-card.custom-card.sel {
    border-color: rgba(236,72,153,.8);
    background: rgba(236,72,153,.13);
    box-shadow: 0 0 0 3px rgba(236,72,153,.2), 0 10px 32px rgba(236,72,153,.15);
}
.custom-panel {
    background: linear-gradient(145deg, rgba(18,26,48,.95), rgba(8,12,22,.98));
    border: 1.5px solid rgba(236,72,153,.3); border-radius: 18px;
    padding: 26px 28px; margin-top: 16px; animation: fadeIn .35s ease;
    position: relative; overflow: hidden;
}
.custom-panel::before {
    content:""; position:absolute; top:0; left:0; right:0; height:3px;
    background: linear-gradient(90deg,#ec4899,#a855f7,#6366f1); border-radius: 18px 18px 0 0;
}
.custom-panel-title {
    font-family: 'Syne', sans-serif; font-size: 18px; font-weight: 800;
    color: #f0f4ff; margin-bottom: 4px;
}
.custom-panel-sub {
    font-size: 13px; color: #3d5070; margin-bottom: 20px; line-height: 1.5;
}
.gen-btn-wrap div[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #ec4899 0%, #a855f7 100%) !important;
    box-shadow: 0 4px 24px rgba(236,72,153,.35) !important;
}
.gen-btn-wrap div[data-testid="stButton"] > button:hover {
    background: linear-gradient(135deg, #db2777 0%, #9333ea 100%) !important;
    box-shadow: 0 8px 32px rgba(236,72,153,.55) !important;
}
.custom-ready-panel {
    background: linear-gradient(145deg, rgba(18,26,48,.9), rgba(8,12,22,.95));
    border: 1px solid rgba(16,185,129,.3); border-radius: 14px;
    padding: 14px 20px; margin-bottom: 16px;
    display: flex; align-items: center; gap: 12px;
}
.custom-ready-text { font-size: 13px; color: #34d399; font-weight: 600; }
.custom-ready-sub  { font-size: 11px; color: #2d5a4a; margin-top: 2px; }

/* ─── Performance: prevent layout thrash & reduce paint cost ─────── */
.stApp { contain: layout style; }
iframe { will-change: auto !important; }
div[data-testid="stVerticalBlock"] { contain: layout; }
</style>
<div class="orb-a"></div>
<div class="orb-b"></div>
'''

# NEW FIX: Remove empty lines so Markdown parser doesn't break, and inject unconditionally
safe_css = _css_block().replace("\n\n", "\n")
st.markdown(safe_css, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SUBJECT DATA
# ══════════════════════════════════════════════════════════════════════════════
SUBJECT_DATA = {
    "History":          {"icon": "📜", "desc": "India & the world"},
    "Geography":        {"icon": "🌍", "desc": "India, planets & beyond"},
    "Politics":         {"icon": "🏛️", "desc": "Civics and governance"},
    "Biology":          {"icon": "🔬", "desc": "Life & living systems"},
    "Computer Science": {"icon": "💻", "desc": "Coding & technology"},
    "English":          {"icon": "📖", "desc": "Grammar & vocabulary"},
}

# ══════════════════════════════════════════════════════════════════════════════
# YOUTUBE STUDY RESOURCES  (shown on result page)
# ══════════════════════════════════════════════════════════════════════════════
YOUTUBE_RESOURCES = {
    "History": [
        {"icon": "🏛️", "title": "India's Full History",         "desc": "Ancient to Modern India — complete playlist",           "url": "https://www.youtube.com/results?search_query=history+of+india+full+course+hindi+english",          "tag": "Full Course"},
        {"icon": "🌍", "title": "World History Explained",       "desc": "Key world events & civilisations",                      "url": "https://www.youtube.com/results?search_query=world+history+documentary+explained",                   "tag": "World"},
        {"icon": "⚔️",  "title": "Freedom Struggle",              "desc": "India's independence movement deep-dive",               "url": "https://www.youtube.com/results?search_query=india+freedom+struggle+independence+movement",           "tag": "India"},
        {"icon": "📺", "title": "History GK for Exams",          "desc": "Quick-revision MCQs for competitive exams",             "url": "https://www.youtube.com/results?search_query=history+gk+questions+competitive+exam+preparation",      "tag": "Exam Prep"},
    ],
    "Geography": [
        {"icon": "🗺️", "title": "Indian Geography Masterclass",  "desc": "Rivers, mountains, climate — full overview",            "url": "https://www.youtube.com/results?search_query=indian+geography+full+course+upsc",                      "tag": "India"},
        {"icon": "🌐", "title": "World Geography in Hindi/Eng",   "desc": "Continents, oceans & physical geography",               "url": "https://www.youtube.com/results?search_query=world+geography+full+course+explained",                   "tag": "World"},
        {"icon": "🪐", "title": "Solar System & Space",           "desc": "Planets, orbits and our universe",                     "url": "https://www.youtube.com/results?search_query=solar+system+planets+explained+for+students",             "tag": "Space"},
        {"icon": "📊", "title": "Geography MCQs",                 "desc": "Practice questions for exams",                         "url": "https://www.youtube.com/results?search_query=geography+mcq+quiz+exam+preparation",                     "tag": "Exam Prep"},
    ],
    "Politics": [
        {"icon": "📜", "title": "Indian Polity by Laxmikant",    "desc": "Constitution, Parliament & governance explained",       "url": "https://www.youtube.com/results?search_query=indian+polity+laxmikant+upsc+complete+course",            "tag": "Full Course"},
        {"icon": "⚖️",  "title": "Fundamental Rights & Duties",   "desc": "Articles, amendments & judgements",                    "url": "https://www.youtube.com/results?search_query=fundamental+rights+duties+indian+constitution+explained",  "tag": "Constitution"},
        {"icon": "🏛️", "title": "Parliament & Elections",         "desc": "How Indian democracy works",                           "url": "https://www.youtube.com/results?search_query=indian+parliament+election+commission+explained",           "tag": "Democracy"},
        {"icon": "🎯", "title": "Polity MCQs for Exams",          "desc": "Quick revision with practice questions",               "url": "https://www.youtube.com/results?search_query=indian+polity+mcq+exam+preparation+quiz",                 "tag": "Exam Prep"},
    ],
    "Biology": [
        {"icon": "🔬", "title": "Cell Biology Full Course",       "desc": "Cell structure, organelles & processes",               "url": "https://www.youtube.com/results?search_query=cell+biology+full+course+for+students",                   "tag": "Full Course"},
        {"icon": "🧬", "title": "Genetics & DNA Explained",       "desc": "Heredity, genes, DNA replication",                     "url": "https://www.youtube.com/results?search_query=genetics+DNA+replication+explained+biology",              "tag": "Genetics"},
        {"icon": "🫀", "title": "Human Body Systems",             "desc": "Digestive, respiratory, circulatory & more",           "url": "https://www.youtube.com/results?search_query=human+body+systems+biology+explained+for+students",       "tag": "Human Body"},
        {"icon": "🌿", "title": "Photosynthesis & Respiration",   "desc": "Plant biology & metabolic pathways",                   "url": "https://www.youtube.com/results?search_query=photosynthesis+cellular+respiration+explained+biology",    "tag": "Plants"},
    ],
    "Computer Science": [
        {"icon": "💻", "title": "Python for Beginners",           "desc": "Complete Python programming from scratch",             "url": "https://www.youtube.com/results?search_query=python+programming+full+course+beginners",                 "tag": "Programming"},
        {"icon": "🌐", "title": "Data Structures & Algorithms",   "desc": "Arrays, trees, sorting — with examples",               "url": "https://www.youtube.com/results?search_query=data+structures+algorithms+full+course",                  "tag": "DSA"},
        {"icon": "🖥️", "title": "How Computers Work",             "desc": "CPU, memory, OS fundamentals explained",               "url": "https://www.youtube.com/results?search_query=how+computers+work+CPU+memory+operating+system",           "tag": "Fundamentals"},
        {"icon": "🔐", "title": "Cybersecurity Basics",           "desc": "Networks, security & the internet",                    "url": "https://www.youtube.com/results?search_query=cybersecurity+basics+networking+fundamentals+explained",    "tag": "Security"},
    ],
    "English": [
        {"icon": "📝", "title": "English Grammar Mastery",        "desc": "Tenses, parts of speech, sentence structure",          "url": "https://www.youtube.com/results?search_query=english+grammar+full+course+beginners",                   "tag": "Grammar"},
        {"icon": "📚", "title": "Vocabulary Builder",             "desc": "1000+ words with meaning & usage",                    "url": "https://www.youtube.com/results?search_query=english+vocabulary+building+words+meaning+usage",          "tag": "Vocabulary"},
        {"icon": "🗣️", "title": "Spoken English Fluency",         "desc": "Speaking naturally with confidence",                   "url": "https://www.youtube.com/results?search_query=spoken+english+fluency+course+for+beginners",             "tag": "Speaking"},
        {"icon": "✍️",  "title": "Essay & Writing Skills",         "desc": "Writing structured essays & paragraphs",               "url": "https://www.youtube.com/results?search_query=english+essay+writing+skills+for+students",              "tag": "Writing"},
    ],
}

# ══════════════════════════════════════════════════════════════════════════════
# PRE-WRITTEN QUESTIONS  (used by default; refreshed by AI on demand)
# ══════════════════════════════════════════════════════════════════════════════
PRESET_QUESTIONS = {
    "History": {
        "Easy": [
            {"question": "Who was the first Prime Minister of independent India?", "options": {"A": "Mahatma Gandhi", "B": "Sardar Patel", "C": "Jawaharlal Nehru", "D": "B.R. Ambedkar"}, "answer": "C", "explanation": "Jawaharlal Nehru became India's first Prime Minister on 15 August 1947. He served until his death in May 1964."},
            {"question": "In which year did India gain independence from British rule?", "options": {"A": "1945", "B": "1946", "C": "1947", "D": "1948"}, "answer": "C", "explanation": "India gained independence on 15 August 1947 after decades of struggle. The Indian Independence Act was passed by the British Parliament in July 1947."},
            {"question": "Who built the Taj Mahal?", "options": {"A": "Akbar", "B": "Humayun", "C": "Aurangzeb", "D": "Shah Jahan"}, "answer": "D", "explanation": "Mughal Emperor Shah Jahan built the Taj Mahal in memory of his beloved wife Mumtaz Mahal. It was completed around 1653 AD."},
            {"question": "The Sepoy Mutiny (First War of Independence) took place in which year?", "options": {"A": "1847", "B": "1857", "C": "1867", "D": "1877"}, "answer": "B", "explanation": "The Sepoy Mutiny of 1857, also called India's First War of Independence, began in Meerut on 10 May 1857. It was a major revolt against British East India Company rule."},
            {"question": "Which country colonised India before independence?", "options": {"A": "France", "B": "Portugal", "C": "Netherlands", "D": "Britain"}, "answer": "D", "explanation": "Britain, through the British East India Company, gradually colonised India and by 1858 the British Crown took direct control. British rule in India is often called the 'Raj'."},
        ],
        "Medium": [
            {"question": "In which year was the Indian National Congress founded?", "options": {"A": "1875", "B": "1885", "C": "1895", "D": "1905"}, "answer": "B", "explanation": "The Indian National Congress was founded on 28 December 1885 in Bombay, with A.O. Hume as its founder. It became the principal political party leading the independence movement."},
            {"question": "The Partition of Bengal in 1905 was announced by which Viceroy?", "options": {"A": "Lord Dalhousie", "B": "Lord Curzon", "C": "Lord Mountbatten", "D": "Lord Wavell"}, "answer": "B", "explanation": "Lord Curzon, the Viceroy of India, announced the Partition of Bengal in 1905. The partition aroused intense nationalist feelings and led to the Swadeshi Movement."},
            {"question": "The Jallianwala Bagh massacre (1919) took place in which city?", "options": {"A": "Delhi", "B": "Lahore", "C": "Amritsar", "D": "Lucknow"}, "answer": "C", "explanation": "The Jallianwala Bagh massacre occurred on 13 April 1919 in Amritsar, Punjab. General Dyer ordered troops to fire on unarmed civilians, killing hundreds."},
            {"question": "Who wrote the book 'The Discovery of India'?", "options": {"A": "Mahatma Gandhi", "B": "Jawaharlal Nehru", "C": "Rabindranath Tagore", "D": "Sardar Patel"}, "answer": "B", "explanation": "Jawaharlal Nehru wrote 'The Discovery of India' while imprisoned at Ahmednagar Fort (1942-1945). The book explores India's history, culture, and philosophy."},
            {"question": "The Battle of Plassey (1757) was fought between the British and whom?", "options": {"A": "The Mughals", "B": "The Marathas", "C": "The Nawab of Bengal", "D": "The Sultan of Mysore"}, "answer": "C", "explanation": "The Battle of Plassey on 23 June 1757 was fought between the British East India Company and Siraj ud-Daulah, the Nawab of Bengal. The British victory laid the foundation of British rule in India."},
        ],
        "Hard": [
            {"question": "Which session of the Indian National Congress passed the resolution for complete independence (Purna Swaraj)?", "options": {"A": "Calcutta 1928", "B": "Lahore 1929", "C": "Karachi 1931", "D": "Lucknow 1936"}, "answer": "B", "explanation": "The Lahore session of the INC in December 1929, presided by Jawaharlal Nehru, declared Purna Swaraj (complete independence) as its goal. 26 January was chosen as Independence Day from 1930 onwards."},
            {"question": "The Simon Commission was boycotted by Indian leaders mainly because:", "options": {"A": "It recommended partition of India", "B": "It had no Indian members", "C": "It proposed new tax laws", "D": "It restricted electoral rights"}, "answer": "B", "explanation": "The Simon Commission (1928) consisted entirely of British members with no Indian representation. This was deeply insulting to Indians and led to widespread protests with the slogan 'Simon Go Back'."},
            {"question": "Who founded the Azad Hind Fauj (Indian National Army)?", "options": {"A": "Bhagat Singh", "B": "Bal Gangadhar Tilak", "C": "Subhas Chandra Bose", "D": "Lala Lajpat Rai"}, "answer": "C", "explanation": "Subhas Chandra Bose reorganised and led the Indian National Army (Azad Hind Fauj) during World War II. He aimed to liberate India from British rule with Japanese support."},
            {"question": "Which Act transferred governing power in India from the East India Company to the British Crown?", "options": {"A": "Regulating Act 1773", "B": "Charter Act 1853", "C": "Government of India Act 1858", "D": "Indian Councils Act 1861"}, "answer": "C", "explanation": "The Government of India Act 1858 was passed following the 1857 revolt. It dissolved the East India Company and transferred all powers to the British Crown, establishing direct Crown rule."},
            {"question": "The Treaty of Versailles (1919), which ended World War I, imposed heavy reparations on which country?", "options": {"A": "Austria", "B": "Germany", "C": "Ottoman Empire", "D": "Hungary"}, "answer": "B", "explanation": "The Treaty of Versailles placed full blame for WWI on Germany through the 'War Guilt Clause' (Article 231). Germany was required to pay massive reparations, which contributed to economic instability and the rise of Nazism."},
        ],
    },
    "Geography": {
        "Easy": [
            {"question": "What is the capital city of India?", "options": {"A": "Mumbai", "B": "Kolkata", "C": "New Delhi", "D": "Chennai"}, "answer": "C", "explanation": "New Delhi is the capital city of India and serves as the seat of all three branches of the Indian government. It was officially declared capital in 1911, replacing Calcutta."},
            {"question": "Which is the longest river in India?", "options": {"A": "Yamuna", "B": "Godavari", "C": "Brahmaputra", "D": "Ganga"}, "answer": "D", "explanation": "The Ganga (Ganges) is the longest river in India, stretching approximately 2,525 km. It originates from the Gangotri glacier in the Himalayas and flows into the Bay of Bengal."},
            {"question": "On which continent is the Sahara Desert located?", "options": {"A": "Asia", "B": "Australia", "C": "Africa", "D": "South America"}, "answer": "C", "explanation": "The Sahara is the world's largest hot desert, located across North Africa. It spans about 9 million square kilometres, covering much of North Africa."},
            {"question": "What is the capital of France?", "options": {"A": "Berlin", "B": "Madrid", "C": "Rome", "D": "Paris"}, "answer": "D", "explanation": "Paris is the capital and largest city of France, located along the Seine River. It is known as the 'City of Light' and is famous for landmarks like the Eiffel Tower."},
            {"question": "Which planet is closest to the Sun?", "options": {"A": "Venus", "B": "Earth", "C": "Mars", "D": "Mercury"}, "answer": "D", "explanation": "Mercury is the closest planet to the Sun in our solar system, orbiting at an average distance of about 57.9 million km. It completes one orbit around the Sun every 88 Earth days."},
        ],
        "Medium": [
            {"question": "What is the largest ocean on Earth by area?", "options": {"A": "Atlantic Ocean", "B": "Indian Ocean", "C": "Arctic Ocean", "D": "Pacific Ocean"}, "answer": "D", "explanation": "The Pacific Ocean is the largest and deepest ocean on Earth, covering about 165 million square kilometres. It accounts for approximately 46% of Earth's water surface area."},
            {"question": "What is the capital of Australia?", "options": {"A": "Sydney", "B": "Melbourne", "C": "Canberra", "D": "Perth"}, "answer": "C", "explanation": "Canberra is the capital city of Australia and home to the national government. It was purpose-built as a compromise between rivals Sydney and Melbourne, and was inaugurated as the capital in 1913."},
            {"question": "The Radcliffe Line forms the border between which two countries?", "options": {"A": "India and Nepal", "B": "India and China", "C": "India and Pakistan", "D": "India and Bangladesh"}, "answer": "C", "explanation": "The Radcliffe Line, drawn by Sir Cyril Radcliffe in 1947, forms the border between India and Pakistan. It was created during the partition of the Indian subcontinent."},
            {"question": "Which is the largest desert in the world by total area?", "options": {"A": "Sahara Desert", "B": "Arabian Desert", "C": "Gobi Desert", "D": "Antarctic Desert"}, "answer": "D", "explanation": "The Antarctic Desert is the world's largest desert with an area of about 14 million sq km. A desert is defined by low precipitation, and Antarctica receives less than 200mm of rain equivalent per year."},
            {"question": "The Strait of Malacca connects which two bodies of water?", "options": {"A": "Red Sea and Arabian Sea", "B": "South China Sea and Andaman Sea", "C": "Pacific and Indian Oceans", "D": "Java Sea and Indian Ocean"}, "answer": "B", "explanation": "The Strait of Malacca runs between the Malay Peninsula and Sumatra, connecting the South China Sea to the Andaman Sea. It is one of the world's most important shipping lanes."},
        ],
        "Hard": [
            {"question": "What is the latitude of the Tropic of Cancer?", "options": {"A": "0 degrees (Equator)", "B": "23.5 degrees N", "C": "66.5 degrees N", "D": "23.5 degrees S"}, "answer": "B", "explanation": "The Tropic of Cancer is at approximately 23.5 North latitude. It is the northernmost circle of latitude where the Sun can be directly overhead, which occurs at the June solstice."},
            {"question": "Which country has the greatest number of freshwater lakes in the world?", "options": {"A": "Russia", "B": "USA", "C": "Canada", "D": "Brazil"}, "answer": "C", "explanation": "Canada holds approximately 60% of the world's lakes, with an estimated 2 million lakes covering about 9% of its territory. This is largely a result of glaciation during the last Ice Age."},
            {"question": "What is the deepest lake in the world?", "options": {"A": "Lake Superior", "B": "Caspian Sea", "C": "Lake Titicaca", "D": "Lake Baikal"}, "answer": "D", "explanation": "Lake Baikal in Siberia, Russia, is the world's deepest lake at approximately 1,642 metres deep. It also holds about 20% of the world's unfrozen surface fresh water."},
            {"question": "Which river forms a major part of the border between the USA and Mexico?", "options": {"A": "Colorado River", "B": "Mississippi River", "C": "Rio Grande", "D": "Missouri River"}, "answer": "C", "explanation": "The Rio Grande forms the international border between the US state of Texas and the Mexican states of Chihuahua, Coahuila, Nuevo Leon and Tamaulipas. It flows approximately 3,057 km in total."},
            {"question": "The Mariana Trench, the deepest point on Earth, is located in which ocean?", "options": {"A": "Atlantic Ocean", "B": "Indian Ocean", "C": "Arctic Ocean", "D": "Pacific Ocean"}, "answer": "D", "explanation": "The Mariana Trench is located in the western Pacific Ocean and reaches a maximum depth of about 11,034 metres at a point called Challenger Deep. It is deeper than Mount Everest is tall."},
        ],
    },
    "Politics": {
        "Easy": [
            {"question": "Who is the constitutional head of the Republic of India?", "options": {"A": "Prime Minister", "B": "Chief Justice of India", "C": "President", "D": "Speaker of Lok Sabha"}, "answer": "C", "explanation": "The President of India is the constitutional head of state. However, in practice, executive power is exercised by the Prime Minister and the Council of Ministers, making it a parliamentary democracy."},
            {"question": "The Indian Constitution came into force on:", "options": {"A": "15 August 1947", "B": "26 November 1949", "C": "26 January 1950", "D": "2 October 1949"}, "answer": "C", "explanation": "The Constitution of India came into effect on 26 January 1950, which is celebrated as Republic Day. It was adopted by the Constituent Assembly on 26 November 1949."},
            {"question": "How many original articles did the Indian Constitution have?", "options": {"A": "256", "B": "350", "C": "395", "D": "448"}, "answer": "C", "explanation": "The original Indian Constitution had 395 articles, 22 parts, and 8 schedules. Today, due to amendments, it has grown to over 448 articles and 12 schedules."},
            {"question": "What does the Preamble of the Indian Constitution declare India to be?", "options": {"A": "A Federal Democratic Republic", "B": "A Parliamentary Democracy", "C": "A Sovereign Socialist Secular Democratic Republic", "D": "A Constitutional Monarchy"}, "answer": "C", "explanation": "The Preamble declares India to be a Sovereign, Socialist, Secular, Democratic Republic. The words 'Socialist' and 'Secular' were added by the 42nd Amendment in 1976."},
            {"question": "Which body has the power to amend the Indian Constitution?", "options": {"A": "Supreme Court", "B": "The President of India", "C": "Parliament", "D": "Lok Sabha alone"}, "answer": "C", "explanation": "Under Article 368, Parliament has the power to amend the Constitution. However, certain provisions require ratification by at least half of the state legislatures as well."},
        ],
        "Medium": [
            {"question": "The concept of Judicial Review in India is primarily borrowed from:", "options": {"A": "United Kingdom", "B": "United States of America", "C": "Canada", "D": "Australia"}, "answer": "B", "explanation": "The concept of Judicial Review, which allows courts to review legislation for constitutional validity, was borrowed from the USA. It was incorporated into the Indian Constitution to protect fundamental rights."},
            {"question": "Which Article of the Indian Constitution abolishes untouchability?", "options": {"A": "Article 14", "B": "Article 17", "C": "Article 19", "D": "Article 21"}, "answer": "B", "explanation": "Article 17 of the Indian Constitution abolishes untouchability and forbids its practice in any form. The Protection of Civil Rights Act 1955 enforces this constitutional provision."},
            {"question": "The 73rd Constitutional Amendment Act (1992) is related to:", "options": {"A": "Right to Education", "B": "Anti-defection Law", "C": "Panchayati Raj System", "D": "Reservation in Government Jobs"}, "answer": "C", "explanation": "The 73rd Amendment gave constitutional status to Panchayati Raj institutions (local self-government in rural areas). It added the 11th Schedule and introduced elections to these bodies."},
            {"question": "The word 'Secular' was added to the Preamble of the Indian Constitution by which Amendment?", "options": {"A": "44th Amendment", "B": "52nd Amendment", "C": "42nd Amendment", "D": "46th Amendment"}, "answer": "C", "explanation": "The 42nd Constitutional Amendment Act (1976), enacted during the Emergency, added both 'Socialist' and 'Secular' to the Preamble. This amendment is sometimes called the 'Mini-Constitution'."},
            {"question": "Who chaired the Drafting Committee of the Indian Constitution?", "options": {"A": "Jawaharlal Nehru", "B": "Rajendra Prasad", "C": "Sardar Patel", "D": "B.R. Ambedkar"}, "answer": "D", "explanation": "Dr. B.R. Ambedkar chaired the seven-member Drafting Committee of the Constituent Assembly. He is widely regarded as the principal architect of the Indian Constitution."},
        ],
        "Hard": [
            {"question": "Which Article of the Indian Constitution deals with the power to proclaim a National Emergency?", "options": {"A": "Article 352", "B": "Article 356", "C": "Article 360", "D": "Article 370"}, "answer": "A", "explanation": "Article 352 empowers the President to proclaim a National Emergency if the security of India is threatened by war, external aggression, or armed rebellion. Article 356 deals with State Emergency (President's Rule)."},
            {"question": "The landmark Kesavananda Bharati case (1973) established which constitutional doctrine?", "options": {"A": "Doctrine of Separation of Powers", "B": "Doctrine of Judicial Activism", "C": "Basic Structure Doctrine", "D": "Rule of Law Doctrine"}, "answer": "C", "explanation": "In Kesavananda Bharati v. State of Kerala (1973), the Supreme Court held that Parliament cannot amend the 'basic structure' of the Constitution. This doctrine limits parliamentary power to amend the Constitution."},
            {"question": "The Directive Principles of State Policy in the Indian Constitution are borrowed from which country's constitution?", "options": {"A": "USA", "B": "USSR", "C": "Canada", "D": "Ireland"}, "answer": "D", "explanation": "The Directive Principles of State Policy (Part IV, Articles 36-51) are borrowed from the Irish Constitution of 1937. They are non-justiciable but fundamental in governance."},
            {"question": "The anti-defection provisions in India are contained in which Schedule of the Constitution?", "options": {"A": "8th Schedule", "B": "9th Schedule", "C": "10th Schedule", "D": "12th Schedule"}, "answer": "C", "explanation": "The 10th Schedule, added by the 52nd Amendment (1985), contains the anti-defection law. It disqualifies members of Parliament or state legislatures who defect from their political party."},
            {"question": "Under which Article can the President of India refer a question of law or fact to the Supreme Court for its opinion?", "options": {"A": "Article 131", "B": "Article 136", "C": "Article 143", "D": "Article 148"}, "answer": "C", "explanation": "Article 143 grants the President the power to consult the Supreme Court by referring questions of law or public importance (Advisory Jurisdiction). The Supreme Court may or may not answer such a reference."},
        ],
    },
    "Biology": {
        "Easy": [
            {"question": "Which organelle is known as the 'powerhouse of the cell'?", "options": {"A": "Nucleus", "B": "Ribosome", "C": "Mitochondria", "D": "Cell Membrane"}, "answer": "C", "explanation": "The mitochondria produce ATP (adenosine triphosphate) through the process of cellular respiration, providing energy for cellular activities. This is why they are called the powerhouse of the cell."},
            {"question": "How many chromosomes does a normal human body cell have?", "options": {"A": "23", "B": "44", "C": "46", "D": "48"}, "answer": "C", "explanation": "Human body cells contain 46 chromosomes arranged in 23 pairs. Reproductive cells (sperm and eggs) contain only 23 chromosomes, combining to form 46 at fertilisation."},
            {"question": "What is the process by which plants make their own food using sunlight?", "options": {"A": "Respiration", "B": "Transpiration", "C": "Digestion", "D": "Photosynthesis"}, "answer": "D", "explanation": "Photosynthesis is the process where plants use sunlight, carbon dioxide, and water to produce glucose and oxygen. The reaction occurs in chloroplasts using the green pigment chlorophyll."},
            {"question": "Which is the largest organ of the human body?", "options": {"A": "Heart", "B": "Liver", "C": "Brain", "D": "Skin"}, "answer": "D", "explanation": "The skin is the largest organ of the human body, covering an area of about 1.5-2 square metres in adults. It acts as a protective barrier, regulates temperature, and contains sensory receptors."},
            {"question": "What determines a person's blood type (A, B, AB or O)?", "options": {"A": "Antibodies in plasma", "B": "Antigens on red blood cell surface", "C": "White blood cell count", "D": "Enzymes in blood"}, "answer": "B", "explanation": "Blood type is determined by specific antigens (proteins) present on the surface of red blood cells. The ABO blood grouping system and the Rh factor together determine a person's blood type."},
        ],
        "Medium": [
            {"question": "Which organelle is primarily responsible for protein synthesis?", "options": {"A": "Mitochondria", "B": "Nucleus", "C": "Ribosome", "D": "Golgi Apparatus"}, "answer": "C", "explanation": "Ribosomes are the sites of protein synthesis (translation) in the cell. They read messenger RNA (mRNA) sequences and assemble amino acids into polypeptide chains according to the genetic code."},
            {"question": "The modern science of genetics was pioneered by:", "options": {"A": "Charles Darwin", "B": "Gregor Mendel", "C": "Louis Pasteur", "D": "Robert Hooke"}, "answer": "B", "explanation": "Gregor Mendel, an Austrian monk, pioneered genetics through his experiments with pea plants in the 1860s. His work established the laws of inheritance, though it was not recognised until after his death."},
            {"question": "Which vitamin is synthesised by human skin on exposure to sunlight?", "options": {"A": "Vitamin A", "B": "Vitamin B12", "C": "Vitamin C", "D": "Vitamin D"}, "answer": "D", "explanation": "Vitamin D (calciferol) is produced in the skin when exposed to ultraviolet B (UVB) radiation from sunlight. It is essential for calcium absorption and bone health."},
            {"question": "Which part of the brain is responsible for balance and coordination of movement?", "options": {"A": "Cerebrum", "B": "Medulla Oblongata", "C": "Thalamus", "D": "Cerebellum"}, "answer": "D", "explanation": "The cerebellum, located at the back of the brain, coordinates voluntary movements and maintains balance and posture. Damage to the cerebellum results in poor coordination and unsteady movement."},
            {"question": "During which phase of the cell cycle does DNA replication occur?", "options": {"A": "G1 Phase", "B": "S Phase (Synthesis)", "C": "G2 Phase", "D": "M Phase (Mitosis)"}, "answer": "B", "explanation": "DNA replication occurs during the Synthesis (S) phase of the cell cycle interphase. During this phase, the cell duplicates its entire genome so that both daughter cells receive a complete copy."},
        ],
        "Hard": [
            {"question": "Which enzyme unwinds the DNA double helix during replication?", "options": {"A": "DNA Polymerase", "B": "DNA Ligase", "C": "Helicase", "D": "Primase"}, "answer": "C", "explanation": "Helicase is the enzyme that unwinds and separates the two strands of the DNA double helix at the replication fork by breaking hydrogen bonds between base pairs. This exposes the template strands for replication."},
            {"question": "Which metabolic pathway converts glucose into pyruvate in the cytoplasm?", "options": {"A": "Krebs Cycle", "B": "Calvin Cycle", "C": "Oxidative Phosphorylation", "D": "Glycolysis"}, "answer": "D", "explanation": "Glycolysis is the metabolic pathway that breaks down one molecule of glucose into two molecules of pyruvate, occurring in the cytoplasm. It produces a net gain of 2 ATP molecules and 2 NADH molecules."},
            {"question": "The lac operon model of gene regulation was proposed by:", "options": {"A": "Watson and Crick", "B": "Jacob and Monod", "C": "Beadle and Tatum", "D": "Avery, MacLeod and McCarty"}, "answer": "B", "explanation": "Francois Jacob and Jacques Monod proposed the lac operon model in 1961 to explain how gene expression is regulated in E. coli in response to lactose availability. They were awarded the Nobel Prize in 1965."},
            {"question": "Which type of immunity involves memory B and T cells for long-term protection?", "options": {"A": "Innate Immunity", "B": "Passive Immunity", "C": "Adaptive (Acquired) Immunity", "D": "Non-specific Immunity"}, "answer": "C", "explanation": "Adaptive immunity is characterised by specificity and memory. After an infection or vaccination, memory B and T cells persist and enable a faster, stronger response upon re-exposure to the same pathogen."},
            {"question": "The Hardy-Weinberg principle states that in a large, randomly mating population:", "options": {"A": "Natural selection always changes allele frequencies", "B": "Mutation rates increase over time", "C": "Allele and genotype frequencies remain constant over generations", "D": "Predator-prey ratios stabilise"}, "answer": "C", "explanation": "The Hardy-Weinberg equilibrium states that allele and genotype frequencies in a population remain stable from generation to generation in the absence of disturbing factors like mutation, selection, and genetic drift."},
        ],
    },
    "Computer Science": {
        "Easy": [
            {"question": "What does CPU stand for?", "options": {"A": "Computer Personal Unit", "B": "Central Processing Unit", "C": "Central Program Utility", "D": "Core Processing Unit"}, "answer": "B", "explanation": "CPU stands for Central Processing Unit, which is the primary component of a computer that executes instructions. It performs arithmetic, logic, control, and input/output operations."},
            {"question": "Which programming language category is closest to human-readable language?", "options": {"A": "Machine language", "B": "Assembly language", "C": "High-level language", "D": "Binary code"}, "answer": "C", "explanation": "High-level programming languages (like Python, Java, C++) use syntax closer to natural human language and are machine-independent. They must be compiled or interpreted into machine code for execution."},
            {"question": "What does HTML stand for?", "options": {"A": "High Transfer Markup Language", "B": "HyperText Management Language", "C": "HyperText Markup Language", "D": "Home Tool Markup Language"}, "answer": "C", "explanation": "HTML (HyperText Markup Language) is the standard markup language used to create web pages. It defines the structure and content of a webpage using elements represented by tags."},
            {"question": "What is the binary representation of the decimal number 10?", "options": {"A": "1000", "B": "0110", "C": "1100", "D": "1010"}, "answer": "D", "explanation": "Decimal 10 in binary is 1010. This is calculated as: 1x8 + 0x4 + 1x2 + 0x1 = 10. Binary uses only two digits (0 and 1) and each position represents a power of 2."},
            {"question": "What is the output of the Python expression: 2 ** 3?", "options": {"A": "6", "B": "5", "C": "9", "D": "8"}, "answer": "D", "explanation": "In Python, ** is the exponentiation operator. So 2 ** 3 means 2 raised to the power 3, which equals 2 x 2 x 2 = 8."},
        ],
        "Medium": [
            {"question": "What is the time complexity of binary search on a sorted array?", "options": {"A": "O(n)", "B": "O(n squared)", "C": "O(log n)", "D": "O(1)"}, "answer": "C", "explanation": "Binary search has a time complexity of O(log n) because it repeatedly divides the search space in half. With each comparison, the algorithm eliminates half the remaining elements."},
            {"question": "Which data structure follows the LIFO (Last In, First Out) principle?", "options": {"A": "Queue", "B": "Array", "C": "Linked List", "D": "Stack"}, "answer": "D", "explanation": "A stack follows the LIFO principle, meaning the last element added is the first to be removed. It supports two main operations: push (add to top) and pop (remove from top)."},
            {"question": "What does SQL stand for?", "options": {"A": "Simple Query Language", "B": "Structured Query Language", "C": "Standard Question Logic", "D": "Sequential Query Language"}, "answer": "B", "explanation": "SQL (Structured Query Language) is a domain-specific language used to manage and query relational databases. It supports operations like SELECT, INSERT, UPDATE, DELETE, and more."},
            {"question": "Which HTTP method is primarily used to send data to a server (e.g., form submission)?", "options": {"A": "GET", "B": "POST", "C": "PUT", "D": "DELETE"}, "answer": "B", "explanation": "The HTTP POST method sends data to the server in the request body, commonly used for form submissions or creating resources. Unlike GET, POST requests are not cached and not stored in browser history."},
            {"question": "What is the primary role of a compiler in programming?", "options": {"A": "Runs programs directly line by line", "B": "Manages computer memory allocation", "C": "Translates high-level source code to machine code", "D": "Connects programs to the internet"}, "answer": "C", "explanation": "A compiler translates the entire source code written in a high-level language into machine code (binary) before execution. Unlike an interpreter, a compiler processes the whole program at once."},
        ],
        "Hard": [
            {"question": "What is the worst-case time complexity of the QuickSort algorithm?", "options": {"A": "O(n log n)", "B": "O(n)", "C": "O(log n)", "D": "O(n squared)"}, "answer": "D", "explanation": "QuickSort has a worst-case time complexity of O(n squared), which occurs when the pivot is always chosen as the smallest or largest element. Its average case is O(n log n)."},
            {"question": "In networking, what does CIDR stand for?", "options": {"A": "Circuit-based Internet Data Routing", "B": "Common Interface Domain Registry", "C": "Classless Inter-Domain Routing", "D": "Centralized Internet Data Relay"}, "answer": "C", "explanation": "CIDR (Classless Inter-Domain Routing) is a method for allocating IP addresses and routing. It replaced the old class-based system and uses prefix notation (e.g., 192.168.1.0/24) to specify network and host portions."},
            {"question": "Which design pattern ensures that only one instance of a class is created throughout an application?", "options": {"A": "Factory Pattern", "B": "Observer Pattern", "C": "Singleton Pattern", "D": "Decorator Pattern"}, "answer": "C", "explanation": "The Singleton pattern restricts the instantiation of a class to a single object and provides a global point of access to it. It is commonly used for database connections, logging, or configuration management."},
            {"question": "In relational databases, what does ACID stand for?", "options": {"A": "Access, Control, Integrity, Data", "B": "Atomic, Compound, Index, Domain", "C": "Atomicity, Consistency, Isolation, Durability", "D": "Algorithm, Cache, Input, Dynamic"}, "answer": "C", "explanation": "ACID is a set of properties that guarantee database transactions are processed reliably: Atomicity (all or nothing), Consistency (valid state), Isolation (concurrent transactions don't interfere), Durability (committed data persists)."},
            {"question": "What is the primary purpose of a mutex in concurrent programming?", "options": {"A": "To increase processing speed", "B": "To automatically prevent all deadlocks", "C": "To manage creation of new threads", "D": "To ensure mutual exclusion when accessing shared resources"}, "answer": "D", "explanation": "A mutex (mutual exclusion object) ensures that only one thread can access a shared resource at a time. When a thread acquires the mutex lock, other threads must wait, preventing race conditions."},
        ],
    },
    "English": {
        "Easy": [
            {"question": "Which of the following words is a noun?", "options": {"A": "Run", "B": "Quickly", "C": "Beautiful", "D": "Happiness"}, "answer": "D", "explanation": "A noun is a word that names a person, place, thing, or abstract idea. 'Happiness' is an abstract noun. 'Run' is a verb, 'quickly' is an adverb, and 'beautiful' is an adjective."},
            {"question": "What is the correct plural form of the word 'child'?", "options": {"A": "Childs", "B": "Childes", "C": "Childrens", "D": "Children"}, "answer": "D", "explanation": "The plural of 'child' is 'children', which is an irregular plural form. Unlike regular nouns that simply add -s or -es, 'children' is formed from the Old English word 'cildru'."},
            {"question": "Identify the sentence written in the passive voice:", "options": {"A": "She writes a letter every day.", "B": "They are writing letters now.", "C": "The letter was written by her.", "D": "Write the letter now!"}, "answer": "C", "explanation": "In the passive voice, the subject receives the action rather than performing it. 'The letter was written by her' — the subject 'letter' is acted upon, making it passive."},
            {"question": "Which word is a synonym of 'happy'?", "options": {"A": "Sad", "B": "Tired", "C": "Angry", "D": "Joyful"}, "answer": "D", "explanation": "A synonym is a word with the same or similar meaning. 'Joyful' means feeling great happiness and delight, making it the closest synonym to 'happy' among the options."},
            {"question": "In the sentence 'The tall boy ran fast', which word is an adjective?", "options": {"A": "boy", "B": "ran", "C": "fast", "D": "tall"}, "answer": "D", "explanation": "An adjective modifies or describes a noun. In this sentence, 'tall' describes the noun 'boy', making it an adjective. 'Fast' here is an adverb modifying the verb 'ran'."},
        ],
        "Medium": [
            {"question": "Which figure of speech is used in the phrase 'The wind whispered through the trees'?", "options": {"A": "Simile", "B": "Metaphor", "C": "Hyperbole", "D": "Personification"}, "answer": "D", "explanation": "Personification attributes human characteristics to non-human things. Saying the wind 'whispered' gives it a human quality. A simile compares using 'like/as', a metaphor directly equates two things."},
            {"question": "What is the antonym of 'benevolent'?", "options": {"A": "Kind", "B": "Generous", "C": "Malevolent", "D": "Charitable"}, "answer": "C", "explanation": "'Benevolent' means well-meaning and kindly. Its antonym is 'malevolent', which means having or showing a wish to do evil to others. Both words share the Latin root 'volent' (wishing)."},
            {"question": "In which tense is the sentence: 'She has been working here for five years'?", "options": {"A": "Simple Present", "B": "Present Perfect", "C": "Past Perfect Continuous", "D": "Present Perfect Continuous"}, "answer": "D", "explanation": "The Present Perfect Continuous tense is used for actions that started in the past and continue up to now. It is formed with 'have/has been + present participle (verb+ing)'."},
            {"question": "What does the word 'ubiquitous' mean?", "options": {"A": "Extremely rare", "B": "Outdated or old-fashioned", "C": "Unique and one of a kind", "D": "Present or appearing everywhere"}, "answer": "D", "explanation": "'Ubiquitous' comes from Latin 'ubique' meaning 'everywhere'. It describes something that seems to appear everywhere simultaneously, for example: 'Smartphones have become ubiquitous in modern life.'"},
            {"question": "What is a 'gerund' in English grammar?", "options": {"A": "A verb used as an adjective", "B": "An adverb that modifies a noun", "C": "A noun formed from a verb by adding -ing", "D": "A conjunction joining two clauses"}, "answer": "C", "explanation": "A gerund is the -ing form of a verb used as a noun. For example, in 'Swimming is good exercise', 'swimming' functions as the subject noun. Gerunds can serve as subjects, objects, or complements."},
        ],
        "Hard": [
            {"question": "Which sentence is grammatically correct?", "options": {"A": "Each of the students have submitted their work.", "B": "Each students has submitted their work.", "C": "Every students have submitted work.", "D": "Each of the students has submitted their work."}, "answer": "D", "explanation": "'Each' is an indefinite pronoun that takes a singular verb. Therefore, 'Each of the students has submitted their work' is correct. The plural noun 'students' in the prepositional phrase does not affect subject-verb agreement."},
            {"question": "The rhetorical device where the last word or phrase of one clause becomes the first of the next is called:", "options": {"A": "Anaphora", "B": "Epistrophe", "C": "Chiasmus", "D": "Anadiplosis"}, "answer": "D", "explanation": "Anadiplosis involves repeating the last word of one clause at the start of the next, e.g., 'Fear leads to anger. Anger leads to hate.' Anaphora is repetition at the beginning; epistrophe at the end."},
            {"question": "Which sentence contains a dangling modifier?", "options": {"A": "Walking through the park, she saw the flowers.", "B": "After reading the book, he wrote a review.", "C": "Singing loudly, the child played in the yard.", "D": "Having finished dinner, the table was cleared."}, "answer": "D", "explanation": "A dangling modifier is a word or phrase that modifies a word not clearly stated in the sentence. In option D, 'Having finished dinner' implies the table finished dinner. It should read: 'Having finished dinner, they cleared the table.'"},
            {"question": "What does the word 'prolix' mean?", "options": {"A": "Brief and to the point", "B": "Extremely precise and accurate", "C": "Using too many words; long-winded", "D": "Cryptic and difficult to understand"}, "answer": "C", "explanation": "'Prolix' (from Latin 'prolixus', meaning 'extended') describes speech or writing that uses too many words and is tediously long. Its antonym is 'concise' or 'succinct'."},
            {"question": "In grammar, a 'pleonasm' refers to:", "options": {"A": "A word that modifies a verb", "B": "A form of indirect reported speech", "C": "A type of conditional clause structure", "D": "The use of more words than necessary to express an idea"}, "answer": "D", "explanation": "A pleonasm is the use of redundant words that add no meaning, such as 'free gift', 'past history', or 'advance warning'. While sometimes considered poor style, pleonasms are occasionally used for emphasis."},
        ],
    },
}

# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def valid_email(e): return bool(re.match(r"^[\w\.\+\-]+@[\w\-]+\.[a-zA-Z]{2,}$", e.strip()))
def valid_pw(p): return len(p) >= 6

def initials(name):
    parts = re.split(r"[.\-_ ]", name.strip())
    return "".join(p[0].upper() for p in parts if p)[:2] or "U"

def get_badge_info(xp):
    if xp >= 50: return "👑 Master Badge", "#8b5cf6", "You are an elite intellect! A true BrainBlitz legend."
    elif xp >= 40: return "🦸 Heroic Badge", "#ef4444", "A spectacular and brave performance!"
    elif xp >= 30: return "🥇 Gold Badge", "#eab308", "You're shining brightly at the top!"
    elif xp >= 20: return "🥈 Silver Badge", "#94a3b8", "Solid, consistent, and highly impressive!"
    elif xp >= 10: return "🥉 Bronze Badge", "#d97706", "A great start, keep climbing the ranks!"
    else: return "🌱 Beginner Badge", "#10b981", "Every master was once a beginner. Keep learning!"

def full_reset():
    for k in list(st.session_state.keys()):
        del st.session_state[k]

def quiz_reset():
    for k in ["question_index", "score", "wrong_answers", "start_time", "current_xp", "current_questions"]:
        st.session_state.pop(k, None)
    radio_keys = [k for k in st.session_state if isinstance(k, str) and re.match(r'^q_\d+$', k)]
    for k in radio_keys:
        del st.session_state[k]
def _call_api(api_client, model, prompt, max_tokens=MAX_TOKENS):
    """Call a single API client and return parsed JSON, or raise on failure."""
    chat_completion = api_client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Reply with raw JSON only. No extra text, no markdown, no code fences."},
            {"role": "user",   "content": prompt},
        ],
        max_tokens=max_tokens,
        temperature=0.3,
    )
    text = chat_completion.choices[0].message.content.strip()
    text = re.sub(r"\s*```$", "", text)
    return json.loads(text.strip())


def refresh_subject_questions(subj):
    """
    Call the API to generate NEW questions for all 3 difficulties of a subject.
    Stores results in session_state as q_cache_{subj}_{difficulty}.
    Returns True on success, False on failure.
    """
    prompt = (
        f"Generate exactly 5 MCQ questions for the subject '{subj}' at Easy difficulty, "
        f"5 at Medium difficulty, and 5 at Hard difficulty. "
        "Return ONLY a raw JSON object (no markdown, no code fences) in this exact format:\n"
        "{\"Easy\": [...], \"Medium\": [...], \"Hard\": [...]}\n"
        "Each question object must follow this structure:\n"
        "{\"question\": \"...\", \"options\": {\"A\": \"...\", \"B\": \"...\", \"C\": \"...\", \"D\": \"...\"}, "
        "\"answer\": \"A\", \"explanation\": \"2 sentences max.\"}"
    )

    result = None

    if groq_client:
        try:
            result = _call_api(groq_client, GROK_MODEL, prompt, max_tokens=2800)
        except Exception:
            pass

    if result is None and openrouter_client:
        try:
            result = _call_api(openrouter_client, OPENROUTER_MODEL, prompt, max_tokens=2800)
        except Exception:
            return False

    if result is None:
        return False

    stored = 0
    for diff in ["Easy", "Medium", "Hard"]:
        if diff in result and isinstance(result[diff], list) and len(result[diff]) > 0:
            st.session_state[f"q_cache_{subj}_{diff}"] = result[diff]
            stored += 1

    return stored > 0


def get_ai_study_tip(subj, diff, score, total):
    """Use the AI API to generate a personalised study tip for the result page."""
    pct = int((score / total) * 100) if total > 0 else 0
    prompt = (
        f"A student just completed a {diff}-difficulty quiz on {subj} and scored {score}/{total} ({pct}%).\n"
        "Write a SHORT, encouraging, personalised study tip (3-4 sentences max). "
        "Mention one specific concept or area from this subject they should focus on next. "
        "Keep it warm, motivating, and actionable. No bullet points, just flowing text."
    )
    client = groq_client or openrouter_client
    model  = GROK_MODEL if groq_client else OPENROUTER_MODEL
    if client is None:
        return None
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.8,
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        return None


def _shuffle_options(q):
    """
    Randomly reassign A/B/C/D labels to the option values so the correct
    answer is never biased to a particular letter.  Updates q["answer"] and
    the letter reference in q["explanation"] to match the new assignment.
    """
    import random as _random, re as _re3

    opts      = q["options"]
    ans_letter = q["answer"]
    ans_value  = opts[ans_letter]

    values = list(opts.values())
    _random.shuffle(values)

    letters = ["A", "B", "C", "D"]
    new_opts = dict(zip(letters, values))

    # Find which letter now holds the correct value
    new_ans = next(l for l, v in new_opts.items() if v == ans_value)

    # Update explanation letter reference (e.g. "answer is C" → "answer is B")
    expl = q.get("explanation", "")
    expl = _re3.sub(
        r"((?:correct )?answer is\s+)[A-D]",
        lambda m: m.group(1) + new_ans,
        expl, flags=_re3.IGNORECASE
    )

    q["options"]      = new_opts
    q["answer"]       = new_ans
    q["explanation"]  = expl
    return q


def _deduplicate_options(q):
    """
    Detect duplicate option values (the A==C bug) and replace them with
    clearly distinct placeholders so the question is still usable.

    Key rule: ALWAYS keep the answer letter's value intact.
    Any other letter that duplicates the answer letter's value is replaced.
    If two NON-answer letters duplicate each other, replace the later one.
    Returns the fixed question, or None if it cannot be salvaged.
    """
    import random as _random2

    opts = q["options"]
    ans  = q["answer"]

    placeholders = [
        "None of the above", "All of the above",
        "Cannot be determined", "Insufficient information",
        "Not applicable", "Other"
    ]
    _random2.shuffle(placeholders)

    # Build a canonical mapping: value → the ONE letter that should keep it.
    # The answer letter always wins; for duplicates among wrong options,
    # the first occurrence wins.
    keep = {}   # normalised_value → letter to keep
    replace = []  # letters that must be replaced

    # Process answer letter first so it always wins
    ans_val_norm = opts[ans].strip().lower()
    keep[ans_val_norm] = ans

    for letter in ["A", "B", "C", "D"]:
        if letter == ans:
            continue
        val_norm = opts[letter].strip().lower()
        if val_norm in keep:
            replace.append(letter)   # duplicate — must be replaced
        else:
            keep[val_norm] = letter

    if not replace:
        return q   # no duplicates

    # Collect values already legitimately used so placeholders are truly distinct
    used_vals = {opts[l].strip().lower() for l in ["A", "B", "C", "D"] if l not in replace}
    ph_iter = iter(p for p in placeholders if p.strip().lower() not in used_vals)

    for letter in replace:
        try:
            opts[letter] = next(ph_iter)
        except StopIteration:
            return None   # ran out of placeholders — drop the question

    q["options"] = opts
    return q


def _validate_questions(questions):
    """
    Full pipeline per question:
      1. Structural check (A-D present, answer letter valid)
      2. Deduplicate options  (fix A==C bug)
      3. Repair answer/explanation mismatch
      4. Shuffle option labels  (eliminate letter bias)
    """
    valid = []
    for q in questions:
        try:
            opts = q.get("options", {})
            ans  = q.get("answer", "").strip().upper()
            if ans not in ("A", "B", "C", "D"):
                continue
            if not all(k in opts for k in ("A", "B", "C", "D")):
                continue
            q["answer"] = ans

            # Step 2 — remove duplicate option values
            q = _deduplicate_options(q)
            if q is None:
                continue   # unsalvageable, skip

            # Step 3 — fix answer/explanation letter mismatch
            q = _repair_question(q)

            # Step 4 — shuffle labels so correct answer isn't always C
            q = _shuffle_options(q)

            valid.append(q)
        except Exception:
            continue
    return valid


def _repair_question(q):
    """
    Detect and fix the AI bug where options[answer] does not match the correct
    value described in the explanation.

    Strategy A — numeric: scan explanation for '= 9', find which option holds 9.
    Strategy B — text:    parse 'correct answer is C - VALUE', find VALUE in options.
    """
    import re as _re2

    ans  = q["answer"]
    opts = q["options"]
    expl = q.get("explanation", "")

    # Strategy A: numeric equality  (e.g. "9 + 0 = 9")
    num_match = _re2.search(r"=\s*(-?\d+(?:\.\d+)?)", expl)
    if num_match:
        stated_num  = num_match.group(1).strip()
        current_val = opts.get(ans, "").strip()
        if current_val != stated_num:
            for letter, opt_val in opts.items():
                if opt_val.strip() == stated_num:
                    q["answer"] = letter
                    q["explanation"] = _re2.sub(
                        r"((?:correct )?answer is\s+)[A-D]",
                        lambda m: m.group(1) + letter,
                        expl, flags=_re2.IGNORECASE
                    )
                    return q

    # Strategy B: "correct answer is X - VALUE" or "correct answer is X — VALUE"
    m = _re2.search(
        r"correct answer is\s+([A-D])\s*[\u2014\-:\u2013]\s*([^,\.]+)",
        expl, _re2.IGNORECASE
    )
    if m:
        stated_letter = m.group(1).upper()
        stated_val    = m.group(2).strip().rstrip(".,;")
        if stated_letter in opts:
            if opts[stated_letter].strip().lower() == stated_val.lower():
                if stated_letter != ans:
                    q["answer"] = stated_letter
                return q
            else:
                for letter, opt_val in opts.items():
                    if opt_val.strip().lower() == stated_val.lower():
                        q["answer"] = letter
                        q["explanation"] = _re2.sub(
                            r"(correct answer is\s+)[A-D]",
                            lambda m2: m2.group(1) + letter,
                            expl, flags=_re2.IGNORECASE
                        )
                        return q

    return q  # best-effort: unchanged


def generate_custom_questions(subj_name, topic):
    """
    AI generates 5 Easy + 5 Medium + 5 Hard MCQs for a user-defined subject & topic.
    Cache key: q_cache_CUSTOM_{subj_name}_{topic}
    Returns True on success, False on failure.
    """
    cache_key_prefix = f"q_cache_CUSTOM_{subj_name}_{topic}"
    prompt = (
        f"Generate exactly 5 multiple-choice questions (MCQs) about '{topic}' "
        f"in the subject '{subj_name}' at Easy difficulty, "
        "5 at Medium difficulty, and 5 at Hard difficulty.\n\n"
        "RULES (follow exactly):\n"
        "  1. Every question must have exactly 4 options: A, B, C, D.\n"
        "  2. ALL FOUR OPTION VALUES MUST BE DIFFERENT — never repeat a value.\n"
        "  3. Decide the correct answer value first, place it under any letter.\n"
        "  4. The other 3 letters get distinct WRONG values.\n"
        "  5. Set 'answer' to whichever letter holds the correct value.\n"
        "  6. Vary which letter is correct — use A, B, C, D roughly equally.\n"
        "  7. Explanation: 'The correct answer is [letter] - [value], because [reason].'\n\n"
        "Return ONLY raw JSON (no markdown, no fences):\n"
        "{\"Easy\": [...], \"Medium\": [...], \"Hard\": [...]}\n\n"
        "Question format:\n"
        "{\"question\": \"...\", \"options\": {\"A\": \"...\", \"B\": \"...\", "
        "\"C\": \"...\", \"D\": \"...\"}, \"answer\": \"A_OR_B_OR_C_OR_D\", "
        "\"explanation\": \"The correct answer is [letter] - [value], because [reason].\"}\n\n"
        "EXAMPLES showing variety of correct-answer letters:\n"
        "{\"question\": \"What is 3+1?\", "
        "\"options\": {\"A\": \"3\", \"B\": \"4\", \"C\": \"5\", \"D\": \"6\"}, "
        "\"answer\": \"B\", "
        "\"explanation\": \"The correct answer is B - 4, because 3+1=4.\"}\n"
        "{\"question\": \"Capital of France?\", "
        "\"options\": {\"A\": \"Paris\", \"B\": \"Berlin\", \"C\": \"Rome\", \"D\": \"Madrid\"}, "
        "\"answer\": \"A\", "
        "\"explanation\": \"The correct answer is A - Paris, because Paris is France's capital.\"}\n"
        "{\"question\": \"What is 10-3?\", "
        "\"options\": {\"A\": \"6\", \"B\": \"8\", \"C\": \"9\", \"D\": \"7\"}, "
        "\"answer\": \"D\", "
        "\"explanation\": \"The correct answer is D - 7, because 10-3=7.\"}"
    )

    result = None
    if groq_client:
        try:
            result = _call_api(groq_client, GROK_MODEL, prompt, max_tokens=2800)
        except Exception:
            pass

    if result is None and openrouter_client:
        try:
            result = _call_api(openrouter_client, OPENROUTER_MODEL, prompt, max_tokens=2800)
        except Exception:
            return False

    if result is None:
        return False

    stored = 0
    for diff in ["Easy", "Medium", "Hard"]:
        if diff in result and isinstance(result[diff], list) and len(result[diff]) > 0:
            validated = _validate_questions(result[diff])
            if validated:
                st.session_state[f"{cache_key_prefix}_{diff}"] = validated
                stored += 1

    return stored > 0


def generate_custom_yt_resources(subj_name, topic):
    """
    Use AI to generate 4 YouTube search resource cards for a custom subject+topic.
    Returns a list of dicts matching the YOUTUBE_RESOURCES format, or [].
    """
    prompt = (
        f"Generate exactly 4 YouTube study resource cards for the subject '{subj_name}' and topic '{topic}'.\n"
        "Return ONLY a raw JSON array (no markdown, no code fences) like this:\n"
        "[{\"icon\": \"📘\", \"title\": \"Short card title (max 5 words)\", "
        "\"desc\": \"One sentence description\", "
        "\"url\": \"https://www.youtube.com/results?search_query=relevant+search+terms\", "
        "\"tag\": \"Short Tag\"}]\n"
        "Make the search_query URL-encoded with + between words. "
        "Use 4 different learning angles: full course, beginner tutorial, exam prep, and advanced deep-dive."
    )
    client = groq_client or openrouter_client
    model  = GROK_MODEL if groq_client else OPENROUTER_MODEL
    if client is None:
        return []
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Reply with raw JSON only. No markdown, no code fences, no extra text."},
                {"role": "user",   "content": prompt},
            ],
            max_tokens=600,
            temperature=0.4,
        )
        text = resp.choices[0].message.content.strip()
        text = re.sub(r"```[a-z]*", "", text).replace("```", "").strip()
        cards = json.loads(text)
        if isinstance(cards, list) and len(cards) > 0:
            return cards[:4]
    except Exception:
        pass
    return []


def start_custom_quiz(subj_name, topic, difficulty, timer_sec):
    """Start a quiz using custom AI-generated questions."""
    cache_key = f"q_cache_CUSTOM_{subj_name}_{topic}_{difficulty}"
    if cache_key not in st.session_state:
        return False
    questions = st.session_state[cache_key]
    display_name = f"{subj_name} — {topic}"

    # Register dynamically into SUBJECT_DATA AND persist in session_state so
    # it survives Streamlit reruns (module-level dicts reset every run)
    entry = {"icon": "✏️", "desc": f"Custom: {topic}"}
    SUBJECT_DATA[display_name] = entry
    st.session_state[f"custom_subj_entry_{display_name}"] = entry

    st.session_state.subject      = display_name
    st.session_state.difficulty   = difficulty
    st.session_state.timer_seconds = timer_sec

    quiz_reset()
    st.session_state.current_questions = questions
    st.session_state.question_index    = 0
    st.session_state.score             = 0
    st.session_state.current_xp        = 0
    st.session_state.wrong_answers     = []
    st.session_state.start_time        = time.time()
    st.session_state.page              = "quiz"
    st.rerun()


def start_quiz(subj, difficulty, timer_sec):
    """Start the quiz — instant, no API call made here."""
    st.session_state.subject = subj
    st.session_state.difficulty = difficulty
    st.session_state.timer_seconds = timer_sec

    cache_key = f"q_cache_{subj}_{difficulty}"
    if cache_key in st.session_state:
        questions = st.session_state[cache_key]
    elif subj in PRESET_QUESTIONS:
        questions = PRESET_QUESTIONS[subj][difficulty]
    else:
        st.error("❌ No questions found for this subject. Please generate them first.")
        return

    quiz_reset()
    st.session_state.current_questions = questions
    st.session_state.question_index = 0
    st.session_state.score = 0
    st.session_state.current_xp = 0
    st.session_state.wrong_answers = []
    st.session_state.start_time = time.time()
    st.session_state.page = "quiz"
    st.rerun()


# ── UI components ──────────────────────────────────────────────────────────
def render_brand():
    st.markdown('<div class="brand-wrap"><span class="brand-logo">BrainBlitz</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-tag">Personalised Knowledge Challenge</div>', unsafe_allow_html=True)

def render_steps(current):
    labels = ["Login", "Subject", "Quiz", "Result"]
    icons  = ["🔐", "📚", "⚡", "🏆"]
    html   = '<div class="stepbar">'
    for i, (lbl, icon) in enumerate(zip(labels, icons)):
        cls = "done" if i < current else ("active" if i == current else "idle")
        html += f'<div class="step-item"><div class="step-circle {cls}">{icon}</div><div class="step-label {cls}">{lbl}</div></div>'
        if i < len(labels) - 1:
            lc = "done" if i < current else ""
            html += f'<div class="step-line {lc}"></div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

def render_badge():
    name  = st.session_state.get("user_name", "User")
    email = st.session_state.get("email", "")
    xp    = st.session_state.get("total_xp", 0)
    av    = initials(name)

    badge_name, badge_col, _ = get_badge_info(xp)

    subj = st.session_state.get("subject", "")
    diff = st.session_state.get("difficulty", "")

    subj_tag = ""
    if subj and diff:
        icon     = SUBJECT_DATA.get(subj, {"icon": "✏️", "desc": "Custom Quiz"})["icon"]
        subj_tag = f'&nbsp;·&nbsp;<span style="color:#a855f7;font-size:11px;font-weight:700">{icon} {subj} ({diff})</span>'

    st.markdown(f'''
    <div class="ubadge">
        <div class="uavatar">{av}</div>
        <div style="flex:1">
            <div class="uname">{name}{subj_tag}</div>
            <div class="uemail">{email}</div>
        </div>
        <div style="text-align:right">
            <div class="uxp" style="color:{badge_col};">{badge_name}</div>
            <div class="uxp">{xp} Total XP</div>
        </div>
    </div>''', unsafe_allow_html=True)


# ── Init session state ──────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "login"
if "total_xp" not in st.session_state:
    st.session_state.total_xp = 0

# ── Restore any custom subjects into SUBJECT_DATA on every rerun ─────────────
# (module-level dicts reset on each Streamlit rerun; session_state persists)
for _key, _val in list(st.session_state.items()):
    if isinstance(_key, str) and _key.startswith("custom_subj_entry_"):
        _display_name = _key[len("custom_subj_entry_"):]
        if _display_name not in SUBJECT_DATA:
            SUBJECT_DATA[_display_name] = _val


# ══════════════════════════════════════════════════════════════════════════════
# PAGE — LOGIN
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "login":
    render_brand()
    render_steps(0)

    # ── Test API button — uses cached results so it never re-calls the API ─
    st.markdown('<div class="test-api-wrap">', unsafe_allow_html=True)
    if st.button("🔌 Test APIs", key="test_api_btn"):
        # Only test if results not already cached in this session
        st.session_state._api_test_requested = True

    # Run tests in a fragment so only this section rerenders
    if st.session_state.get("_api_test_requested"):
        col1, col2 = st.columns(2)
        with col1:
            if groq_client is None:
                st.error("❌ Groq — Missing API Key")
            elif st.session_state.get("_groq_ok") is not None:
                if st.session_state["_groq_ok"]:
                    st.success("✅ Groq — OK")
                else:
                    st.error(f"❌ Groq — {st.session_state.get('_groq_err','Error')}")
            else:
                with st.spinner("Testing Groq…"):
                    try:
                        groq_client.chat.completions.create(
                            model=GROK_MODEL,
                            messages=[{"role": "user", "content": "Hi"}],
                            max_tokens=5, temperature=0
                        )
                        st.session_state["_groq_ok"] = True
                        st.success("✅ Groq — OK")
                    except Exception as e:
                        st.session_state["_groq_ok"] = False
                        st.session_state["_groq_err"] = str(e)
                        st.error(f"❌ Groq — {e}")
        with col2:
            if openrouter_client is None:
                st.error("❌ OpenRouter — Missing API Key")
            elif st.session_state.get("_or_ok") is not None:
                if st.session_state["_or_ok"]:
                    st.success("✅ OpenRouter — OK")
                else:
                    st.error(f"❌ OpenRouter — {st.session_state.get('_or_err','Error')}")
            else:
                with st.spinner("Testing OpenRouter…"):
                    try:
                        openrouter_client.chat.completions.create(
                            model=OPENROUTER_MODEL,
                            messages=[{"role": "user", "content": "Hi"}],
                            max_tokens=5, temperature=0
                        )
                        st.session_state["_or_ok"] = True
                        st.success("✅ OpenRouter — OK")
                    except Exception as e:
                        st.session_state["_or_ok"] = False
                        st.session_state["_or_err"] = str(e)
                        st.error(f"❌ OpenRouter — {e}")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('''
    <div style="
        background: linear-gradient(135deg, rgba(99,102,241,.15) 0%, rgba(168,85,247,.12) 50%, rgba(236,72,153,.10) 100%);
        border: 1px solid rgba(99,102,241,.25); border-radius: 20px; padding: 22px 28px; margin-bottom: 24px;
        display: flex; align-items: center; gap: 18px; box-shadow: inset 0 1px 0 rgba(255,255,255,.07);
    ">
        <div style="font-size:48px;line-height:1">🧠</div>
        <div>
            <div style="font-family:\'Syne\',sans-serif;font-size:18px;font-weight:800;color:#e2e8f0;margin-bottom:4px;">
                Ready to challenge your mind?
            </div>
            <div style="font-size:13px;color:#3d5070;line-height:1.6;">
                Sign in · Pick a subject · Build your XP · Earn the Master Badge!
            </div>
        </div>
    </div>

    <div class="login-header">
        <div class="section-chip">🔐 Sign In</div>
        <div class="login-title">Welcome, challenger!</div>
        <div class="login-sub">Enter your details to begin your personalised quiz journey and save your XP.</div>
    </div>
    ''', unsafe_allow_html=True)

    user_name = st.text_input("Display Name", placeholder="e.g. Karanveer", key="li_name")
    email     = st.text_input("Email Address", placeholder="yourname@example.com", key="li_email")
    password  = st.text_input("Password", type="password", placeholder="Minimum 6 characters", key="li_pw")

    st.markdown('<div class="login-footer"><div class="divider-line"></div></div>', unsafe_allow_html=True)

    if st.button("Continue to Subject →", use_container_width=True):
        e = email.strip()
        n = user_name.strip()
        if not n or not e or not password:
            st.error("⚠️ All fields are required.")
        elif not valid_email(e):
            st.error("⚠️ Enter a valid email — e.g. name@gmail.com")
        elif not valid_pw(password):
            st.error("⚠️ Password must be at least 6 characters.")
        else:
            st.session_state.user_name = n.title()
            st.session_state.email     = e
            st.session_state.page      = "subject"
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE — SUBJECT SELECTION & DIFFICULTY
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "subject":
    render_brand()
    render_steps(1)
    render_badge()

    st.markdown('''
    <div style="margin-bottom:6px;"><div class="section-chip">📚 Pick Your Subject</div></div>
    <div style="font-family:\'Syne\',sans-serif;font-size:22px;font-weight:800;color:#f0f4ff;margin-bottom:6px;">
        What do you want to be tested on?
    </div>
    <div style="color:#2d3e5a;font-size:14px;margin-bottom:20px;">
        Harder difficulties reward more XP! Hit 🔄 on any subject to get fresh AI-generated questions.
    </div>
    ''', unsafe_allow_html=True)

    chosen = st.session_state.get("subject_pick", None)

    subjects_list = list(SUBJECT_DATA.keys())
    # Only show the 6 preset subjects in the grid (filter out any dynamically added custom ones)
    preset_subjects = [s for s in subjects_list if s in PRESET_QUESTIONS]
    row1 = st.columns(3)
    row2 = st.columns(3)
    grid = list(zip([*row1, *row2], preset_subjects))

    for col, subj in grid:
        info = SUBJECT_DATA.get(subj, {"icon": "✏️", "desc": "Custom Quiz"})
        sel_c = "sel" if chosen == subj else ""
        is_refreshed = f"q_cache_{subj}_Easy" in st.session_state

        with col:
            st.markdown(f'''
            <div class="s-card {sel_c}">
                <div class="s-icon">{info['icon']}</div>
                <div class="s-name">{subj}</div>
                <div class="s-desc">{info['desc']}</div>
            </div>
            ''', unsafe_allow_html=True)

            if st.button(f"{'✓ ' if chosen == subj else ''}{subj}", key=f"pick_{subj}", use_container_width=True):
                st.session_state.subject_pick = subj
                st.session_state.pop("custom_pick", None)
                st.rerun()

    # ── Custom Subject Card ────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    custom_sel_c = "sel" if chosen == "__custom__" else ""
    ccard_col1, ccard_col2, ccard_col3 = st.columns([1, 2, 1])
    with ccard_col2:
        st.markdown(f'''
        <div class="s-card custom-card {custom_sel_c}">
            <div class="s-icon">✏️</div>
            <div class="s-name">Custom Subject</div>
            <div class="s-desc">Type your own subject &amp; topic — AI generates the quiz!</div>
        </div>
        ''', unsafe_allow_html=True)
        if st.button(f"{'✓ ' if chosen == '__custom__' else ''}+ Create Custom Quiz", key="pick_custom", use_container_width=True):
            st.session_state.subject_pick = "__custom__"
            st.session_state.pop("custom_ready", None)
            st.rerun()

    # ── Custom Subject Input Panel ─────────────────────────────────────────
    if chosen == "__custom__":
        st.markdown('''
        <div class="custom-panel">
            <div class="custom-panel-title">✏️ Create Your Own Quiz</div>
            <div class="custom-panel-sub">Enter the subject and a specific topic — the AI will generate 15 fresh MCQs (Easy, Medium, Hard).</div>
        </div>
        ''', unsafe_allow_html=True)

        c_subj  = st.text_input("📘 Subject Name",  placeholder="e.g.  Physics, Economics, Music Theory…",     key="custom_subj_input")
        c_topic = st.text_input("🎯 Topic / Chapter", placeholder="e.g.  Newton's Laws,  Demand & Supply,  Scales…", key="custom_topic_input")

        is_ready = st.session_state.get("custom_ready", False)
        cready_subj  = st.session_state.get("custom_ready_subj", "")
        cready_topic = st.session_state.get("custom_ready_topic", "")

        if is_ready and cready_subj and cready_topic:
            st.markdown(f'''
            <div class="custom-ready-panel">
                <div style="font-size:26px">✅</div>
                <div>
                    <div class="custom-ready-text">Questions ready for "{cready_subj} — {cready_topic}"</div>
                    <div class="custom-ready-sub">Choose a difficulty mode below to start!</div>
                </div>
            </div>
            ''', unsafe_allow_html=True)

            cd1, cd2, cd3 = st.columns(3)
            with cd1:
                if st.button("🌱 Easy Mode\n30s | 1 XP/Q", key="cbtn_easy", use_container_width=True):
                    start_custom_quiz(cready_subj, cready_topic, "Easy", 30)
            with cd2:
                if st.button("⚖️ Medium Mode\n20s | 2 XP/Q", key="cbtn_med", use_container_width=True):
                    start_custom_quiz(cready_subj, cready_topic, "Medium", 20)
            with cd3:
                if st.button("🔥 Hard Mode\n15s | 3 XP/Q", key="cbtn_hard", use_container_width=True):
                    start_custom_quiz(cready_subj, cready_topic, "Hard", 15)
        else:
            gcol1, gcol2, gcol3 = st.columns([1, 2, 1])
            with gcol2:
                st.markdown('<div class="gen-btn-wrap">', unsafe_allow_html=True)
                if st.button("🤖 Generate Questions with AI", key="gen_custom_qs", use_container_width=True):
                    sn = c_subj.strip()
                    tn = c_topic.strip()
                    if not sn or not tn:
                        st.error("⚠️ Please fill in both Subject Name and Topic.")
                    else:
                        with st.spinner(f'🤖 Generating MCQs for "{sn} - {tn}"... this takes ~10 seconds'):
                            ok = generate_custom_questions(sn, tn)
                        if ok:
                            st.session_state.custom_ready       = True
                            st.session_state.custom_ready_subj  = sn
                            st.session_state.custom_ready_topic = tn
                            st.toast(f"✅ Questions ready for {sn} — {tn}!", icon="🤖")
                            st.rerun()
                        else:
                            st.error("❌ Could not generate questions. Check your API keys and try again.")
                st.markdown('</div>', unsafe_allow_html=True)


    # ── Difficulty Selection Panel (preset subjects only) ─────────────────
    if chosen and chosen != "__custom__":
        cache_status = "🤖 AI questions active!" if is_refreshed else "📝 Using preset questions"
        st.markdown(f'''
        <div class="diff-panel">
            <div class="diff-title">You selected {info['icon']} {chosen}. Now choose your difficulty:</div>
            <div style="font-size:11px; color:#4a5878; margin-top:-10px; margin-bottom:8px;">{cache_status}</div>
        </div>
        ''', unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("🌱 Easy Mode\n30s | 1 XP/Q", key="btn_easy", use_container_width=True):
                start_quiz(chosen, "Easy", 30)
        with c2:
            if st.button("⚖️ Medium Mode\n20s | 2 XP/Q", key="btn_med", use_container_width=True):
                start_quiz(chosen, "Medium", 20)
        with c3:
            if st.button("🔥 Hard Mode\n15s | 3 XP/Q", key="btn_hard", use_container_width=True):
                start_quiz(chosen, "Hard", 15)

        # ── Refresh button ──────────────────────────────────────────────────
        refresh_label   = "🤖 AI ✓ All Modes Refreshed" if is_refreshed else "🔄 Refresh All Questions (AI)"
        refreshed_class = "refreshed" if is_refreshed else ""
        rcol1, rcol2, rcol3 = st.columns([1, 2, 1])
        with rcol2:
            st.markdown(f'<div class="refresh-btn-wrap {refreshed_class}">', unsafe_allow_html=True)
            if st.button(refresh_label, key="refresh_chosen_subj", use_container_width=True):
                with st.spinner(f"Generating fresh {chosen} questions via AI…"):
                    success = refresh_subject_questions(chosen)
                if success:
                    st.toast(f"✅ {chosen} — all 3 modes refreshed!", icon="🤖")
                    st.rerun()
                else:
                    st.error(f"❌ Could not generate questions for {chosen}. Check your API keys.")
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="logout-area">', unsafe_allow_html=True)
    if st.button("← Log out", key="subj_logout"):
        full_reset()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE — QUIZ
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "quiz":
    subj   = st.session_state.subject
    diff   = st.session_state.difficulty
    timer  = st.session_state.timer_seconds

    xp_multiplier = {"Easy": 1, "Medium": 2, "Hard": 3}[diff]
    info          = SUBJECT_DATA.get(subj, {"icon": "✏️", "desc": "Custom Quiz"})

    qs    = st.session_state.current_questions
    total = len(qs)
    idx   = st.session_state.get("question_index", 0)

    if idx >= total:
        st.session_state.page = "result"
        st.rerun()

    q = qs[idx]

    render_brand()
    render_steps(2)
    render_badge()

    pc, sc = st.columns([5, 1])
    with pc: st.progress(idx / total)
    with sc: st.markdown(f'<div class="spill">⚡{st.session_state.score}/{total}</div>', unsafe_allow_html=True)

    # ── Timer — isolated fragment so ONLY the timer div re-renders ─────────
    @st.fragment(run_every=1)
    def live_timer():
        remaining = timer - int(time.time() - st.session_state.start_time)
        remaining = max(remaining, 0)

        if remaining > (timer * 0.5):   tc, ti = "t-safe",   "🟢"
        elif remaining > (timer * 0.25): tc, ti = "t-warn",  "🟡"
        else:                            tc, ti = "t-danger", "🔴"

        st.markdown(
            f'<div class="tmr {tc}">{ti}&nbsp;&nbsp;{remaining} seconds remaining</div>',
            unsafe_allow_html=True
        )

        if remaining <= 0 and st.session_state.get("question_index") == idx:
            ca = q["answer"]
            st.session_state.wrong_answers.append({
                "question":    q["question"],
                "your_answer": "⏰ Time up — skipped",
                "correct":     f"{ca} → {q['options'][ca]}",
                "explanation": q.get("explanation", "No explanation available.")
            })
            st.session_state.question_index += 1
            st.session_state.start_time = time.time()
            st.rerun()

    live_timer()

    st.markdown(f'<div class="subj-pill">{info["icon"]} {subj} — {diff} Mode (+{xp_multiplier} XP)</div>', unsafe_allow_html=True)

    st.markdown(f'''
    <div class="qcard">
        <div class="qnum">Question {idx+1} of {total}</div>
        <div class="qtxt">{q['question']}</div>
    </div>
    ''', unsafe_allow_html=True)

    selected = st.radio(
        "Your answer", list(q["options"].keys()),
        format_func=lambda k: f"  {k}  ·  {q['options'][k]}",
        index=None, key=f"q_{idx}"
    )

    st.markdown("<br>", unsafe_allow_html=True)
    _, bc_left, bc_right, _ = st.columns([1, 2, 2, 1])

    with bc_left:
        st.markdown('<div class="back-btn-wrap">', unsafe_allow_html=True)
        if st.button("← Back to Subjects", use_container_width=True, key=f"back_{idx}"):
            quiz_reset()
            st.session_state.pop("subject_pick", None)
            st.session_state.pop("subject",      None)
            st.session_state.pop("difficulty",   None)
            st.session_state.page = "subject"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with bc_right:
        if st.button("Submit Answer →", use_container_width=True, key=f"submit_{idx}"):
            if selected is None:
                st.warning("⚠️ Please select an option first.")
            else:
                if selected == q["answer"]:
                    st.session_state.score      = st.session_state.get("score", 0) + 1
                    st.session_state.current_xp += xp_multiplier
                    st.session_state.total_xp   += xp_multiplier
                else:
                    ca = q["answer"]
                    st.session_state.wrong_answers.append({
                        "question":    q["question"],
                        "your_answer": f"{selected} → {q['options'][selected]}",
                        "correct":     f"{ca} → {q['options'][ca]}",
                        "explanation": q.get("explanation", "No explanation available.")
                    })
                st.session_state.question_index += 1
                st.session_state.start_time = time.time()
                st.rerun()



# ══════════════════════════════════════════════════════════════════════════════
# PAGE — RESULT
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "result":
    user_name = st.session_state.get("user_name", "Challenger")
    subj      = st.session_state.subject
    diff      = st.session_state.difficulty
    info      = SUBJECT_DATA.get(subj, {"icon": "✏️", "desc": "Custom Quiz"})
    fs        = st.session_state.score
    total     = len(st.session_state.current_questions)
    pct       = (fs / total) * 100 if total > 0 else 0
    wrongs    = st.session_state.wrong_answers

    current_xp_earned = st.session_state.get("current_xp", 0)
    total_xp          = st.session_state.get("total_xp", 0)
    badge_name, badge_col, badge_msg = get_badge_info(total_xp)

    render_brand()
    render_steps(3)
    render_badge()
    st.balloons()

    if pct == 100:   em, gr = "🏆", "Perfect Score!"
    elif pct >= 80:  em, gr = "🌟", "Excellent Work!"
    elif pct >= 60:  em, gr = "👍", "Good Job!"
    else:            em, gr = "💪", "Keep Practising!"

    hero_html = (
        '<div class="res-hero">'
        + '<div class="res-emoji">' + em + '</div>'
        + '<div class="res-grade" style="color:' + badge_col + ';">' + gr + '</div>'
        + '<div class="res-msg">Outstanding effort, <strong>' + user_name + '</strong>! Here is your performance overview.</div>'
        + '<div class="badge-card" style="border-color:' + badge_col + '; color:' + badge_col + ';">' + badge_name + '</div>'
        + '<div style="font-size:14px; color:#94a3b8; font-style:italic; margin-bottom:24px;">'
        + '&#8220;' + badge_msg + '&#8221;'
        + '</div></div>'
    )
    st.markdown(hero_html, unsafe_allow_html=True)

    st.progress(fs / total if total > 0 else 0)
    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("✅ Correct",  fs)
    with c2: st.metric("❌ Wrong",    total - fs)
    with c3: st.metric("📊 Accuracy", f"{pct:.0f}%")
    with c4: st.metric("⚡ XP Earned", f"+{current_xp_earned}")

    st.markdown('<div class="h-divider"></div>', unsafe_allow_html=True)

    if wrongs:
        with st.expander(f"📋 Review mistakes ({len(wrongs)} wrong)"):
            for i, w in enumerate(wrongs, 1):
                st.markdown(f'''
                <div class="mk">
                    <div class="mk-q">Q{i}: {w['question']}</div>
                    <div class="mk-u">Your answer: {w['your_answer']}</div>
                    <div class="mk-c">✓ Correct: {w['correct']}</div>
                    <div class="mk-e">💡 <strong>Explanation:</strong> {w['explanation']}</div>
                </div>''', unsafe_allow_html=True)
    else:
        st.success(f"🔥 Zero mistakes! Flawless victory for {user_name}!")

    # ── YouTube Study Resources ────────────────────────────────────────────
    st.markdown('<div class="h-divider"></div>', unsafe_allow_html=True)

    # AI-generated personalised study tip
    tip_key = f"ai_tip_{subj}_{diff}_{fs}"
    if tip_key not in st.session_state:
        with st.spinner("🤖 Generating personalised study tip…"):
            tip = get_ai_study_tip(subj, diff, fs, total)
            st.session_state[tip_key] = tip
    else:
        tip = st.session_state[tip_key]

    if tip:
        st.markdown(f'''
        <div class="ai-tip-box">
            <div class="ai-tip-label">🤖 AI Study Coach · Personalised for You</div>
            <div class="ai-tip-text">{tip}</div>
        </div>
        ''', unsafe_allow_html=True)

    # YouTube resource cards — preset subjects use YOUTUBE_RESOURCES dict;
    # custom subjects (subj contains " — ") use AI-generated cards cached in session_state.
    is_custom_subj = " — " in subj
    if is_custom_subj:
        yt_cache_key = f"yt_resources_{subj}"
        if yt_cache_key not in st.session_state:
            # Parse subj_name and topic back from "SubjName — Topic"
            parts = subj.split(" — ", 1)
            c_subj_name = parts[0].strip()
            c_topic     = parts[1].strip() if len(parts) > 1 else subj
            with st.spinner("🤖 Generating YouTube study resources for your topic…"):
                cards = generate_custom_yt_resources(c_subj_name, c_topic)
            st.session_state[yt_cache_key] = cards
        yt_resources = st.session_state.get(yt_cache_key, [])
    else:
        yt_resources = YOUTUBE_RESOURCES.get(subj, [])

    if yt_resources:
        subj_icon = SUBJECT_DATA.get(subj, {"icon": "✏️", "desc": "Custom Quiz"})["icon"]
        yt_label  = "🤖 AI-Curated" if is_custom_subj else "Handpicked"
        st.markdown(f'''
        <div class="yt-section-title">▶️ YouTube Resources — {subj_icon} {subj}</div>
        <div class="yt-section-sub">
            {yt_label} YouTube topics to deepen your understanding of <strong style="color:#e2e8f0">{subj}</strong>.
            Click any card to search on YouTube.
        </div>
        ''', unsafe_allow_html=True)

        # Render cards as a 2×2 grid using columns
        col_pairs = [yt_resources[i:i+2] for i in range(0, len(yt_resources), 2)]
        for pair in col_pairs:
            cols = st.columns(len(pair))
            for col, res in zip(cols, pair):
                with col:
                    st.markdown(f'''
                    <a href="{res['url']}" target="_blank" class="yt-card">
                        <div class="yt-icon">{res['icon']}</div>
                        <div class="yt-title">{res['title']}</div>
                        <div class="yt-desc">{res['desc']}</div>
                        <div class="yt-tag">{res['tag']}</div>
                    </a>
                    ''', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    a, b, c = st.columns(3)
    with a:
        if st.button("🔄 Retry Same", use_container_width=True):
            if is_custom_subj:
                parts = subj.split(" — ", 1)
                c_subj_name = parts[0].strip()
                c_topic     = parts[1].strip() if len(parts) > 1 else subj
                start_custom_quiz(c_subj_name, c_topic, diff, st.session_state.timer_seconds)
            else:
                start_quiz(subj, diff, st.session_state.timer_seconds)
    with b:
        if st.button("📚 Play Again", use_container_width=True):
            quiz_reset()
            st.session_state.pop("subject_pick", None)
            st.session_state.pop("subject",      None)
            st.session_state.pop("difficulty",   None)
            st.session_state.page = "subject"
            st.rerun()
    with c:
        if st.button("🚪 Log Out", use_container_width=True):
            full_reset()
            st.rerun()