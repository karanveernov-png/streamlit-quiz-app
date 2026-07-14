"""
login_page.py — Authentication screen: log in / create account tabs,
API connectivity test, and the post-signup "go to login" prompt.
"""
import streamlit as st

from config import groq_client, openrouter_client, GROK_MODEL, OPENROUTER_MODEL
from db import (
    is_configured, sign_in, sign_up, load_profile, load_bookmarks,
    get_google_oauth_url, exchange_google_code,
)
from utils import valid_email, valid_pw
from ui_components import render_brand, render_steps


_GOOGLE_G_SVG = """<svg width="18" height="18" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
  <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>
  <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>
  <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>
  <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>
</svg>"""


def _handle_oauth_callback():
    """
    Called at the top of render().  If Supabase redirected back with ?code=,
    exchange it for a session and drop the user straight into the app.
    """
    code = st.query_params.get("code")
    if not code:
        return

    with st.spinner("Signing in with Google…"):
        ok, msg, user = exchange_google_code(code)

    # Clear the one-time code from the URL regardless of outcome
    try:
        st.query_params.clear()
    except Exception:
        pass

    if not ok:
        st.error(f"⚠️ {msg}")
        return

    profile          = load_profile(user["id"])
    saved_bookmarks  = load_bookmarks(user["id"])
    st.session_state.user_id     = user["id"]
    st.session_state.user_name   = (profile.get("display_name") or user["display_name"]).title()
    st.session_state.email       = user["email"]
    st.session_state.total_xp    = profile.get("total_xp", 0)
    st.session_state.best_streak = profile.get("best_streak", 0)
    st.session_state.bookmarks   = saved_bookmarks
    st.session_state.page        = "subject"
    st.success(f"✅ {msg}")
    st.rerun()


def _google_button():
    """
    Render an OR divider and the Google sign-in button.
    Generates the OAuth URL once per session and caches it.
    """
    if not is_configured():
        return

    # Build URL once per session (contains an anti-CSRF state token)
    if "google_oauth_url" not in st.session_state:
        url, err = get_google_oauth_url()
        st.session_state["google_oauth_url"] = url if not err else ""

    google_url = st.session_state.get("google_oauth_url", "")
    if not google_url:
        return

    st.markdown(f"""
<div style="display:flex;align-items:center;gap:12px;margin:20px 0 14px;">
  <div style="flex:1;height:1px;background:rgba(200,216,232,0.1);"></div>
  <span style="font-size:11px;color:rgba(200,216,232,0.3);font-family:'DM Sans',sans-serif;
               letter-spacing:1.5px;text-transform:uppercase;">or</span>
  <div style="flex:1;height:1px;background:rgba(200,216,232,0.1);"></div>
</div>
<a href="{google_url}" target="_self" style="
  display:flex;align-items:center;justify-content:center;gap:10px;
  width:100%;padding:11px 20px;margin-bottom:4px;
  background:rgba(255,255,255,0.05);
  border:1px solid rgba(255,255,255,0.14);
  border-radius:4px;
  color:#c8d8e8;
  font-family:'DM Sans',sans-serif;font-size:14px;font-weight:600;
  text-decoration:none;cursor:pointer;
  box-sizing:border-box;
">
  {_GOOGLE_G_SVG}
  Continue with Google
</a>
""", unsafe_allow_html=True)


def render():
    # Handle OAuth redirect-back before any UI is painted
    _handle_oauth_callback()

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

        _google_button()

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

        _google_button()

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