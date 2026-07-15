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
import config  # noqa: F401  (imported for its side effects)

import styles
from quiz_logic import init_session_state

from pages import login_page, subject_page, quiz_page, result_page

# ── Global CSS ────────────────────────────────────────────────────────────
styles.inject_css()

# ── Session state ─────────────────────────────────────────────────────────
init_session_state()

# ── CATCH SUPABASE LOGIN REDIRECT ─────────────────────────────────────────
if "code" in st.query_params:
    from db import exchange_google_code
    
    auth_code = st.query_params["code"]
    success, msg, user_data = exchange_google_code(auth_code)
    
    st.query_params.clear()
    
    # 🛑 FREEZE THE APP AND PRINT THE SECRET DATA:
    st.write("--- DEBUGGING RADAR ---")
    st.write("Did login succeed?", success)
    st.write("Database Message:", msg)
    st.write("User Profile Data:", user_data)
    st.stop() # This forces Streamlit to halt before the page reloads!
    
    if success:
        st.session_state["user"] = user_data
        st.session_state["page"] = "subject" 
        st.rerun()
    else:
        st.error(msg)

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