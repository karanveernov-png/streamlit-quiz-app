"""
ui_components.py — Small reusable Streamlit render functions used at the
top of every page: the BrainBlitz brand header, the 4-step progress bar,
and the logged-in user badge.
"""
import streamlit as st

from data import SUBJECT_DATA
from utils import initials, get_badge_info

def render_brand():
    st.markdown('<div class="brand-wrap"><span class="brand-logo">BRAIN<span style="color:#00b4ff;text-shadow:0 0 8px rgba(0,180,255,.9),0 0 24px rgba(0,180,255,.5)">BLITZ</span></span></div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-tag">// Neural Challenge System v2.0</div>', unsafe_allow_html=True)

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
        subj_tag = f'&nbsp;<span style="color:rgba(0,180,255,.7);font-size:10px;font-weight:700;font-family:Orbitron,sans-serif">// {icon} {subj} [{diff}]</span>'

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