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
 
st.title("🧠 BrainBlitz AI Test")
 
# ── API KEY ─────────────────────────────────────────────────
xai_api_key = (
    os.getenv("XAI_API_KEY")
    or st.secrets.get("XAI_API_KEY", None)
)
if not xai_api_key:
    st.error("XAI_API_KEY not found. Add it to .env or Streamlit secrets.")
    st.stop()
 
# ── GROK (Now Groq!) CLIENT ───────────────────────────────────────
client = OpenAI(api_key=xai_api_key, base_url="https://api.groq.com/openai/v1")

# UPDATE: Changed to Groq's active 3.1 model because the old one was decommissioned
GROK_MODEL    = "llama-3.1-8b-instant"  
NUM_QUESTIONS = 5              # token saver: fewer questions
MAX_TOKENS    = 900            # cap per API response
# ── TEST BUTTON ─────────────────────────────────────────────
if st.button("Test Grok API"):
    with st.spinner(f"Connecting to {GROK_MODEL}..."):
        try:
            response = client.chat.completions.create(
                model=GROK_MODEL,
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=10,
                temperature=0
            )
            st.success(f"✅ Grok API Connected — {GROK_MODEL}")
            st.write(response.choices[0].message.content)
        except Exception as e:
            st.error(f"❌ Error: {e}")
# ══════════════════════════════════════════════════════════════════════════════
# GLOBAL CSS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('''
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800;900&family=Inter:wght@300;400;500;600&display=swap');
 
/* ─── Base ─────────────────────────────────────────────────────────── */
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
 
/* ─── Orbs ──────────────────────────────────────────────────────────── */
.orb-a {
    position: fixed; width: 600px; height: 600px;
    top: -200px; right: -200px;
    background: radial-gradient(circle, rgba(99,102,241,.16) 0%, transparent 60%);
    border-radius: 50%; pointer-events: none; z-index: 0;
    animation: drift 12s ease-in-out infinite alternate;
}
.orb-b {
    position: fixed; width: 500px; height: 500px;
    bottom: -150px; left: -150px;
    background: radial-gradient(circle, rgba(236,72,153,.11) 0%, transparent 60%);
    border-radius: 50%; pointer-events: none; z-index: 0;
    animation: drift 16s ease-in-out infinite alternate-reverse;
}
@keyframes drift {
    0%   { transform: translateY(0px) scale(1); }
    100% { transform: translateY(30px) scale(1.06); }
}
 
/* ─── Brand ─────────────────────────────────────────────────────────── */
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
 
/* ─── Step bar ───────────────────────────────────────────────────────── */
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
 
/* ─── Login card ──────────────────────────────────────────────────── */
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
 
/* ─── Inputs & Buttons ─────────────────────────────────────────────── */
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
 
/* ─── Subject cards & Difficulty Panel ────────────────────────────────── */
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
 
/* ─── Timer & Progress ────────────────────────────────────────────────── */
.stProgress > div > div { background: rgba(255,255,255,.05) !important; border-radius: 99px !important; height: 5px !important; }
.stProgress > div > div > div > div { background: linear-gradient(90deg,#6366f1,#a855f7,#ec4899) !important; }
 
.tmr {
    border-radius: 14px; padding: 11px 20px; text-align: center; font-family: 'Syne', sans-serif;
    font-size: 20px; font-weight: 800; margin-bottom: 16px; border: 1.5px solid;
    display: flex; align-items: center; justify-content: center; gap: 10px;
}
.t-safe   { background:rgba(16,185,129,.08); border-color:rgba(16,185,129,.3); color:#34d399; }
.t-warn   { background:rgba(245,158,11,.08); border-color:rgba(245,158,11,.3); color:#fbbf24; }
.t-danger { background:rgba(239,68,68,.1);   border-color:rgba(239,68,68,.4);  color:#f87171;
    animation: pulse-red .6s ease-in-out infinite alternate; }
 
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
</style>
<div class="orb-a"></div>
<div class="orb-b"></div>
''', unsafe_allow_html=True)
 
# ══════════════════════════════════════════════════════════════════════════════
# DYNAMIC SUBJECTS
# ══════════════════════════════════════════════════════════════════════════════
SUBJECT_DATA = {
    "History": {"icon": "📜", "desc": "India & the world"},
    "Geography": {"icon": "🌍", "desc": "India, planets & beyond"},
    "Politics": {"icon": "🏛️", "desc": "Civics and governance"},
    "Biology": {"icon": "🔬", "desc": "Life & living systems"},
    "Computer Science": {"icon": "💻", "desc": "Coding & technology"},
    "English": {"icon": "📖", "desc": "Grammar & vocabulary"}
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
    for k in [k for k in st.session_state if isinstance(k, str) and k.startswith("q_")]:
        del st.session_state[k]
 
# ── AI Generation Logic ────────────────────────────────────────────────────
def generate_questions(subject, difficulty, num_questions=NUM_QUESTIONS):
    # Short prompt = fewer input tokens consumed
    prompt = (
        f"Make {num_questions} MCQs on {subject} ({difficulty}). "
        "JSON array only, no markdown. Each: "
        "{\"question\":\"...\",\"options\":{\"A\":\"...\",\"B\":\"...\",\"C\":\"...\",\"D\":\"...\"},\"answer\":\"A\",\"explanation\":\"1 sentence.\"}"
    )
    try:
        chat_completion = client.chat.completions.create(
            model=GROK_MODEL,
            messages=[
                {"role": "system", "content": "Reply with raw JSON array only. No extra text."},
                {"role": "user",   "content": prompt},
            ],
            max_tokens=MAX_TOKENS,
            temperature=0.5,
        )
        text = chat_completion.choices[0].message.content.strip()
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        return json.loads(text.strip())
    except Exception as e:
        st.error(f"Failed to generate questions: {e}")
        return None
 
def start_quiz(subj, difficulty, timer_sec):
    st.session_state.subject = subj
    st.session_state.difficulty = difficulty
    st.session_state.timer_seconds = timer_sec
    
    with st.spinner("🧠 BrainBlitz AI is generating your questions..."):
        questions = generate_questions(subj, difficulty, NUM_QUESTIONS)
        if not questions:
            return # Stop if generation failed
        st.session_state.current_questions = questions
 
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
    name = st.session_state.get("user_name", "User")
    email = st.session_state.get("email", "")
    xp = st.session_state.get("total_xp", 0)
    av = initials(name)
    
    badge_name, badge_col, _ = get_badge_info(xp)
    
    subj = st.session_state.get("subject", "")
    diff = st.session_state.get("difficulty", "")
    
    subj_tag = ""
    if subj and diff:
        icon = SUBJECT_DATA[subj]["icon"]
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
 
# ── Init ───────────────────────────────────────────────────────────────────
if "page" not in st.session_state: 
    st.session_state.page = "login"
if "total_xp" not in st.session_state:
    st.session_state.total_xp = 0
 
# ══════════════════════════════════════════════════════════════════════════════
# PAGE — LOGIN
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "login":
    render_brand()
    render_steps(0)
 
    st.markdown('''
    <div style="
        background: linear-gradient(135deg, rgba(99,102,241,.15) 0%, rgba(168,85,247,.12) 50%, rgba(236,72,153,.10) 100%);
        border: 1px solid rgba(99,102,241,.25); border-radius: 20px; padding: 22px 28px; margin-bottom: 24px;
        display: flex; align-items: center; gap: 18px; box-shadow: inset 0 1px 0 rgba(255,255,255,.07);
    ">
        <div style="font-size:48px;line-height:1">🧠</div>
        <div>
            <div style="font-family:'Syne',sans-serif;font-size:18px;font-weight:800;color:#e2e8f0;margin-bottom:4px;">
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
    email = st.text_input("Email Address", placeholder="yourname@example.com", key="li_email")
    password = st.text_input("Password", type="password", placeholder="Minimum 6 characters", key="li_pw")
 
    st.markdown('<div class="login-footer"><div class="divider-line"></div></div>', unsafe_allow_html=True)
 
    if st.button("Continue to Subject →", use_container_width=True):
        e = email.strip()
        n = user_name.strip()
        if not n or not e or not password: st.error("⚠️ All fields are required.")
        elif not valid_email(e): st.error("⚠️ Enter a valid email — e.g. name@gmail.com")
        elif not valid_pw(password): st.error("⚠️ Password must be at least 6 characters.")
        else:
            st.session_state.user_name = n.title()
            st.session_state.email = e
            st.session_state.page = "subject"
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
    <div style="font-family:'Syne',sans-serif;font-size:22px;font-weight:800;color:#f0f4ff;margin-bottom:6px;">
        What do you want to be tested on?
    </div>
    <div style="color:#2d3e5a;font-size:14px;margin-bottom:20px;">
        Harder difficulties reward more XP! Questions are now AI-generated.
    </div>
    ''', unsafe_allow_html=True)
 
    chosen = st.session_state.get("subject_pick", None)
    
    subjects_list = list(SUBJECT_DATA.keys())
    row1 = st.columns(3)
    row2 = st.columns(3)
    grid = list(zip([*row1, *row2], subjects_list))
 
    for col, subj in grid:
        info = SUBJECT_DATA[subj]
        sel_c = "sel" if chosen == subj else ""
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
                st.rerun()
 
    # ── Difficulty Selection Panel ─────────────────────────────────────────
    if chosen:
        info = SUBJECT_DATA[chosen]
        st.markdown(f'''
        <div class="diff-panel">
            <div class="diff-title">You selected {info['icon']} {chosen}. Now choose your difficulty:</div>
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
    subj = st.session_state.subject
    diff = st.session_state.difficulty
    timer = st.session_state.timer_seconds
    
    xp_multiplier = {"Easy": 1, "Medium": 2, "Hard": 3}[diff]
    info = SUBJECT_DATA[subj]
    
    # Load AI generated questions from state
    qs = st.session_state.current_questions
    total = len(qs)
    idx = st.session_state.get("question_index", 0)
 
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
 
    @st.fragment(run_every=1)
    def live_timer():
        remaining = timer - int(time.time() - st.session_state.start_time)
        remaining = max(remaining, 0)
 
        if remaining > (timer * 0.5): tc, ti = "t-safe", "🟢"
        elif remaining > (timer * 0.25): tc, ti = "t-warn", "🟡"
        else: tc, ti = "t-danger", "🔴"
 
        st.markdown(f'<div class="tmr {tc}">{ti}&nbsp;&nbsp;{remaining} seconds remaining</div>', unsafe_allow_html=True)
 
        if remaining <= 0:
            ca = q["answer"]
            if st.session_state.get("question_index") == idx:
                st.session_state.wrong_answers.append({
                    "question": q["question"],
                    "your_answer": "⏰ Time up — skipped",
                    "correct": f"{ca} → {q['options'][ca]}",
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
    _, bc, _ = st.columns([1, 3, 1])
    with bc:
        if st.button("Submit Answer →", use_container_width=True, key=f"submit_{idx}"):
            if selected is None:
                st.warning("⚠️ Please select an option first.")
            else:
                if selected == q["answer"]:
                    st.session_state.score = st.session_state.get("score", 0) + 1
                    st.session_state.current_xp += xp_multiplier
                    st.session_state.total_xp += xp_multiplier
                else:
                    ca = q["answer"]
                    st.session_state.wrong_answers.append({
                        "question": q["question"],
                        "your_answer": f"{selected} → {q['options'][selected]}",
                        "correct": f"{ca} → {q['options'][ca]}",
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
    subj = st.session_state.subject
    diff = st.session_state.difficulty
    info = SUBJECT_DATA[subj]
    fs = st.session_state.score
    total = len(st.session_state.current_questions)
    pct = (fs / total) * 100 if total > 0 else 0
    wrongs = st.session_state.wrong_answers
    
    current_xp_earned = st.session_state.get("current_xp", 0)
    total_xp = st.session_state.get("total_xp", 0)
    badge_name, badge_col, badge_msg = get_badge_info(total_xp)
 
    render_brand()
    render_steps(3)
    render_badge()
    st.balloons()
 
    if pct == 100: em, gr = "🏆", "Perfect Score!"
    elif pct >= 80: em, gr = "🌟", "Excellent Work!"
    elif pct >= 60: em, gr = "👍", "Good Job!"
    else: em, gr = "💪", "Keep Practising!"
 
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
    with c1: st.metric("✅ Correct", fs)
    with c2: st.metric("❌ Wrong", total - fs)
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
 
    st.markdown("<br>", unsafe_allow_html=True)
    a, b, c = st.columns(3)
    with a:
        if st.button("🔄 Retry Same", use_container_width=True):
            start_quiz(subj, diff, st.session_state.timer_seconds)
    with b:
        if st.button("📚 Play Again", use_container_width=True):
            quiz_reset()
            st.session_state.pop("subject_pick", None)
            st.session_state.pop("subject", None)
            st.session_state.pop("difficulty", None)
            st.session_state.page = "subject"
            st.rerun()
    with c:
        if st.button("🚪 Log Out", use_container_width=True):
            full_reset()
            st.rerun()