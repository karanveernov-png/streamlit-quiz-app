import streamlit as st
import time

# ── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="BrainBlitz Quiz",
    page_icon="🧠",
    layout="centered"
)

# ── CUSTOM CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800;900&family=DM+Sans:wght@300;400;500;600&display=swap');

/* ── Global Reset ── */
#MainMenu, footer, header { visibility: hidden; }

html, body, .stApp {
    background: #080c14;
    font-family: 'DM Sans', sans-serif;
    color: #e2e8f0;
}

/* ── Noise/Grain overlay ── */
.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.035'/%3E%3C/svg%3E");
    pointer-events: none;
    z-index: 0;
    opacity: 0.5;
}

/* ── Ambient glow blobs ── */
.glow-orb-1 {
    position: fixed;
    width: 400px; height: 400px;
    top: -100px; right: -100px;
    background: radial-gradient(circle, rgba(99,102,241,0.18) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
    z-index: 0;
}
.glow-orb-2 {
    position: fixed;
    width: 350px; height: 350px;
    bottom: -80px; left: -80px;
    background: radial-gradient(circle, rgba(236,72,153,0.14) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
    z-index: 0;
}

/* ── Title ── */
.brand-title {
    font-family: 'Syne', sans-serif;
    font-weight: 900;
    font-size: 52px;
    background: linear-gradient(135deg, #818cf8 0%, #c084fc 50%, #f472b6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-align: center;
    letter-spacing: -1px;
    line-height: 1;
    margin-bottom: 4px;
}
.brand-sub {
    text-align: center;
    color: #475569;
    font-size: 15px;
    font-weight: 400;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 28px;
}

/* ── Progress bar ── */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #6366f1, #a855f7, #ec4899) !important;
    border-radius: 99px !important;
}
.stProgress > div > div {
    background: rgba(255,255,255,0.06) !important;
    border-radius: 99px !important;
    height: 7px !important;
}

/* ── Pill badge ── */
.pill {
    display: inline-block;
    background: rgba(99,102,241,0.15);
    border: 1px solid rgba(99,102,241,0.35);
    color: #818cf8;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    padding: 4px 14px;
    border-radius: 99px;
    margin-bottom: 12px;
}

/* ── Question card ── */
.q-card {
    background: linear-gradient(145deg, rgba(30,41,59,0.9), rgba(15,23,42,0.95));
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 24px;
    padding: 32px 36px;
    margin: 16px 0 24px 0;
    box-shadow:
        0 0 0 1px rgba(99,102,241,0.08),
        0 20px 60px rgba(0,0,0,0.4),
        inset 0 1px 0 rgba(255,255,255,0.06);
    position: relative;
    overflow: hidden;
}
.q-card::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #6366f1, #a855f7, #ec4899);
    opacity: 0.8;
}
.q-number {
    font-family: 'Syne', sans-serif;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #6366f1;
    margin-bottom: 14px;
}
.q-text {
    font-family: 'Syne', sans-serif;
    font-size: 22px;
    font-weight: 700;
    color: #f1f5f9;
    line-height: 1.45;
}

/* ── Timer ── */
.timer-wrap {
    border-radius: 16px;
    padding: 14px 24px;
    text-align: center;
    font-family: 'Syne', sans-serif;
    font-size: 26px;
    font-weight: 800;
    margin-bottom: 20px;
    letter-spacing: -0.5px;
    border: 1px solid;
    transition: all 0.3s ease;
}
.timer-safe {
    background: rgba(16,185,129,0.1);
    border-color: rgba(16,185,129,0.3);
    color: #34d399;
    box-shadow: 0 0 30px rgba(16,185,129,0.1);
}
.timer-warn {
    background: rgba(245,158,11,0.1);
    border-color: rgba(245,158,11,0.3);
    color: #fbbf24;
    box-shadow: 0 0 30px rgba(245,158,11,0.12);
}
.timer-danger {
    background: rgba(239,68,68,0.12);
    border-color: rgba(239,68,68,0.4);
    color: #f87171;
    box-shadow: 0 0 30px rgba(239,68,68,0.18);
}

/* ── Radio options ── */
div[data-testid="stRadio"] > label {
    display: none;
}
div[data-testid="stRadio"] > div {
    gap: 10px !important;
    display: flex;
    flex-direction: column;
}
div[data-testid="stRadio"] > div > label {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 14px !important;
    padding: 15px 20px !important;
    cursor: pointer;
    transition: all 0.2s ease !important;
    color: #cbd5e1 !important;
    font-size: 15px !important;
    font-weight: 500 !important;
}
div[data-testid="stRadio"] > div > label:hover {
    background: rgba(99,102,241,0.12) !important;
    border-color: rgba(99,102,241,0.4) !important;
    color: #e2e8f0 !important;
    transform: translateX(4px);
}
div[data-testid="stRadio"] > div > label[data-checked="true"] {
    background: rgba(99,102,241,0.18) !important;
    border-color: rgba(99,102,241,0.7) !important;
    color: #a5b4fc !important;
}

/* ── Submit button ── */
div[data-testid="stButton"] > button {
    width: 100%;
    background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
    color: white;
    font-family: 'Syne', sans-serif;
    font-size: 16px;
    font-weight: 700;
    letter-spacing: 1px;
    border: none;
    border-radius: 14px;
    padding: 14px 28px;
    height: auto;
    cursor: pointer;
    box-shadow: 0 4px 20px rgba(99,102,241,0.35);
    transition: all 0.2s ease;
}
div[data-testid="stButton"] > button:hover {
    background: linear-gradient(135deg, #4f46e5 0%, #9333ea 100%);
    box-shadow: 0 6px 28px rgba(99,102,241,0.5);
    transform: translateY(-2px);
}
div[data-testid="stButton"] > button:active {
    transform: translateY(0px);
}

/* ── Metrics ── */
div[data-testid="stMetric"] {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 18px 16px;
    text-align: center;
}
div[data-testid="stMetric"] label {
    color: #64748b !important;
    font-size: 12px !important;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    font-weight: 600;
}
div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    font-family: 'Syne', sans-serif;
    font-size: 32px !important;
    font-weight: 800 !important;
    color: #f1f5f9 !important;
}

/* ── Expander ── */
details {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 14px !important;
    padding: 4px !important;
}
summary {
    color: #94a3b8 !important;
    font-weight: 600 !important;
}

/* ── Mistake card ── */
.mistake-card {
    background: rgba(239,68,68,0.07);
    border: 1px solid rgba(239,68,68,0.25);
    border-radius: 12px;
    padding: 14px 18px;
    margin: 8px 0;
    line-height: 1.6;
}
.mistake-q { color: #94a3b8; font-size: 14px; margin-bottom: 6px; }
.mistake-yours { color: #fca5a5; font-size: 13px; }
.mistake-correct { color: #86efac; font-size: 13px; font-weight: 600; }

/* ── Result badge ── */
.result-badge {
    text-align: center;
    padding: 40px 20px 20px;
}
.result-emoji { font-size: 72px; line-height: 1; margin-bottom: 12px; }
.result-grade {
    font-family: 'Syne', sans-serif;
    font-size: 38px;
    font-weight: 900;
    margin-bottom: 8px;
}
.result-msg { color: #64748b; font-size: 16px; }

/* ── Divider ── */
.fancy-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(99,102,241,0.4), transparent);
    margin: 28px 0;
    border: none;
}

/* ── Score badge inline ── */
.score-inline {
    text-align: right;
    color: #a855f7;
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 15px;
    padding-top: 4px;
}

/* ── Alerts ── */
div[data-testid="stAlert"] {
    border-radius: 12px !important;
}
</style>

<div class="glow-orb-1"></div>
<div class="glow-orb-2"></div>
""", unsafe_allow_html=True)

# ── QUESTIONS ─────────────────────────────────────────────────────────────────
QUESTIONS = [
    {
        "question": "How many countries are members of the United Nations (UN)?",
        "options": {"A": "194", "B": "192", "C": "193", "D": "191"},
        "answer": "C",
        "category": "🌍 World Affairs",
    },
    {
        "question": "When did India gain its independence?",
        "options": {"A": "1948", "B": "1947", "C": "1946", "D": "1945"},
        "answer": "B",
        "category": "📜 History",
    },
    {
        "question": "Where is the Taj Mahal located?",
        "options": {"A": "Agra", "B": "Mumbai", "C": "Delhi", "D": "Rupnagar"},
        "answer": "A",
        "category": "🗺️ Geography",
    },
    {
        "question": "How many bones are in the adult human body?",
        "options": {"A": "204", "B": "205", "C": "206", "D": "207"},
        "answer": "C",
        "category": "🔬 Science",
    },
    {
        "question": "How many countries currently possess hydrogen bombs?",
        "options": {"A": "6", "B": "5", "C": "9", "D": "8"},
        "answer": "A",
        "category": "🌍 World Affairs",
    },
]

TIMER_SECONDS = 12

# ── SESSION STATE ──────────────────────────────────────────────────────────────
def reset_state():
    st.session_state.question_index = 0
    st.session_state.score = 0
    st.session_state.quiz_finished = False
    st.session_state.wrong_answers = []
    st.session_state.start_time = time.time()

if "question_index" not in st.session_state:
    reset_state()

# ── HEADER ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="brand-title">BrainBlitz</div>', unsafe_allow_html=True)
st.markdown('<div class="brand-sub">Knowledge Challenge</div>', unsafe_allow_html=True)

total_q = len(QUESTIONS)

# ══════════════════════════════════════════════════════════════════════════════
# QUIZ IN PROGRESS
# ══════════════════════════════════════════════════════════════════════════════
if not st.session_state.quiz_finished:
    idx = st.session_state.question_index
    q   = QUESTIONS[idx]

    # ── Progress row ──────────────────────────────────────────────────────────
    prog_col, score_col = st.columns([4, 1])
    with prog_col:
        st.progress((idx) / total_q)
    with score_col:
        st.markdown(
            f'<div class="score-inline">⚡ {st.session_state.score} pts</div>',
            unsafe_allow_html=True
        )

    # ── Timer ─────────────────────────────────────────────────────────────────
    elapsed   = int(time.time() - st.session_state.start_time)
    remaining = TIMER_SECONDS - elapsed

    if remaining > 7:
        t_cls, t_icon = "timer-safe",   "🟢"
    elif remaining > 4:
        t_cls, t_icon = "timer-warn",   "🟡"
    else:
        t_cls, t_icon = "timer-danger", "🔴"

    st.markdown(
        f'<div class="timer-wrap {t_cls}">'
        f'{t_icon}&nbsp; {max(remaining, 0)}s remaining'
        f'</div>',
        unsafe_allow_html=True
    )

    # ── Auto-skip on timeout ──────────────────────────────────────────────────
    if remaining <= 0:
        ca = q["answer"]
        st.session_state.wrong_answers.append({
            "question":    q["question"],
            "your_answer": "⏰ No answer (time up)",
            "correct":     f"{ca} → {q['options'][ca]}",
        })
        st.session_state.question_index += 1
        st.session_state.start_time = time.time()
        if st.session_state.question_index >= total_q:
            st.session_state.quiz_finished = True
        st.rerun()

    # ── Category pill + question card ─────────────────────────────────────────
    st.markdown(
        f'<div class="pill">{q["category"]}</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        f'''<div class="q-card">
                <div class="q-number">Question {idx + 1} of {total_q}</div>
                <div class="q-text">{q["question"]}</div>
            </div>''',
        unsafe_allow_html=True
    )

    # ── Options ───────────────────────────────────────────────────────────────
    selected = st.radio(
        "Pick your answer",
        list(q["options"].keys()),
        format_func=lambda k: f"  {k}   ·   {q['options'][k]}",
        index=None,
        key=f"q_{idx}",
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Submit ─────────────────────────────────────────────────────────────────
    _, btn_col, _ = st.columns([1, 3, 1])
    with btn_col:
        if st.button("Submit Answer →", use_container_width=True):
            if selected is None:
                st.warning("⚠️  Please choose an answer before submitting.")
            else:
                if selected == q["answer"]:
                    st.success("✅  Correct!  Well done!")
                    st.session_state.score += 1
                else:
                    ca = q["answer"]
                    st.error(
                        f"❌  Wrong!  Correct answer: **{ca} → {q['options'][ca]}**"
                    )
                    st.session_state.wrong_answers.append({
                        "question":    q["question"],
                        "your_answer": f"{selected} → {q['options'][selected]}",
                        "correct":     f"{ca} → {q['options'][ca]}",
                    })
                time.sleep(1.2)
                st.session_state.question_index += 1
                st.session_state.start_time = time.time()
                if st.session_state.question_index >= total_q:
                    st.session_state.quiz_finished = True
                st.rerun()

    # ── Auto-refresh every second for timer ───────────────────────────────────
    time.sleep(1)
    st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# RESULTS PAGE
# ══════════════════════════════════════════════════════════════════════════════
else:
    final_score = st.session_state.score
    pct         = (final_score / total_q) * 100
    wrong_count = total_q - final_score

    st.balloons()

    # Grade
    if pct == 100:
        emoji, grade, msg, color = "🏆", "Perfect Score!", "Flawless. You're a genius.", "#fbbf24"
    elif pct >= 80:
        emoji, grade, msg, color = "🌟", "Excellent!", "Outstanding knowledge!", "#34d399"
    elif pct >= 60:
        emoji, grade, msg, color = "👍", "Good Job!", "Solid effort — keep it up.", "#60a5fa"
    else:
        emoji, grade, msg, color = "💪", "Keep Practicing!", "Review and come back stronger.", "#f87171"

    st.markdown(f"""
    <div class="result-badge">
        <div class="result-emoji">{emoji}</div>
        <div class="result-grade" style="color:{color};">{grade}</div>
        <div class="result-msg">{msg}</div>
    </div>
    """, unsafe_allow_html=True)

    # Progress bar showing score
    st.progress(final_score / total_q)

    st.markdown("<br>", unsafe_allow_html=True)

    # Metric row
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("✅ Correct", f"{final_score}")
    with c2:
        st.metric("📊 Score", f"{pct:.0f}%")
    with c3:
        st.metric("❌ Wrong", f"{wrong_count}")

    st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

    # Mistakes review
    if st.session_state.wrong_answers:
        with st.expander(f"📋  Review mistakes  ({len(st.session_state.wrong_answers)} total)"):
            for i, w in enumerate(st.session_state.wrong_answers, 1):
                st.markdown(f"""
                <div class="mistake-card">
                    <div class="mistake-q">Q{i}: {w['question']}</div>
                    <div class="mistake-yours">Your answer: {w['your_answer']}</div>
                    <div class="mistake-correct">✓ Correct: {w['correct']}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.success("🔥  Flawless! Zero mistakes — incredible!")

    st.markdown("<br>", unsafe_allow_html=True)

    # Restart
    _, rb_col, _ = st.columns([1, 3, 1])
    with rb_col:
        if st.button("🔄  Play Again", use_container_width=True):
            reset_state()
            # clear widget keys so radio buttons reset cleanly
            for k in [k for k in st.session_state if isinstance(k, str) and k.startswith("q_")]:
                del st.session_state[k]
            st.rerun()