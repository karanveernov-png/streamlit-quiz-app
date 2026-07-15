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
# This stops the revolving door, unpacks the user, and loads all saved data!
if "code" in st.query_params:
    # Bring in the profile and bookmark loaders from your database file
    from db import exchange_google_code, load_profile, load_bookmarks
    
    auth_code = st.query_params["code"]
    success, msg, user_data = exchange_google_code(auth_code)
    
    st.query_params.clear()
    
    if success:
        user_id = user_data["id"]
        
        # 1. Unpack the Google data exactly how ui_components expects it
        st.session_state["user_id"] = user_id
        st.session_state["user_name"] = user_data["display_name"]
        st.session_state["email"] = user_data["email"]
        
        # 2. Fetch the saved XP and Bookmarks from the Supabase tables
        profile = load_profile(user_id)
        st.session_state["total_xp"] = profile.get("total_xp", 0)
        st.session_state["best_streak"] = profile.get("best_streak", 0)
        st.session_state["bookmarks"] = load_bookmarks(user_id)
        
        # 3. Tell Streamlit the user is fully loaded and send them to the app
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