"""
login_page.py — Authentication screen: log in / create account tabs,
API connectivity test, and the post-signup "go to login" prompt.
"""
import streamlit as st

from config import groq_client, openrouter_client, GROK_MODEL, OPENROUTER_MODEL
from db import is_configured, sign_in, sign_up, load_profile, load_bookmarks
from utils import valid_email, valid_pw
from ui_components import render_brand, render_steps


def render():
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
        background: rgba(0,255,160,.04);
        border: 1px solid rgba(0,255,160,.15); border-radius: 3px; padding: 20px 24px; margin-bottom: 20px;
        display: flex; align-items: center; gap: 18px;
        border-left: 3px solid rgba(0,255,160,.5);
    ">
        <div style="font-size:42px;line-height:1">⚡</div>
        <div>
            <div style="font-family:\'Orbitron\',sans-serif;font-size:15px;font-weight:800;color:#00ffa0;margin-bottom:4px;letter-spacing:.5px;">
                INITIALISE YOUR CHALLENGE
            </div>
            <div style="font-size:12px;color:rgba(0,255,160,.4);line-height:1.6;">
                Sign in → Pick a subject → Build XP → Earn the Master Badge
            </div>
        </div>
    </div>

    <div class="login-header">
        <div class="section-chip">// AUTH</div>
        <div class="login-title">IDENTIFY YOURSELF</div>
        <div class="login-sub">Enter your credentials to access the neural challenge system.</div>
    </div>
    ''', unsafe_allow_html=True)

    if not is_configured():
        st.warning("⚠️ Database not configured — add `SUPABASE_URL` and `SUPABASE_ANON_KEY` to your Streamlit secrets to enable accounts.")

   # Initialize the default tab state
    if "auth_tab" not in st.session_state:
        st.session_state.auth_tab = "🔐 Log In"

    # A radio button that mimics tabs
    selected_tab = st.radio(
        "Authentication",
        ["🔐 Log In", "✨ Create Account"],
        horizontal=True,
        label_visibility="collapsed",
        key="auth_tab"
    )

    # ── LOG IN TAB ──────────────────────────────────────────────────────
    if selected_tab == "🔐 Log In":
        li_email = st.text_input("Email Address", placeholder="yourname@example.com", key="li_email")
        li_pw    = st.text_input("Password", type="password", placeholder="Your password", key="li_pw")

        if st.button("Log In →", use_container_width=True, key="login_btn", disabled=not is_configured()):
            e = li_email.strip()
            if not e or not li_pw:
                st.error("⚠️ Enter both email and password.")
            elif not valid_email(e):
                st.error("⚠️ Enter a valid email — e.g. name@gmail.com")
            else:
                with st.spinner("Authenticating…"):
                    ok, msg, user = sign_in(e, li_pw)
                if not ok:
                    st.error(f"⚠️ {msg}")
                else:
                    # Load saved progress from the database
                    profile = load_profile(user["id"])
                    saved_bookmarks = load_bookmarks(user["id"])
                    st.session_state.user_id     = user["id"]
                    st.session_state.user_name   = (profile.get("display_name") or user["display_name"]).title()
                    st.session_state.email       = user["email"]
                    st.session_state.total_xp    = profile.get("total_xp", 0)
                    st.session_state.best_streak = profile.get("best_streak", 0)
                    st.session_state.bookmarks   = saved_bookmarks
                    st.session_state.page        = "subject"
                    st.success(f"✅ {msg}")
                    st.rerun()

    # ── CREATE ACCOUNT TAB ──────────────────────────────────────────────
    elif selected_tab == "✨ Create Account":
        su_name  = st.text_input("Display Name", placeholder="e.g. Karanveer", key="su_name")
        su_email = st.text_input("Email Address", placeholder="yourname@example.com", key="su_email")
        su_pw    = st.text_input("Password", type="password", placeholder="Minimum 6 characters", key="su_pw")
        su_pw2   = st.text_input("Confirm Password", type="password", placeholder="Re-enter password", key="su_pw2")

        if st.button("Create Account →", use_container_width=True, key="signup_btn", disabled=not is_configured()):
            n = su_name.strip()
            e = su_email.strip()
            if not n or not e or not su_pw or not su_pw2:
                st.error("⚠️ All fields are required.")
            elif not valid_email(e):
                st.error("⚠️ Enter a valid email — e.g. name@gmail.com")
            elif not valid_pw(su_pw):
                st.error("⚠️ Password must be at least 6 characters.")
            elif su_pw != su_pw2:
                st.error("⚠️ Passwords do not match.")
            else:
                with st.spinner("Creating your account…"):
                    ok, msg, user_id = sign_up(e, su_pw, n.title())
                if not ok:
                    st.error(f"⚠️ {msg}")
                else:
                    st.success(f"✅ {msg}")
                    # If no email confirmation required, Supabase already returned a session
                    # via sign_up — but to keep auth state simple/consistent we ask the user
                    # to log in explicitly on the Log In tab.
                    if user_id:
                        st.session_state["show_login_switch"] = True
                        st.rerun()

        # ── Post-signup login switch ─────────────────────────────────────────
        if st.session_state.get("show_login_switch"):
            st.markdown("""
            <div style="
                background: rgba(0,255,160,.06);
                border: 1px solid rgba(0,255,160,.3);
                border-radius: 4px; padding: 18px 22px; margin-top: 16px;
                border-left: 3px solid rgba(0,255,160,.7);
                display: flex; align-items: center; gap: 14px;
            ">
                <div style="font-size:28px">🎉</div>
                <div>
                    <div style="font-family:'Orbitron',sans-serif;font-size:13px;font-weight:800;color:#00ffa0;margin-bottom:3px;letter-spacing:.5px;">
                        ACCOUNT CREATED!
                    </div>
                    <div style="font-size:12px;color:rgba(0,255,160,.5);line-height:1.5;">
                        Your neural profile is ready. Switch to login to begin your first challenge.
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Define the callback function right before the button
            def switch_to_login_callback():
                st.session_state.pop("show_login_switch", None)
                # Clear signup fields
                for k in ["su_name", "su_email", "su_pw", "su_pw2"]:
                    st.session_state.pop(k, None)
                # Safely update the radio menu state
                st.session_state.auth_tab = "🔐 Log In"

            # Create the button and attach the callback
            st.button("🔐 Go to Login", key="goto_login_button", on_click=switch_to_login_callback)

    st.markdown('<div class="login-footer"><div class="divider-line"></div></div>', unsafe_allow_html=True)