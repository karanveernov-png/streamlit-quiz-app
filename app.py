"""
app.py — BrainBlitz entry point.

Responsible for, in order:
  1. Importing config (sets st.set_page_config, loads API keys/clients,
     and st.stop()s early if no AI provider key is configured).
  2. Injecting the global CSS theme.
  3. Initialising Streamlit session state (and restoring any custom
     subjects created earlier in the session).
  4. Routing to the correct page module based on st.session_state.page.

Run with:  streamlit run app.py
"""
import streamlit as st

# Importing config first runs st.set_page_config() and validates API keys
# (it will st.stop() the app here if neither XAI_API_KEY nor
# OPENROUTER_API_KEY is configured).
# 👉 ADD THIS LINE TO DEBUG:
st.write("Streamlit sees these URL parameters:", st.query_params)
import config  # noqa: F401  (imported for its side effects)

import styles
from quiz_logic import init_session_state

from pages import login_page, subject_page, quiz_page, result_page

# 👉 Import your database client to handle the login token
from db import _get_client 

# ── Global CSS ────────────────────────────────────────────────────────────
styles.inject_css()

# ── Session state ─────────────────────────────────────────────────────────
init_session_state()

# ── CATCH SUPABASE LOGIN REDIRECT ─────────────────────────────────────────
# This stops the "revolving door" bug!
if "code" in st.query_params:
    try:
        supabase = _get_client()
        auth_code = st.query_params["code"]
        
        # Exchange the URL code for a real user session
        supabase.auth.exchange_code_for_session({"auth_code": auth_code})
        
        # Wipe the code from the web address so it looks clean
        st.query_params.clear()
        
        # Tell Streamlit the user is logged in and send them to the main app!
        st.session_state["page"] = "subject" 
        st.rerun()
        
    except Exception as e:
        st.error("Authentication failed. Please try again.")

# ── Page router ───────────────────────────────────────────────────────────
PAGES = {
    "login":   login_page.render,
    "subject": subject_page.render,
    "quiz":    quiz_page.render,
    "result":  result_page.render,
}

current_page = st.session_state.get("page", "login")
render_fn = PAGES.get(current_page, login_page.render)
render_fn()