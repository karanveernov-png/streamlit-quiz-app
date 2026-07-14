"""
utils.py — Small stateless validators and helpers shared across pages:
email/password validation, name initials, XP badge lookup, and the
full session-state reset used on logout.
"""
import re
import streamlit as st

def valid_email(e): return bool(re.match(r"^[\w\.\+\-]+@[\w\-]+\.[a-zA-Z]{2,}$", e.strip()))
def valid_pw(p): return len(p) >= 6

def initials(name):
    parts = re.split(r"[.\-_ ]", name.strip())
    return "".join(p[0].upper() for p in parts if p)[:2] or "U"

def get_badge_info(xp):
    if xp >= 150: return "👑 SUPREME COMMANDER",  "#00ffa0", "An absolute legend. Your knowledge is unmatched!"
    elif xp >= 100: return "🦅 WARRIOR ELITE",  "#00b4ff", "A spectacular and brave performance on the battlefield!"
    elif xp >= 50: return "🥇 GOLD VANGUARD",    "#ffd700", "You're shining brightly at the top!"
    elif xp >= 25: return "🥈 SILVER GLADIATOR",  "#c0d8e8", "Solid, consistent, and highly impressive!"
    elif xp >= 10: return "🥉 BRONZE SPARTAN",  "#e8a060", "A great start, keep building your strength!"
    else: return "🌱 CADET", "#00ffa0", "Every commander was once a cadet. Keep training!"

def full_reset():
    for k in list(st.session_state.keys()):
        del st.session_state[k]