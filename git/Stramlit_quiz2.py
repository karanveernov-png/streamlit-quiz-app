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

/* ─── Inputs ─────────────────────────────────────────────────────────── */
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

/* ─── ALL Buttons ─────────────────────────────────────── */
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
.xp-tally { font-size: 15px; color: #fbbf24; font-weight: 700; }
</style>
<div class="orb-a"></div>
<div class="orb-b"></div>
''', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# MULTI-TIER QUESTION BANK
# ══════════════════════════════════════════════════════════════════════════════
QUESTION_BANK = {
    "History": {
        "icon": "📜", "color": "#f59e0b", "desc": "India & the world",
        "questions": {
            "Easy": [
                {"question": "In which year did India gain independence from British rule?", "options": {"A": "1945", "B": "1946", "C": "1947", "D": "1948"}, "answer": "C", "explanation": "India officially gained independence on August 15, 1947."},
                {"question": "Who is known as the 'Father of the Indian Nation'?", "options": {"A": "Jawaharlal Nehru", "B": "Bhagat Singh", "C": "B.R. Ambedkar", "D": "Mahatma Gandhi"}, "answer": "D", "explanation": "Mahatma Gandhi led the non-violent freedom struggle in India."},
                {"question": "[World] World War II officially ended in which year?", "options": {"A": "1943", "B": "1944", "C": "1945", "D": "1946"}, "answer": "C", "explanation": "WWII ended in 1945 following the surrender of Axis powers."},
                {"question": "Who built the Taj Mahal in Agra?", "options": {"A": "Akbar", "B": "Shah Jahan", "C": "Aurangzeb", "D": "Babur"}, "answer": "B", "explanation": "Mughal Emperor Shah Jahan commissioned the Taj Mahal for his wife Mumtaz."},
                {"question": "Who was the first President of independent India?", "options": {"A": "Sardar Patel", "B": "Dr. Rajendra Prasad", "C": "Dr. S. Radhakrishnan", "D": "Jawaharlal Nehru"}, "answer": "B", "explanation": "Dr. Rajendra Prasad served as the first President of India from 1950 to 1962."}
            ],
            "Medium": [
                {"question": "In which year was the 'Quit India Movement' launched?", "options": {"A": "1930", "B": "1942", "C": "1945", "D": "1947"}, "answer": "B", "explanation": "Mahatma Gandhi launched the Quit India Movement in August 1942 at the Gowalia Tank Maidan."},
                {"question": "[World] In which year did the French Revolution begin?", "options": {"A": "1776", "B": "1789", "C": "1812", "D": "1848"}, "answer": "B", "explanation": "The French Revolution began in 1789 with the storming of the Bastille."},
                {"question": "Which historic battle in 1526 marked the beginning of the Mughal Empire in India?", "options": {"A": "Battle of Buxar", "B": "First Battle of Panipat", "C": "Battle of Haldighati", "D": "Battle of Plassey"}, "answer": "B", "explanation": "Babur defeated Ibrahim Lodi in the First Battle of Panipat in 1526."},
                {"question": "Which great warrior king is known as the founder of the Maratha Empire and the father of the Indian Navy?", "options": {"A": "Rana Pratap", "B": "Chhatrapati Shivaji Maharaj", "C": "Baji Rao I", "D": "Tipu Sultan"}, "answer": "B", "explanation": "Shivaji Maharaj laid the foundation of the Maratha Empire and built a formidable naval fleet."},
                {"question": "The Gateway of India in Mumbai was built to commemorate the visit of which British monarch?", "options": {"A": "Queen Victoria", "B": "King George V", "C": "King Edward VII", "D": "Queen Elizabeth II"}, "answer": "B", "explanation": "It was built to commemorate the 1911 royal visit of King George V and Queen Mary."}
            ],
            "Hard": [
                {"question": "The tragic Jallianwala Bagh massacre took place on which exact date?", "options": {"A": "April 13, 1919", "B": "March 23, 1931", "C": "August 15, 1947", "D": "January 26, 1930"}, "answer": "A", "explanation": "General Dyer ordered troops to fire on a peaceful gathering on April 13, 1919, in Amritsar."},
                {"question": "[World] The collapse of the Soviet Union (USSR), marking the end of the Cold War, occurred in?", "options": {"A": "1989", "B": "1991", "C": "1993", "D": "1995"}, "answer": "B", "explanation": "The USSR officially dissolved on December 26, 1991."},
                {"question": "Who was the founder of the Indian National Army (Azad Hind Fauj) before Subhas Chandra Bose took command?", "options": {"A": "Captain Mohan Singh", "B": "Rash Behari Bose", "C": "Bhagat Singh", "D": "Chandrashekhar Azad"}, "answer": "A", "explanation": "Captain Mohan Singh originally formed the INA with Indian POWs in 1942."},
                {"question": "Which ancient ruler defeated the Greek king Seleucus Nicator?", "options": {"A": "King Porus", "B": "Chandragupta Maurya", "C": "Ashoka", "D": "Samudragupta"}, "answer": "B", "explanation": "Chandragupta Maurya defeated Seleucus Nicator, securing the northwestern borders of India."},
                {"question": "The Chola dynasty is famous for its powerful navy. Which Chola king conquered parts of Southeast Asia?", "options": {"A": "Aditya Chola", "B": "Rajaraja Chola I", "C": "Rajendra Chola I", "D": "Karikala Chola"}, "answer": "C", "explanation": "Rajendra Chola I expanded the empire overseas, using his navy to conquer Srivijaya (modern Indonesia/Malaysia)."}
            ]
        }
    },
    "Geography": {
        "icon": "🌍", "color": "#10b981", "desc": "India, planets & beyond",
        "questions": {
            "Easy": [
                {"question": "Which is the longest river flowing entirely within India?", "options": {"A": "Yamuna", "B": "Brahmaputra", "C": "Godavari", "D": "Ganga"}, "answer": "D", "explanation": "The Ganga flows for over 2,500 km within Indian territory."},
                {"question": "[World] Which planet in our solar system is known as the 'Red Planet'?", "options": {"A": "Jupiter", "B": "Venus", "C": "Mars", "D": "Saturn"}, "answer": "C", "explanation": "Mars appears red due to the abundance of iron oxide (rust) on its surface."},
                {"question": "The Indian state of Punjab is famously known as the 'Land of ____ Rivers'.", "options": {"A": "Three", "B": "Five", "C": "Seven", "D": "Nine"}, "answer": "B", "explanation": "Punjab translates to 'Land of Five Rivers' (Sutlej, Beas, Ravi, Chenab, Jhelum)."},
                {"question": "Which Indian state primarily hosts the harsh and arid Thar Desert?", "options": {"A": "Gujarat", "B": "Rajasthan", "C": "Punjab", "D": "Haryana"}, "answer": "B", "explanation": "The Thar Desert is predominantly located in Rajasthan."},
                {"question": "How many states does India currently have?", "options": {"A": "27", "B": "28", "C": "29", "D": "30"}, "answer": "B", "explanation": "India currently has 28 States and 8 Union Territories."}
            ],
            "Medium": [
                {"question": "Which is the largest brackish water lake in India?", "options": {"A": "Wular Lake", "B": "Dal Lake", "C": "Chilika Lake", "D": "Vembanad Lake"}, "answer": "C", "explanation": "Chilika Lake in Odisha is the largest coastal lagoon in India."},
                {"question": "[World] The Equator passes through which of these continents?", "options": {"A": "Europe", "B": "North America", "C": "Africa", "D": "Antarctica"}, "answer": "C", "explanation": "The Equator passes through South America, Africa, and Asia."},
                {"question": "Which is the highest mountain peak located fully in undisputed Indian territory?", "options": {"A": "K2 (Godwin Austen)", "B": "Mount Everest", "C": "Nanda Devi", "D": "Kanchenjunga"}, "answer": "D", "explanation": "Kanchenjunga is the highest peak in India (Sikkim). Nanda Devi is the highest located *entirely* within India, but Kanchenjunga is standardly recognized as India's highest."},
                {"question": "Majuli, the world's largest river island, is located in which river?", "options": {"A": "Ganga", "B": "Brahmaputra", "C": "Godavari", "D": "Narmada"}, "answer": "B", "explanation": "Majuli island is situated in the Brahmaputra River in Assam."},
                {"question": "Which type of soil is most suitable for growing cotton in India?", "options": {"A": "Red Soil", "B": "Alluvial Soil", "C": "Laterite Soil", "D": "Black Soil (Regur)"}, "answer": "D", "explanation": "Black soil is ideal for cotton due to its high moisture retention capacity."}
            ],
            "Hard": [
                {"question": "The Siachen Glacier, known as the world's highest militarized zone, is located in which mountain range?", "options": {"A": "Pir Panjal", "B": "Karakoram", "C": "Zanskar", "D": "Dhauladhar"}, "answer": "B", "explanation": "Siachen is in the eastern Karakoram range in the Himalayas."},
                {"question": "[World] The 'Ring of Fire', known for earthquakes and volcanoes, is located in which ocean?", "options": {"A": "Atlantic Ocean", "B": "Indian Ocean", "C": "Pacific Ocean", "D": "Arctic Ocean"}, "answer": "C", "explanation": "The Ring of Fire forms a massive horseshoe shape around the Pacific Ocean."},
                {"question": "India's only active volcano is located in which island group?", "options": {"A": "Lakshadweep", "B": "Barren Island (Andaman)", "C": "Minicoy", "D": "Majuli"}, "answer": "B", "explanation": "Barren Island in the Andaman Sea is home to South Asia's only active volcano."},
                {"question": "The Standard Meridian of India (82°30' E) passes through which of these cities?", "options": {"A": "Bhopal", "B": "Mirzapur", "C": "Patna", "D": "Nagpur"}, "answer": "B", "explanation": "The Standard Meridian passes through Mirzapur in Uttar Pradesh."},
                {"question": "Which Himalayan pass connects the Kashmir Valley with the Ladakh region?", "options": {"A": "Rohtang Pass", "B": "Nathu La", "C": "Zoji La", "D": "Shipki La"}, "answer": "C", "explanation": "Zoji La is a high mountain pass providing vital connectivity to Ladakh."}
            ]
        }
    },
    "Politics": {
        "icon": "🏛️", "color": "#6366f1", "desc": "Easy civics everyone knows",
        "questions": {
            "Easy": [
                {"question": "Who is the Constitutional Head of State in India?", "options": {"A": "Prime Minister", "B": "Chief Justice", "C": "President", "D": "Speaker of Lok Sabha"}, "answer": "C", "explanation": "The President is the Head of State and the Supreme Commander of the Armed Forces."},
                {"question": "In which year did the Constitution of India formally come into effect?", "options": {"A": "1947", "B": "1949", "C": "1950", "D": "1952"}, "answer": "C", "explanation": "The Constitution came into effect on January 26, 1950 (Republic Day)."},
                {"question": "[World] Where is the headquarters of the United Nations (UN) located?", "options": {"A": "Geneva", "B": "London", "C": "Paris", "D": "New York"}, "answer": "D", "explanation": "The UN Headquarters is located in New York City, USA."},
                {"question": "Which Article of the Indian Constitution, granting special status to Jammu & Kashmir, was abrogated in 2019?", "options": {"A": "Article 356", "B": "Article 370", "C": "Article 21", "D": "Article 44"}, "answer": "B", "explanation": "Article 370 was revoked, restructuring the state into two Union Territories."},
                {"question": "Who was the first Prime Minister of independent India?", "options": {"A": "Sardar Patel", "B": "Jawaharlal Nehru", "C": "B.R. Ambedkar", "D": "Lal Bahadur Shastri"}, "answer": "B", "explanation": "Jawaharlal Nehru served as the first Prime Minister from 1947 to 1964."}
            ],
            "Medium": [
                {"question": "What is the minimum age requirement to become a member of the Lok Sabha?", "options": {"A": "18 years", "B": "21 years", "C": "25 years", "D": "30 years"}, "answer": "C", "explanation": "Article 84(b) sets the minimum age for Lok Sabha MPs at 25 years."},
                {"question": "Fundamental Rights are enshrined in which Part of the Indian Constitution?", "options": {"A": "Part II", "B": "Part III", "C": "Part IV", "D": "Part V"}, "answer": "B", "explanation": "Part III (Articles 12 to 35) guarantees Fundamental Rights to citizens."},
                {"question": "[World] Which of these countries is NOT a permanent veto-wielding member of the UN Security Council?", "options": {"A": "France", "B": "Russia", "C": "India", "D": "China"}, "answer": "C", "explanation": "India is not a permanent member. The P5 are US, UK, France, Russia, and China."},
                {"question": "Who appoints the Chief Election Commissioner of India?", "options": {"A": "Prime Minister", "B": "Chief Justice of India", "C": "President of India", "D": "Parliament"}, "answer": "C", "explanation": "The President appoints the Chief Election Commissioner under Article 324."},
                {"question": "The Panchayati Raj system in India was introduced through which Constitutional Amendment?", "options": {"A": "42nd", "B": "44th", "C": "73rd", "D": "86th"}, "answer": "C", "explanation": "The 73rd Amendment Act (1992) gave constitutional status to Panchayati Raj institutions."}
            ],
            "Hard": [
                {"question": "Which Article was called the 'Heart and Soul of the Constitution' by Dr. B.R. Ambedkar?", "options": {"A": "Article 14", "B": "Article 19", "C": "Article 21", "D": "Article 32"}, "answer": "D", "explanation": "Article 32 provides the right to Constitutional Remedies to enforce Fundamental Rights."},
                {"question": "The concept of 'Directive Principles of State Policy' was borrowed from which country's constitution?", "options": {"A": "USA", "B": "UK", "C": "Ireland", "D": "USSR"}, "answer": "C", "explanation": "The DPSP concept was inspired by the Irish Constitution."},
                {"question": "[World] The International Court of Justice (ICJ) is located in which city?", "options": {"A": "Geneva", "B": "The Hague", "C": "Vienna", "D": "Brussels"}, "answer": "B", "explanation": "The ICJ is seated at the Peace Palace in The Hague, Netherlands."},
                {"question": "Under which Article can the President declare a National Emergency in India?", "options": {"A": "Article 352", "B": "Article 356", "C": "Article 360", "D": "Article 365"}, "answer": "A", "explanation": "Article 352 allows for National Emergency due to war, external aggression, or armed rebellion."},
                {"question": "When did the Constituent Assembly of India hold its very first session?", "options": {"A": "August 15, 1947", "B": "December 9, 1946", "C": "January 26, 1950", "D": "November 26, 1949"}, "answer": "B", "explanation": "The first session took place on December 9, 1946, before independence."}
            ]
        }
    },
    "Biology": {
        "icon": "🔬", "color": "#ec4899", "desc": "Life & living systems",
        "questions": {
            "Easy": [
                {"question": "What is generally called the 'powerhouse of the cell'?", "options": {"A": "Nucleus", "B": "Ribosome", "C": "Mitochondria", "D": "Golgi body"}, "answer": "C", "explanation": "Mitochondria generate ATP, which acts as cellular energy."},
                {"question": "Which blood type is considered the 'Universal Donor'?", "options": {"A": "AB+", "B": "O+", "C": "O−", "D": "A−"}, "answer": "C", "explanation": "O-negative blood lacks A, B, and Rh antigens, making it safe for all recipients."},
                {"question": "[World] Who discovered Penicillin, the world's first widely used antibiotic?", "options": {"A": "Louis Pasteur", "B": "Alexander Fleming", "C": "Marie Curie", "D": "Gregor Mendel"}, "answer": "B", "explanation": "Alexander Fleming discovered Penicillin in 1928."},
                {"question": "How many chambers does a normal human heart have?", "options": {"A": "Two", "B": "Three", "C": "Four", "D": "Five"}, "answer": "C", "explanation": "The human heart has four chambers: two atria and two ventricles."},
                {"question": "The traditional Indian medical system that focuses on holistic body-weight and diet balance is called:", "options": {"A": "Homeopathy", "B": "Allopathy", "C": "Ayurveda", "D": "Acupuncture"}, "answer": "C", "explanation": "Ayurveda is a historic Indian system emphasizing diet (like desi ghee and milk) and physical harmony."}
            ],
            "Medium": [
                {"question": "What is the average lifespan of a human Red Blood Cell (RBC)?", "options": {"A": "30 days", "B": "60 days", "C": "120 days", "D": "240 days"}, "answer": "C", "explanation": "RBCs circulate for about 120 days before being recycled in the spleen."},
                {"question": "Which mosquito is the primary vector for Dengue fever, a common disease in India?", "options": {"A": "Anopheles", "B": "Culex", "C": "Aedes aegypti", "D": "Mansonia"}, "answer": "C", "explanation": "Aedes mosquitoes bite during the day and transmit Dengue and Chikungunya."},
                {"question": "[World] Which molecule carries genetic instructions in all living organisms?", "options": {"A": "RNA", "B": "DNA", "C": "Protein", "D": "Lipid"}, "answer": "B", "explanation": "Deoxyribonucleic Acid (DNA) holds genetic blueprints."},
                {"question": "Which is the largest internal organ/gland in the human body?", "options": {"A": "Heart", "B": "Lungs", "C": "Liver", "D": "Kidney"}, "answer": "C", "explanation": "The liver is the largest internal organ, responsible for detoxification."},
                {"question": "Which Indian scientist proved that plants have life using a device called the Crescograph?", "options": {"A": "C.V. Raman", "B": "Homi Bhabha", "C": "Satyendra Nath Bose", "D": "Jagadish Chandra Bose"}, "answer": "D", "explanation": "J.C. Bose pioneered plant biophysics and wireless communication."}
            ],
            "Hard": [
                {"question": "In the human kidney, what is the basic structural and functional unit?", "options": {"A": "Neuron", "B": "Alveolus", "C": "Nephron", "D": "Villus"}, "answer": "C", "explanation": "Nephrons filter blood to produce urine in the kidneys."},
                {"question": "Which plant tissue is responsible for the transport of food (sugars) from leaves to other parts?", "options": {"A": "Xylem", "B": "Phloem", "C": "Epidermis", "D": "Cambium"}, "answer": "B", "explanation": "Phloem transports food, while Xylem transports water."},
                {"question": "[World] In cell division, which phase involves the separation of sister chromatids to opposite poles?", "options": {"A": "Prophase", "B": "Metaphase", "C": "Anaphase", "D": "Telophase"}, "answer": "C", "explanation": "During Anaphase, chromosomes are pulled apart."},
                {"question": "What is the scientific name of the Indian National Animal (Bengal Tiger)?", "options": {"A": "Panthera leo", "B": "Panthera tigris", "C": "Elephas maximus", "D": "Pavo cristatus"}, "answer": "B", "explanation": "Panthera tigris is the scientific name for the tiger."},
                {"question": "Which hormone, produced by the pancreas, regulates blood sugar levels?", "options": {"A": "Glucagon", "B": "Insulin", "C": "Thyroxine", "D": "Adrenaline"}, "answer": "B", "explanation": "Insulin lowers blood glucose, and its deficiency causes Diabetes."}
            ]
        }
    }
    ,
    "English": {
        "icon": "📖", "color": "#38bdf8", "desc": "Comprehension, synonyms & idioms",
        "questions": {
            "Easy": [
                {
                    "question": "Read the passage and answer:\n\n\"Riya loved reading books every evening. One day she found an old, dusty book in the attic. As she opened it, she discovered it was her grandmother's diary. She read it eagerly and felt a deep connection with her past.\"\n\nWhat did Riya find in the attic?",
                    "options": {"A": "A treasure box", "B": "Her grandmother's diary", "C": "An old photograph", "D": "A letter from a friend"},
                    "answer": "B",
                    "explanation": "The passage clearly states she found her grandmother's diary inside the old dusty book."
                },
                {
                    "question": "Based on the same passage about Riya:\n\nHow did Riya feel after reading the diary?",
                    "options": {"A": "Sad and lonely", "B": "Bored and uninterested", "C": "A deep connection with her past", "D": "Confused and puzzled"},
                    "answer": "C",
                    "explanation": "The passage says 'she felt a deep connection with her past' after reading the diary."
                },
                {
                    "question": "Based on the same passage about Riya:\n\nWhere was the old book found?",
                    "options": {"A": "In the library", "B": "In the garden", "C": "In the attic", "D": "Under her bed"},
                    "answer": "C",
                    "explanation": "The passage says Riya found the old dusty book in the attic."
                },
                {
                    "question": "[Synonym] Choose the word closest in meaning to 'HAPPY':",
                    "options": {"A": "Gloomy", "B": "Joyful", "C": "Angry", "D": "Tired"},
                    "answer": "B",
                    "explanation": "'Joyful' means full of joy and happiness, making it the closest synonym to 'happy'."
                },
                {
                    "question": "[Idiom] What does the idiom 'Break the ice' mean?",
                    "options": {"A": "To smash frozen water", "B": "To start a conversation in an awkward situation", "C": "To end a friendship", "D": "To cause trouble"},
                    "answer": "B",
                    "explanation": "'Break the ice' means to do or say something to make people feel comfortable and start talking in an awkward or tense situation."
                }
            ],
            "Medium": [
                {
                    "question": "Read the passage and answer:\n\n\"The Industrial Revolution, which began in Britain in the late 18th century, transformed society drastically. Machines replaced manual labour, cities grew rapidly, and goods were produced at an unprecedented scale. However, this came at a cost — workers, including children, toiled in dangerous conditions for long hours with little pay.\"\n\nWhen did the Industrial Revolution begin?",
                    "options": {"A": "Early 17th century", "B": "Late 18th century", "C": "Early 19th century", "D": "Mid 20th century"},
                    "answer": "B",
                    "explanation": "The passage explicitly states it began in Britain in the late 18th century."
                },
                {
                    "question": "Based on the same passage about the Industrial Revolution:\n\nWhich of these was a negative consequence mentioned in the passage?",
                    "options": {"A": "Decrease in population", "B": "Reduction in goods", "C": "Children working in dangerous conditions", "D": "Cities becoming smaller"},
                    "answer": "C",
                    "explanation": "The passage mentions workers including children toiled in dangerous conditions — a direct negative consequence."
                },
                {
                    "question": "Based on the same passage about the Industrial Revolution:\n\nWhat replaced manual labour during this period?",
                    "options": {"A": "Animals", "B": "Machines", "C": "Slaves", "D": "Foreign workers"},
                    "answer": "B",
                    "explanation": "The passage clearly states 'Machines replaced manual labour' during the Industrial Revolution."
                },
                {
                    "question": "[Synonym] Choose the word closest in meaning to 'ABUNDANT':",
                    "options": {"A": "Scarce", "B": "Plentiful", "C": "Dull", "D": "Narrow"},
                    "answer": "B",
                    "explanation": "'Plentiful' means existing in large quantities, making it the best synonym for 'abundant'."
                },
                {
                    "question": "[Idiom] What does 'Bite the bullet' mean?",
                    "options": {"A": "To eat something hard", "B": "To shoot a gun", "C": "To endure a painful situation with courage", "D": "To avoid a problem"},
                    "answer": "C",
                    "explanation": "'Bite the bullet' means to endure a painful or difficult situation stoically, accepting it as unavoidable."
                }
            ],
            "Hard": [
                {
                    "question": "Read the passage and answer:\n\n\"Existentialism, a philosophical movement that flourished in the 20th century, posits that individuals create their own meaning in an inherently meaningless universe. Thinkers like Sartre and Camus argued that humans are 'condemned to be free' — burdened with the responsibility of choice without a predetermined essence or divine blueprint. This radical freedom, they contended, inevitably produces anxiety, yet it is precisely this anxiety that compels authentic self-definition.\"\n\nAccording to the passage, what produces anxiety in humans according to existentialists?",
                    "options": {"A": "Lack of freedom", "B": "Divine intervention", "C": "Radical freedom and the burden of choice", "D": "Predetermined essence"},
                    "answer": "C",
                    "explanation": "The passage states that 'radical freedom inevitably produces anxiety' — it is the burden of unconstrained choice that causes it."
                },
                {
                    "question": "Based on the same passage about Existentialism:\n\nWhat does the phrase 'condemned to be free' imply in the context of the passage?",
                    "options": {"A": "Humans are imprisoned by freedom", "B": "Freedom is a punishment as it comes with unavoidable responsibility", "C": "Humans have no freedom at all", "D": "Freedom is a divine blessing"},
                    "answer": "B",
                    "explanation": "Sartre's phrase means freedom is not purely liberating — it burdens individuals with inescapable responsibility for their choices."
                },
                {
                    "question": "Based on the same passage about Existentialism:\n\nWhat is the role of anxiety, according to the existentialist view in the passage?",
                    "options": {"A": "It is a disease to be cured", "B": "It is irrelevant to human life", "C": "It compels authentic self-definition", "D": "It is caused by lack of choice"},
                    "answer": "C",
                    "explanation": "The passage says it is 'precisely this anxiety that compels authentic self-definition' — anxiety drives genuine personal identity."
                },
                {
                    "question": "[Synonym] Choose the word closest in meaning to 'LOQUACIOUS':",
                    "options": {"A": "Silent", "B": "Talkative", "C": "Aggressive", "D": "Secretive"},
                    "answer": "B",
                    "explanation": "'Loquacious' means tending to talk a great deal — an advanced synonym for talkative or verbose."
                },
                {
                    "question": "[Idiom] What does 'Burn the midnight oil' mean?",
                    "options": {"A": "To light candles at night", "B": "To waste resources", "C": "To work late into the night", "D": "To cause a fire"},
                    "answer": "C",
                    "explanation": "'Burn the midnight oil' means to work or study until very late at night, historically when people used oil lamps."
                }
            ]
        }
    }
}

SUBJECTS = list(QUESTION_BANK.keys())

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
    for k in ["question_index", "score", "wrong_answers", "start_time", "answered", "current_xp"]:
        st.session_state.pop(k, None)
    for k in [k for k in st.session_state if isinstance(k, str) and k.startswith("q_")]:
        del st.session_state[k]

def start_quiz(subj, difficulty, timer_sec):
    st.session_state.subject = subj
    st.session_state.difficulty = difficulty
    st.session_state.timer_seconds = timer_sec
    quiz_reset()
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
        icon = QUESTION_BANK[subj]["icon"]
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
        Harder difficulties reward more XP! Choose wisely to level up faster.
    </div>
    ''', unsafe_allow_html=True)

    chosen = st.session_state.get("subject_pick", None)

    row1 = st.columns(3)
    row2 = st.columns(3)
    grid = list(zip([*row1, *row2], SUBJECTS))

    for col, subj in grid:
        info = QUESTION_BANK[subj]
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
        info = QUESTION_BANK[chosen]
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
    
    # XP per question based on difficulty
    xp_multiplier = {"Easy": 1, "Medium": 2, "Hard": 3}[diff]
    
    info = QUESTION_BANK[subj]
    qs = info["questions"][diff]
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

        # Dynamic color coding based on the current timer
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
                    # Grant XP instantly
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
    info = QUESTION_BANK[subj]
    fs = st.session_state.score
    total = len(info["questions"][diff])
    pct = (fs / total) * 100
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

    st.progress(fs / total)
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
