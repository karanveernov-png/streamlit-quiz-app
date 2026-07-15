"""
db.py — Supabase database layer: authentication, profile persistence,
and bookmark storage.
"""
import streamlit as st
from supabase import create_client, Client

# ── CONFIG ────────────────────────────────────────────────────────────────
def _get_secret(name):
    import os
    return os.getenv(name) or st.secrets.get(name, None)


SUPABASE_URL = _get_secret("SUPABASE_URL")
SUPABASE_KEY = _get_secret("SUPABASE_ANON_KEY")


@st.cache_resource
def _get_client() -> "Client | None":
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def is_configured() -> bool:
    """True if Supabase URL/key are present."""
    return bool(SUPABASE_URL and SUPABASE_KEY)


# ── AUTH ──────────────────────────────────────────────────────────────────
def sign_up(email: str, password: str, display_name: str):
    """
    Create a new Supabase Auth user. Returns (success: bool, message: str, user_id: str|None).
    """
    client = _get_client()
    if client is None:
        return False, "Database not configured. Add SUPABASE_URL and SUPABASE_ANON_KEY to secrets.", None
    try:
        res = client.auth.sign_up({
            "email": email,
            "password": password,
            "options": {"data": {"display_name": display_name}},
        })
        if res.user is None:
            return False, "Sign up failed — please try again.", None
        user_id = res.user.id
        # Create the profile row (idempotent upsert in case of retries)
        try:
            client.table("profiles").upsert({
                "id": user_id,
                "display_name": display_name,
                "email": email,
                "total_xp": 0,
                "best_streak": 0,
            }).execute()
        except Exception:
            pass  # profile creation is best-effort; trigger may also handle this server-side
        # If email confirmation is required, session may be None
        if res.session is None:
            return True, "Account created! Check your inbox to confirm your email, then log in.", user_id
        return True, "Account created!", user_id
    except Exception as e:
        msg = str(e)
        if "already registered" in msg.lower() or "already exists" in msg.lower():
            return False, "That email is already registered. Try logging in instead.", None
        return False, f"Sign up failed: {msg}", None


def sign_in(email: str, password: str):
    """
    Log in an existing user. Returns (success: bool, message: str, user: dict|None).
    user dict contains: id, email, display_name
    """
    client = _get_client()
    if client is None:
        return False, "Database not configured. Add SUPABASE_URL and SUPABASE_ANON_KEY to secrets.", None
    try:
        res = client.auth.sign_in_with_password({"email": email, "password": password})
        if res.user is None:
            return False, "Invalid email or password.", None
        user_id = res.user.id
        display_name = (res.user.user_metadata or {}).get("display_name") or email.split("@")[0]
        return True, "Welcome back!", {"id": user_id, "email": email, "display_name": display_name}
    except Exception as e:
        msg = str(e)
        if "invalid" in msg.lower() or "credentials" in msg.lower():
            return False, "Invalid email or password.", None
        if "confirm" in msg.lower():
            return False, "Please confirm your email before logging in.", None
        return False, f"Login failed: {msg}", None


def sign_out():
    client = _get_client()
    if client is None:
        return
    try:
        client.auth.sign_out()
    except Exception:
        pass



def get_google_oauth_url() -> tuple:
    """
    Build the Supabase Google OAuth URL manually using implicit flow
    (no code_challenge → tokens arrive in the URL hash fragment, not as ?code=).
    JavaScript in login_page converts the hash to ?at= query params that
    Python can actually read.

    Requires Google provider enabled in Supabase dashboard →
    Authentication → Providers → Google.
    Returns (url: str | None, error: str | None).
    """
    import urllib.parse
    supabase_url = SUPABASE_URL
    if not supabase_url:
        return None, "SUPABASE_URL not configured."
    app_url = _get_secret("APP_URL") or "http://localhost:8501"
    qs = urllib.parse.urlencode({
        "provider": "google",
        "redirect_to": app_url,
        "scopes": "email profile",
    })
    url = f"{supabase_url.rstrip('/')}/auth/v1/authorize?{qs}"
    return url, None


def _upsert_google_profile(client, user):
    """Create a profile row for a first-time Google user (best-effort)."""
    try:
        meta = user.user_metadata or {}
        display_name = (
            meta.get("full_name") or meta.get("name") or user.email.split("@")[0]
        )
        avatar_url = meta.get("avatar_url") or meta.get("picture") or ""
        existing = (
            client.table("profiles")
            .select("id")
            .eq("id", user.id)
            .limit(1)
            .execute()
        )
        if not existing.data:
            client.table("profiles").insert({
                "id": user.id,
                "display_name": display_name,
                "email": user.email,
                "total_xp": 0,
                "best_streak": 0,
            }).execute()
        return display_name, avatar_url
    except Exception:
        meta = user.user_metadata or {}
        return (
            meta.get("full_name") or meta.get("name") or user.email.split("@")[0],
            meta.get("avatar_url") or meta.get("picture") or "",
        )


def set_google_session(access_token: str, refresh_token: str = "") -> tuple:
    """
    Activate a Supabase session from implicit-flow tokens returned in the
    URL hash and converted to query params by the JS hash redirector.
    Returns (success: bool, message: str, user: dict | None).
    """
    client = _get_client()
    if client is None:
        return False, "Database not configured.", None
    try:
        res = client.auth.set_session(access_token, refresh_token)
        if not res.user:
            return False, "Could not verify Google session.", None
        display_name, avatar_url = _upsert_google_profile(client, res.user)
        return True, "Signed in with Google!", {
            "id": res.user.id,
            "email": res.user.email,
            "display_name": display_name,
            "avatar_url": avatar_url,
        }
    except Exception as e:
        return False, f"Google sign-in failed: {e}", None


def exchange_google_code(code: str) -> tuple:
    """
    PKCE fallback: exchange ?code= for a session (used if the Supabase project
    has PKCE enabled at the dashboard level).
    Returns (success: bool, message: str, user: dict | None).
    """
    client = _get_client()
    if client is None:
        return False, "Database not configured.", None
    try:
        res = client.auth.exchange_code_for_session({"auth_code": code})
        if not res.user:
            return False, "Google sign-in failed — no user returned.", None
        display_name, avatar_url = _upsert_google_profile(client, res.user)
        return True, "Signed in with Google!", {
            "id": res.user.id,
            "email": res.user.email,
            "display_name": display_name,
            "avatar_url": avatar_url,
        }
    except Exception as e:
        return False, f"Google sign-in failed: {e}", None

# ── PROFILE / PROGRESS ───────────────────────────────────────────────────
def load_profile(user_id: str):
    """
    Fetch saved progress for a user. Returns dict with total_xp, best_streak,
    or sensible defaults if no row exists yet / on failure.
    """
    defaults = {"total_xp": 0, "best_streak": 0, "display_name": None}
    client = _get_client()
    if client is None:
        return defaults
    try:
        res = client.table("profiles").select("*").eq("id", user_id).limit(1).execute()
        if res.data:
            row = res.data[0]
            return {
                "total_xp": row.get("total_xp", 0) or 0,
                "best_streak": row.get("best_streak", 0) or 0,
                "display_name": row.get("display_name"),
            }
        return defaults
    except Exception:
        return defaults


def save_progress(user_id: str, total_xp: int, best_streak: int):
    """Write-through update of XP/streak. Silently no-ops on failure (non-blocking)."""
    client = _get_client()
    if client is None:
        return
    try:
        client.table("profiles").upsert({
            "id": user_id,
            "total_xp": total_xp,
            "best_streak": best_streak,
        }).execute()
    except Exception:
        pass


# ── BOOKMARKS ────────────────────────────────────────────────────────────
def load_bookmarks(user_id: str):
    """Return list of bookmark dicts for this user, or [] on failure."""
    client = _get_client()
    if client is None:
        return []
    try:
        res = (
            client.table("bookmarks")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )
        out = []
        for row in res.data or []:
            out.append({
                "question": row.get("question"),
                "options": row.get("options"),
                "answer": row.get("answer"),
                "explanation": row.get("explanation"),
                "subject": row.get("subject"),
                "difficulty": row.get("difficulty"),
            })
        return out
    except Exception:
        return []


def save_bookmark(user_id: str, bookmark: dict):
    """Insert a single bookmark row. Non-blocking on failure."""
    client = _get_client()
    if client is None:
        return
    try:
        client.table("bookmarks").insert({
            "user_id": user_id,
            "question": bookmark.get("question"),
            "options": bookmark.get("options"),
            "answer": bookmark.get("answer"),
            "explanation": bookmark.get("explanation"),
            "subject": bookmark.get("subject"),
            "difficulty": bookmark.get("difficulty"),
        }).execute()
    except Exception:
        pass


def clear_bookmarks(user_id: str):
    """Delete all bookmark rows for this user. Non-blocking on failure."""
    client = _get_client()
    if client is None:
        return
    try:
        client.table("bookmarks").delete().eq("user_id", user_id).execute()
    except Exception:
        pass