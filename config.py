"""
config.py — Page configuration, API keys, AI client instances, and shared
constants used across the BrainBlitz app.
"""
import os
import streamlit as st
from openai import OpenAI

## ── PAGE CONFIG ─────────────────────────────────────────────
st.set_page_config(
    page_title="BrainBlitz · Quiz App",
    page_icon="🧠",
    layout="centered"
)

# ── DEFAULT CLIENT STATES (Define these FIRST to prevent ImportErrors) ────
groq_client = None
openrouter_client = None

# ── API KEYS ─────────────────────────────────────────────────────────────────
xai_api_key = (
    os.getenv("XAI_API_KEY")
    or st.secrets.get("XAI_API_KEY", None)
)
openrouter_api_key = (
    os.getenv("OPENROUTER_API_KEY")
    or st.secrets.get("OPENROUTER_API_KEY", None)
)

# ── CLIENT BUILDERS ──────────────────────────────────────────────────────────
@st.cache_resource
def _build_groq_client(key):
    return OpenAI(api_key=key, base_url="https://api.groq.com/openai/v1")

@st.cache_resource
def _build_openrouter_client(key):
    return OpenAI(api_key=key, base_url="https://openrouter.ai/api/v1")

# ── INITIALIZE CLIENTS (If keys exist) ───────────────────────────────────────
if xai_api_key:
    groq_client = _build_groq_client(xai_api_key)
if openrouter_api_key:
    openrouter_client = _build_openrouter_client(openrouter_api_key)

# ── CONSTANTS ────────────────────────────────────────────────────────────────
GROK_MODEL       = "openai/gpt-oss-20b"
OPENROUTER_MODEL = "openai/gpt-4o-mini"
NUM_QUESTIONS    = 5
MAX_TOKENS       = 900

# ── Shared secret helper (also used by db.py) ────────────────────────────────
def get_secret(name):
    return os.getenv(name) or st.secrets.get(name, None)

# ── STOP EXECUTION IF NO KEYS (Moved to the bottom!) ─────────────────────────
if not xai_api_key and not openrouter_api_key:
    st.error("No API keys found. Add XAI_API_KEY and/or OPENROUTER_API_KEY to .env or Streamlit secrets.")
    st.stop()