import streamlit as st
import time
import re

# ── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="BrainBlitz · Quiz App",
    page_icon="🧠",
    layout="centered"
)

# ══════════════════════════════════════════════════════════════════════════════
# GLOBAL CSS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
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
.step-circle.done  { background: rgba(99,102,241,.25); color: #818cf8; border: 2px solid #6366f1; }
.step-circle.active { background: linear-gradient(135deg,#6366f1,#a855f7); color: #fff; border: 2px solid transparent; box-shadow: 0 0 18px rgba(99,102,241,.5); }
.step-circle.idle  { background: rgba(255,255,255,.04); color: #2d3748; border: 2px solid rgba(255,255,255,.08); }
.step-label { font-size: 10px; letter-spacing: 1px; text-transform: uppercase; font-weight: 600; }
.step-label.done  { color: #6366f1; }
.step-label.active { color: #c084fc; }
.step-label.idle  { color: #1e2535; }
.step-line { flex: 1; height: 2px; background: rgba(255,255,255,.07); margin-top: -22px; }
.step-line.done { background: linear-gradient(90deg,#6366f1,#a855f7); }

/* ─── Login card wrapper (Streamlit-safe) ──────────────────────────── */
.login-header {
    background: linear-gradient(145deg, rgba(22,30,50,.95), rgba(10,15,28,.98));
    border: 1px solid rgba(99,102,241,.22);
    border-radius: 24px;
    padding: 36px 40px 8px;
    margin-bottom: -10px;
    position: relative; overflow: hidden;
}
.login-header::before {
    content:""; position:absolute; top:0; left:0; right:0; height:3px;
    background: linear-gradient(90deg,#6366f1,#a855f7,#ec4899);
    border-radius: 24px 24px 0 0;
}
.login-footer {
    background: linear-gradient(145deg, rgba(22,30,50,.95), rgba(10,15,28,.98));
    border: 1px solid rgba(99,102,241,.22);
    border-top: none;
    border-radius: 0 0 24px 24px;
    padding: 8px 40px 32px;
}
.section-chip {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(99,102,241,.12); border: 1px solid rgba(99,102,241,.3);
    color: #818cf8; font-size: 11px; font-weight: 700;
    letter-spacing: 1.5px; text-transform: uppercase;
    padding: 5px 14px; border-radius: 99px; margin-bottom: 14px;
}
.login-title {
    font-family: 'Syne', sans-serif; font-size: 26px; font-weight: 800;
    color: #f1f5f9; margin-bottom: 6px;
}
.login-sub {
    color: #3d4f6e; font-size: 14px; margin-bottom: 22px; line-height: 1.6;
}
.divider-line {
    height: 1px;
    background: linear-gradient(90deg,transparent,rgba(99,102,241,.35),transparent);
    margin: 22px 0;
}
.trust-note {
    text-align: center; color: #1e2a3e; font-size: 12px; margin-top: 6px;
}

/* ─── Inputs ─────────────────────────────────────────────────────────── */
div[data-testid="stTextInput"] label,
div[data-testid="stPasswordInput"] label {
    font-size: 11px !important; font-weight: 700 !important;
    letter-spacing: 2px; text-transform: uppercase;
    color: #3d5070 !important; margin-bottom: 6px;
}
div[data-testid="stTextInput"] input,
div[data-testid="stPasswordInput"] input {
    background: rgba(255,255,255,.04) !important;
    border: 1.5px solid rgba(255,255,255,.09) !important;
    border-radius: 12px !important;
    color: #dde3f0 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 15px !important; padding: 13px 16px !important;
    transition: border-color .2s, box-shadow .2s !important;
}
div[data-testid="stTextInput"] input:focus,
div[data-testid="stPasswordInput"] input:focus {
    border-color: rgba(99,102,241,.7) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,.13) !important;
    background: rgba(99,102,241,.04) !important;
}

/* ─── Buttons ─────────────────────────────────────────────────────────── */
div[data-testid="stButton"] > button {
    width: 100%;
    background: linear-gradient(135deg, #5a5fdb 0%, #9b44e8 100%);
    color: white; font-family: 'Syne', sans-serif;
    font-size: 15px; font-weight: 700; letter-spacing: .8px;
    border: none; border-radius: 14px;
    padding: 14px 28px; height: auto;
    box-shadow: 0 4px 24px rgba(99,102,241,.38);
    transition: all .2s ease;
}
div[data-testid="stButton"] > button:hover {
    background: linear-gradient(135deg, #4548c7 0%, #8226d4 100%);
    box-shadow: 0 8px 32px rgba(99,102,241,.55);
    transform: translateY(-2px);
}
div[data-testid="stButton"] > button:active { transform: translateY(0); }

/* Ghost button (secondary) */
.ghost-btn div[data-testid="stButton"] > button {
    background: rgba(255,255,255,.05) !important;
    border: 1px solid rgba(255,255,255,.1) !important;
    color: #4a5878 !important; font-size: 13px !important;
    box-shadow: none !important; letter-spacing: 0 !important;
}
.ghost-btn div[data-testid="stButton"] > button:hover {
    background: rgba(255,255,255,.09) !important;
    transform: none !important; box-shadow: none !important;
}

/* ─── Subject cards ───────────────────────────────────────────────────── */
.subj-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; margin: 18px 0; }
.subj-grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 18px; }
.s-card {
    background: rgba(255,255,255,.03);
    border: 1.5px solid rgba(255,255,255,.08);
    border-radius: 18px; padding: 22px 14px;
    text-align: center; cursor: pointer;
    transition: all .25s ease;
}
.s-card:hover {
    border-color: rgba(99,102,241,.5);
    background: rgba(99,102,241,.07);
    transform: translateY(-4px);
    box-shadow: 0 10px 32px rgba(99,102,241,.18);
}
.s-card.sel {
    border-color: rgba(168,85,247,.75);
    background: rgba(168,85,247,.1);
    box-shadow: 0 0 0 3px rgba(168,85,247,.2), 0 10px 32px rgba(168,85,247,.15);
}
.s-icon { font-size: 38px; line-height: 1; margin-bottom: 10px; }
.s-name {
    font-family: 'Syne', sans-serif; font-size: 15px;
    font-weight: 800; color: #e2e8f0; margin-bottom: 4px;
}
.s-desc { font-size: 11px; color: #3d5070; font-weight: 500; }

/* ─── User badge ────────────────────────────────────────────────────── */
.ubadge {
    display: flex; align-items: center; gap: 12px;
    background: rgba(255,255,255,.03);
    border: 1px solid rgba(255,255,255,.07);
    border-radius: 14px; padding: 11px 18px; margin-bottom: 22px;
}
.uavatar {
    width: 36px; height: 36px; border-radius: 50%; flex-shrink: 0;
    background: linear-gradient(135deg,#6366f1,#a855f7);
    display: flex; align-items: center; justify-content: center;
    font-family: 'Syne', sans-serif; font-weight: 900;
    font-size: 14px; color: white;
}
.uname { font-weight: 600; font-size: 14px; color: #dde3f0; }
.uemail { font-size: 12px; color: #2d3e5a; }

/* ─── Progress bar ──────────────────────────────────────────────────── */
.stProgress > div > div { background: rgba(255,255,255,.05) !important; border-radius: 99px !important; height: 5px !important; }
.stProgress > div > div > div > div { background: linear-gradient(90deg,#6366f1,#a855f7,#ec4899) !important; border-radius: 99px !important; }

/* ─── Timer ──────────────────────────────────────────────────────────── */
.tmr {
    border-radius: 14px; padding: 11px 20px;
    text-align: center; font-family: 'Syne', sans-serif;
    font-size: 20px; font-weight: 800; margin-bottom: 16px;
    border: 1.5px solid; letter-spacing: -.3px;
    display: flex; align-items: center; justify-content: center; gap: 10px;
}
.t-safe   { background:rgba(16,185,129,.08); border-color:rgba(16,185,129,.3); color:#34d399; }
.t-warn   { background:rgba(245,158,11,.08); border-color:rgba(245,158,11,.3); color:#fbbf24; }
.t-danger { background:rgba(239,68,68,.1);   border-color:rgba(239,68,68,.4);  color:#f87171;
    animation: pulse-red .6s ease-in-out infinite alternate; }
@keyframes pulse-red {
    from { box-shadow: 0 0 0 0 rgba(239,68,68,.0); }
    to   { box-shadow: 0 0 18px 2px rgba(239,68,68,.22); }
}

/* ─── Question card ─────────────────────────────────────────────────── */
.qcard {
    background: linear-gradient(155deg, rgba(18,26,48,.95), rgba(8,12,22,.98));
    border: 1.5px solid rgba(99,102,241,.2);
    border-radius: 22px; padding: 28px 30px;
    margin: 12px 0 20px; position: relative; overflow: hidden;
    box-shadow: 0 16px 48px rgba(0,0,0,.45), inset 0 1px 0 rgba(255,255,255,.05);
}
.qcard::before {
    content:""; position:absolute; top:0; left:0; right:0; height:3px;
    background: linear-gradient(90deg,#6366f1,#a855f7,#ec4899);
}
.qnum {
    font-size: 10px; font-weight: 700; letter-spacing: 3px;
    text-transform: uppercase; color: #5a5fdb; margin-bottom: 12px;
    display: flex; align-items: center; gap: 8px;
}
.qnum::after { content:""; flex:1; height:1px; background:rgba(99,102,241,.18); }
.qtxt {
    font-family: 'Syne', sans-serif; font-size: 20px;
    font-weight: 700; color: #f0f4ff; line-height: 1.5;
}

/* ─── Radio options ──────────────────────────────────────────────────── */
div[data-testid="stRadio"] > label { display: none; }
div[data-testid="stRadio"] > div { gap: 10px !important; flex-direction: column; }
div[data-testid="stRadio"] > div > label {
    background: rgba(255,255,255,.03) !important;
    border: 1.5px solid rgba(255,255,255,.08) !important;
    border-radius: 13px !important; padding: 13px 18px !important;
    color: #8899b8 !important; font-size: 14px !important;
    font-weight: 500 !important; transition: all .2s ease !important;
}
div[data-testid="stRadio"] > div > label:hover {
    background: rgba(99,102,241,.1) !important;
    border-color: rgba(99,102,241,.45) !important;
    color: #dde3f0 !important; transform: translateX(6px);
}
div[data-testid="stRadio"] > div > label[data-checked="true"] {
    background: rgba(99,102,241,.15) !important;
    border-color: rgba(99,102,241,.7) !important;
    color: #a5b4fc !important;
}

/* ─── Score pill ───────────────────────────────────────────────────── */
.spill {
    text-align: right; color: #7c3aed; font-family: 'Syne', sans-serif;
    font-weight: 800; font-size: 15px; padding-top: 6px; letter-spacing: -.3px;
}

/* ─── Subject pill ─────────────────────────────────────────────────── */
.subj-pill {
    display: inline-block;
    background: rgba(99,102,241,.12);
    border: 1px solid rgba(99,102,241,.3);
    color: #818cf8; font-size: 11px; font-weight: 700;
    letter-spacing: 1.5px; text-transform: uppercase;
    padding: 5px 16px; border-radius: 99px; margin-bottom: 12px;
}

/* ─── Metrics ───────────────────────────────────────────────────────── */
div[data-testid="stMetric"] {
    background: rgba(255,255,255,.03);
    border: 1px solid rgba(255,255,255,.07);
    border-radius: 16px; padding: 18px 12px; text-align: center;
}
div[data-testid="stMetric"] label {
    color: #2d3e5a !important; font-size: 10px !important;
    letter-spacing: 2px; text-transform: uppercase; font-weight: 700;
}
div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    font-family: 'Syne', sans-serif;
    font-size: 28px !important; font-weight: 900 !important; color: #f0f4ff !important;
}

/* ─── Expander ─────────────────────────────────────────────────────── */
details {
    background: rgba(255,255,255,.02) !important;
    border: 1px solid rgba(255,255,255,.07) !important;
    border-radius: 14px !important; overflow: hidden;
}
details summary {
    color: #4a5878 !important; font-weight: 600 !important;
    padding: 12px 16px !important; font-size: 14px !important;
}

/* ─── Mistake cards ─────────────────────────────────────────────────── */
.mk { background:rgba(239,68,68,.07); border:1px solid rgba(239,68,68,.22);
    border-radius:12px; padding:14px 18px; margin:8px 0; }
.mk-q  { color:#64748b; font-size:13px; margin-bottom:5px; line-height:1.5; }
.mk-u  { color:#fca5a5; font-size:13px; margin-bottom:2px; }
.mk-c  { color:#86efac; font-size:13px; font-weight:600; }

/* ─── Result hero ───────────────────────────────────────────────────── */
.res-hero { text-align:center; padding:28px 0 12px; }
.res-emoji { font-size:72px; line-height:1; margin-bottom:10px; }
.res-grade { font-family:'Syne',sans-serif; font-size:34px; font-weight:900; margin-bottom:6px; }
.res-msg { color:#2d3e5a; font-size:15px; }
.h-divider {
    height:1px;
    background:linear-gradient(90deg,transparent,rgba(99,102,241,.35),transparent);
    margin:26px 0;
}

/* ─── Comprehension box ─────────────────────────────────────────────── */
.comp-box {
    background: rgba(99,102,241,.06);
    border: 1px solid rgba(99,102,241,.2);
    border-left: 3px solid #6366f1;
    border-radius: 0 12px 12px 0;
    padding: 16px 20px; margin: 12px 0 18px;
    font-size: 14px; line-height: 1.8; color: #8899b8;
    font-style: italic;
}

/* ─── Alerts ────────────────────────────────────────────────────────── */
div[data-testid="stAlert"] { border-radius: 12px !important; }
</style>

<div class="orb-a"></div>
<div class="orb-b"></div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# QUESTION BANK — India-focused
# ══════════════════════════════════════════════════════════════════════════════
QUESTION_BANK = {
    "History": {
        "icon": "📜", "color": "#f59e0b", "desc": "India & the world",
        "questions": [
            {"question": "In which year did India gain independence from British rule?",
             "options": {"A": "1945", "B": "1946", "C": "1947", "D": "1948"},
             "answer": "C"},
            {"question": "Who is known as the 'Father of the Indian Nation'?",
             "options": {"A": "Jawaharlal Nehru", "B": "Sardar Patel", "C": "B.R. Ambedkar", "D": "Mahatma Gandhi"},
             "answer": "D"},
            {"question": "The Indian National Congress was founded in which year?",
             "options": {"A": "1875", "B": "1885", "C": "1895", "D": "1905"},
             "answer": "B"},
            {"question": "The Battle of Plassey (1757) was fought between the British East India Company and the Nawab of —",
             "options": {"A": "Mysore", "B": "Hyderabad", "C": "Bengal", "D": "Maratha"},
             "answer": "C"},
            {"question": "World War II ended in which year? (International)",
             "options": {"A": "1943", "B": "1944", "C": "1945", "D": "1946"},
             "answer": "C"},
        ]
    },
    "Geography": {
        "icon": "🌍", "color": "#10b981", "desc": "India, planets & beyond",
        "questions": [
            {"question": "Which is the longest river in India?",
             "options": {"A": "Yamuna", "B": "Brahmaputra", "C": "Godavari", "D": "Ganga"},
             "answer": "D"},
            {"question": "Which planet is known as the 'Red Planet'?",
             "options": {"A": "Jupiter", "B": "Venus", "C": "Mars", "D": "Saturn"},
             "answer": "C"},
            {"question": "The Thar Desert is primarily located in which Indian state?",
             "options": {"A": "Gujarat", "B": "Rajasthan", "C": "Punjab", "D": "Haryana"},
             "answer": "B"},
            {"question": "Which planet has the most moons in our solar system?",
             "options": {"A": "Jupiter", "B": "Uranus", "C": "Neptune", "D": "Saturn"},
             "answer": "D"},
            {"question": "The Siachen Glacier, the world's highest battlefield, is in which Indian state/UT?",
             "options": {"A": "Himachal Pradesh", "B": "Uttarakhand", "C": "Ladakh", "D": "Sikkim"},
             "answer": "C"},
        ]
    },
    "Politics": {
        "icon": "🏛️", "color": "#6366f1", "desc": "Easy civics everyone knows",
        "questions": [
            {"question": "Who is the President of India as per the Constitution?",
             "options": {"A": "Prime Minister", "B": "Chief Justice", "C": "Head of State", "D": "Speaker"},
             "answer": "C"},
            {"question": "How many members are in the Lok Sabha (maximum strength)?",
             "options": {"A": "250", "B": "545", "C": "552", "D": "543"},
             "answer": "C"},
            {"question": "Which is the supreme law of India?",
             "options": {"A": "IPC", "B": "Constitution", "C": "CrPC", "D": "Parliament Acts"},
             "answer": "B"},
            {"question": "In which year was the Indian Constitution adopted?",
             "options": {"A": "1947", "B": "1948", "C": "1949", "D": "1950"},
             "answer": "C"},
            {"question": "Who was the first Prime Minister of India?",
             "options": {"A": "Sardar Patel", "B": "Jawaharlal Nehru", "C": "Rajendra Prasad", "D": "Lal Bahadur Shastri"},
             "answer": "B"},
        ]
    },
    "Biology": {
        "icon": "🔬", "color": "#ec4899", "desc": "Life & living systems",
        "questions": [
            {"question": "What is the powerhouse of the cell?",
             "options": {"A": "Nucleus", "B": "Ribosome", "C": "Mitochondria", "D": "Golgi body"},
             "answer": "C"},
            {"question": "DNA stands for —",
             "options": {"A": "Deoxyribonucleic Acid", "B": "Dioxynucleic Acid",
                         "C": "Deoxyribose Nitrogen Acid", "D": "Double Nitrogen Acid"},
             "answer": "A"},
            {"question": "How many chromosomes does a healthy human cell contain?",
             "options": {"A": "23", "B": "44", "C": "46", "D": "48"},
             "answer": "C"},
            {"question": "Which blood type is the universal donor?",
             "options": {"A": "AB+", "B": "O+", "C": "O−", "D": "A−"},
             "answer": "C"},
            {"question": "Photosynthesis primarily occurs in which organelle?",
             "options": {"A": "Mitochondria", "B": "Vacuole", "C": "Chloroplast", "D": "Nucleus"},
             "answer": "C"},
        ]
    },
    "English": {
        "icon": "✍️", "color": "#f472b6", "desc": "Comprehension, synonyms & idioms",
        "passage": (
            "Riya had always been fascinated by the night sky. Every evening she would climb "
            "to the rooftop of her small house in Jaipur, armed with a battered notebook and a "
            "pencil, and stare into the vast darkness above. Her neighbours thought she was peculiar, "
            "but Riya did not mind. She believed that patience was the first lesson the universe "
            "taught, and that every star had a story waiting to be told."
        ),
        "questions": [
            {
                "question": "[Comprehension] Where did Riya go every evening to observe the sky?",
                "options": {"A": "A hilltop garden", "B": "The rooftop of her house",
                            "C": "A nearby observatory", "D": "Her balcony"},
                "answer": "B",
                "comp": True
            },
            {
                "question": "[Comprehension] What did Riya's neighbours think of her habit?",
                "options": {"A": "They admired her", "B": "They joined her",
                            "C": "They thought she was peculiar", "D": "They ignored her"},
                "answer": "C",
                "comp": True
            },
            {
                "question": "[Comprehension] What lesson did Riya believe the universe taught first?",
                "options": {"A": "Curiosity", "B": "Patience", "C": "Discipline", "D": "Courage"},
                "answer": "B",
                "comp": True
            },
            {
                "question": "[Synonym] Choose the best synonym for 'Peculiar':",
                "options": {"A": "Ordinary", "B": "Cheerful", "C": "Strange", "D": "Polite"},
                "answer": "C",
                "comp": False
            },
            {
                "question": "[Idiom] 'Hit the books' means —",
                "options": {"A": "Throw books away", "B": "Study hard",
                            "C": "Damage books", "D": "Visit a library"},
                "answer": "B",
                "comp": False
            },
        ]
    },
}

SUBJECTS      = list(QUESTION_BANK.keys())
TIMER_SECONDS = 12

# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def valid_email(e):
    return bool(re.match(r"^[\w\.\+\-]+@[\w\-]+\.[a-zA-Z]{2,}$", e.strip()))

def valid_pw(p):
    return len(p) >= 6

def initials(email):
    n = email.split("@")[0]
    parts = re.split(r"[.\-_]", n)
    return "".join(p[0].upper() for p in parts if p)[:2] or "U"

def full_reset():
    for k in list(st.session_state.keys()):
        del st.session_state[k]

def quiz_reset():
    for k in ["question_index","score","wrong_answers","start_time"]:
        st.session_state.pop(k, None)
    for k in [k for k in st.session_state if isinstance(k,str) and k.startswith("q_")]:
        del st.session_state[k]

# ── UI components ──────────────────────────────────────────────────────────
def render_brand():
    st.markdown('<div class="brand-wrap"><span class="brand-logo">BrainBlitz</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-tag">Personalised Knowledge Challenge</div>', unsafe_allow_html=True)

def render_steps(current):
    labels = ["Login","Subject","Quiz","Result"]
    icons  = ["🔐","📚","⚡","🏆"]
    html   = '<div class="stepbar">'
    for i, (lbl, icon) in enumerate(zip(labels, icons)):
        cls = "done" if i < current else ("active" if i == current else "idle")
        html += f'<div class="step-item"><div class="step-circle {cls}">{icon}</div><div class="step-label {cls}">{lbl}</div></div>'
        if i < len(labels)-1:
            lc = "done" if i < current else ""
            html += f'<div class="step-line {lc}"></div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

def render_badge():
    email = st.session_state.get("email","")
    av    = initials(email)
    name  = email.split("@")[0].replace(".", " ").replace("_"," ").title()
    subj  = st.session_state.get("subject","")
    subj_tag = f'&nbsp;·&nbsp;<span style="color:#a855f7;font-size:11px;font-weight:700">{QUESTION_BANK[subj]["icon"]} {subj}</span>' if subj else ""
    st.markdown(f"""
    <div class="ubadge">
        <div class="uavatar">{av}</div>
        <div style="flex:1">
            <div class="uname">{name}{subj_tag}</div>
            <div class="uemail">{email}</div>
        </div>
    </div>""", unsafe_allow_html=True)

# ── Init ───────────────────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "login"

# ══════════════════════════════════════════════════════════════════════════════
# PAGE — LOGIN
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "login":
    render_brand()
    render_steps(0)

    # ── Hero banner (replaces the empty blue bar) ────────────────────────────
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, rgba(99,102,241,.15) 0%, rgba(168,85,247,.12) 50%, rgba(236,72,153,.10) 100%);
        border: 1px solid rgba(99,102,241,.25);
        border-radius: 20px;
        padding: 22px 28px;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        gap: 18px;
        box-shadow: inset 0 1px 0 rgba(255,255,255,.07);
    ">
        <div style="font-size:48px;line-height:1">🧠</div>
        <div>
            <div style="font-family:'Syne',sans-serif;font-size:18px;font-weight:800;color:#e2e8f0;margin-bottom:4px;">
                Ready to challenge your mind?
            </div>
            <div style="font-size:13px;color:#3d5070;line-height:1.6;">
                Sign in · Pick a subject · Answer 5 timed MCQs · Track your score
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Card top ─────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="login-header">
        <div class="section-chip">🔐 Sign In</div>
        <div class="login-title">Welcome, challenger!</div>
        <div class="login-sub">Enter your email and password to begin your personalised quiz journey.</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Streamlit inputs (must be outside html divs) ─────────────────────────
    with st.container():
        st.markdown('<div style="padding: 0 0 0 0;">', unsafe_allow_html=True)
        email    = st.text_input("Email Address", placeholder="yourname@example.com", key="li_email")
        password = st.text_input("Password", type="password", placeholder="Minimum 6 characters", key="li_pw")
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Card bottom ───────────────────────────────────────────────────────────
    st.markdown("""
    <div class="login-footer">
        <div class="divider-line"></div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Continue to Subject →", use_container_width=True):
        e = email.strip()
        if not e or not password:
            st.error("⚠️  Both fields are required.")
        elif not valid_email(e):
            st.error("⚠️  Enter a valid email — e.g. name@gmail.com")
        elif not valid_pw(password):
            st.error("⚠️  Password must be at least 6 characters.")
        else:
            st.session_state.email = e
            st.session_state.page  = "subject"
            st.rerun()

    st.markdown("""
    <div class="trust-note" style="margin-top:14px;">
        🛡️ Credentials stay in your browser session only — never stored anywhere.
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE — SUBJECT SELECTION
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "subject":
    render_brand()
    render_steps(1)
    render_badge()

    st.markdown("""
    <div style="margin-bottom:6px;">
        <div class="section-chip">📚 Pick Your Subject</div>
    </div>
    <div style="font-family:'Syne',sans-serif;font-size:22px;font-weight:800;color:#f0f4ff;margin-bottom:6px;">
        What do you want to be tested on?
    </div>
    <div style="color:#2d3e5a;font-size:14px;margin-bottom:20px;">
        Choose wisely — you'll get <strong style="color:#6366f1;">5 subject-specific MCQs</strong>
        with a <strong style="color:#f59e0b;">12-second countdown</strong> per question.
    </div>
    """, unsafe_allow_html=True)

    chosen = st.session_state.get("subject_pick", None)

    # 3-column + 2-column grid
    row1 = st.columns(3)
    row2 = st.columns(2)
    grid = list(zip([*row1, *row2], SUBJECTS))

    for col, subj in grid:
        info   = QUESTION_BANK[subj]
        sel_c  = "sel" if chosen == subj else ""
        with col:
            st.markdown(f"""
            <div class="s-card {sel_c}">
                <div class="s-icon">{info['icon']}</div>
                <div class="s-name">{subj}</div>
                <div class="s-desc">{info['desc']}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"{'✓ ' if chosen==subj else ''}{subj}", key=f"pick_{subj}", use_container_width=True):
                st.session_state.subject_pick = subj
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    if chosen:
        info = QUESTION_BANK[chosen]
        st.success(f"{info['icon']}  **{chosen}** selected — Let's test your knowledge!")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(f"🚀  Start {chosen} Quiz →", use_container_width=True):
            st.session_state.subject = chosen
            quiz_reset()
            st.session_state.question_index = 0
            st.session_state.score          = 0
            st.session_state.wrong_answers  = []
            st.session_state.start_time     = time.time()
            st.session_state.page           = "quiz"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
        if st.button("← Log out"):
            full_reset()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE — QUIZ
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "quiz":
    subj  = st.session_state.subject
    info  = QUESTION_BANK[subj]
    qs    = info["questions"]
    total = len(qs)
    idx   = st.session_state.get("question_index", 0)

    if idx >= total:
        st.session_state.page = "result"
        st.rerun()

    q = qs[idx]

    render_brand()
    render_steps(2)
    render_badge()

    # ── Progress + score ──────────────────────────────────────────────────────
    pc, sc = st.columns([5, 1])
    with pc: st.progress(idx / total)
    with sc: st.markdown(f'<div class="spill">⚡{st.session_state.score}</div>', unsafe_allow_html=True)

    # ── Timer ──────────────────────────────────────────────────────────────────
    remaining = TIMER_SECONDS - int(time.time() - st.session_state.start_time)
    if   remaining > 7: tc, ti = "t-safe",   "🟢"
    elif remaining > 4: tc, ti = "t-warn",   "🟡"
    else:               tc, ti = "t-danger", "🔴"

    st.markdown(
        f'<div class="tmr {tc}">{ti}&nbsp;&nbsp;{max(remaining,0)} seconds remaining</div>',
        unsafe_allow_html=True
    )

    # ── Auto-skip ──────────────────────────────────────────────────────────────
    if remaining <= 0:
        ca = q["answer"]
        st.session_state.wrong_answers.append({
            "question":    q["question"],
            "your_answer": "⏰ Time up — skipped",
            "correct":     f"{ca} → {q['options'][ca]}",
        })
        st.session_state.question_index += 1
        st.session_state.start_time      = time.time()
        st.rerun()

    # ── Subject pill ───────────────────────────────────────────────────────────
    st.markdown(f'<div class="subj-pill">{info["icon"]} {subj}</div>', unsafe_allow_html=True)

    # ── Comprehension passage (English only) ───────────────────────────────────
    if subj == "English" and q.get("comp") and "passage" in info:
        st.markdown(
            f'<div class="comp-box">📖 <strong>Read the passage:</strong><br><br>{info["passage"]}</div>',
            unsafe_allow_html=True
        )

    # ── Question card ──────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="qcard">
        <div class="qnum">Question {idx+1} of {total}</div>
        <div class="qtxt">{q['question']}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Answer options ─────────────────────────────────────────────────────────
    selected = st.radio(
        "Your answer",
        list(q["options"].keys()),
        format_func=lambda k: f"  {k}  ·  {q['options'][k]}",
        index=None,
        key=f"q_{idx}"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    _, bc, _ = st.columns([1, 3, 1])
    with bc:
        if st.button("Submit Answer →", use_container_width=True):
            if selected is None:
                st.warning("⚠️  Please select an option first.")
            else:
                if selected == q["answer"]:
                    st.success("✅  Correct!  Great job!")
                    st.session_state.score += 1
                else:
                    ca = q["answer"]
                    st.error(f"❌  Wrong!  Correct: **{ca} → {q['options'][ca]}**")
                    st.session_state.wrong_answers.append({
                        "question":    q["question"],
                        "your_answer": f"{selected} → {q['options'][selected]}",
                        "correct":     f"{ca} → {q['options'][ca]}",
                    })
                time.sleep(1.2)
                st.session_state.question_index += 1
                st.session_state.start_time      = time.time()
                st.rerun()

    # ── Refresh every second for live timer ────────────────────────────────────
    time.sleep(1)
    st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE — RESULT
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "result":
    subj        = st.session_state.subject
    info        = QUESTION_BANK[subj]
    fs          = st.session_state.score
    total       = len(info["questions"])
    pct         = (fs / total) * 100
    wrongs      = st.session_state.wrong_answers

    render_brand()
    render_steps(3)
    render_badge()

    st.balloons()

    if pct == 100:
        em,gr,ms,cl = "🏆","Perfect Score!","Absolutely flawless — you're a legend!","#fbbf24"
    elif pct >= 80:
        em,gr,ms,cl = "🌟","Excellent!","Outstanding performance!","#34d399"
    elif pct >= 60:
        em,gr,ms,cl = "👍","Good Job!","Solid effort — keep pushing.","#60a5fa"
    else:
        em,gr,ms,cl = "💪","Keep Practising!","Review & come back stronger!","#f87171"

    st.markdown(f"""
    <div class="res-hero">
        <div class="res-emoji">{em}</div>
        <div class="res-grade" style="color:{cl};">{gr}</div>
        <div class="res-msg">{ms}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f'<div class="subj-pill">{info["icon"]} {subj}</div>', unsafe_allow_html=True)
    st.progress(fs / total)
    st.markdown("<br>", unsafe_allow_html=True)

    c1,c2,c3,c4 = st.columns(4)
    with c1: st.metric("✅ Correct", fs)
    with c2: st.metric("❌ Wrong",   total-fs)
    with c3: st.metric("📊 Score",   f"{pct:.0f}%")
    with c4: st.metric("❓ Total",   total)

    st.markdown('<div class="h-divider"></div>', unsafe_allow_html=True)

    if wrongs:
        with st.expander(f"📋  Review mistakes  ({len(wrongs)} wrong)"):
            for i, w in enumerate(wrongs, 1):
                st.markdown(f"""
                <div class="mk">
                    <div class="mk-q">Q{i}: {w['question']}</div>
                    <div class="mk-u">Your answer: {w['your_answer']}</div>
                    <div class="mk-c">✓ Correct: {w['correct']}</div>
                </div>""", unsafe_allow_html=True)
    else:
        st.success("🔥  Zero mistakes — you aced every question!")

    st.markdown("<br>", unsafe_allow_html=True)

    a, b, c = st.columns(3)
    with a:
        if st.button("🔄  Retry Same", use_container_width=True):
            quiz_reset()
            st.session_state.question_index = 0
            st.session_state.score          = 0
            st.session_state.wrong_answers  = []
            st.session_state.start_time     = time.time()
            st.session_state.page           = "quiz"
            st.rerun()
    with b:
        if st.button("📚  New Subject", use_container_width=True):
            quiz_reset()
            st.session_state.pop("subject_pick", None)
            st.session_state.pop("subject", None)
            st.session_state.page = "subject"
            st.rerun()
    with c:
        if st.button("🚪  Log Out", use_container_width=True):
            full_reset()
            st.rerun()
