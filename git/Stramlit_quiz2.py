import streamlit as st
import time

# ── Page config ────────────────────────────────────────────────
st.set_page_config(page_title="MCQ Quiz", page_icon="📝", layout="centered")

st.markdown("""
<style>
    .stRadio > div { gap: 12px; }
    .stRadio label { font-size: 1.1rem; }
    .question-box {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 20px;
        border-left: 4px solid #7c3aed;
    }
    .timer-box {
        font-size: 1.3rem;
        font-weight: bold;
        padding: 6px 16px;
        border-radius: 8px;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# ── Questions ──────────────────────────────────────────────────
questions = [
    {
        "question": "How many countries are members of the UN (United Nations)?",
        "options": {"A": "194", "B": "192", "C": "193", "D": "191"},
        "answer": "C"
    },
    {
        "question": "When did India get its independence?",
        "options": {"A": "1948", "B": "1947", "C": "1946", "D": "1945"},
        "answer": "B"
    },
    {
        "question": "Where is the Taj Mahal situated?",
        "options": {"A": "Agra", "B": "Mumbai", "C": "Delhi", "D": "Rupnagar"},
        "answer": "A"
    },
    {
        "question": "How many bones are in a human body?",
        "options": {"A": "204", "B": "205", "C": "206", "D": "207"},
        "answer": "C"
    },
    {
        "question": "How many countries have a hydrogen bomb?",
        "options": {"A": "6", "B": "5", "C": "9", "D": "8"},
        "answer": "A"
    }
]

TIMER_SECONDS = 30

# ── Session state bootstrap ────────────────────────────────────
def init_state():
    defaults = {
        "q_index":    0,
        "score":      0,
        "wrong":      [],
        "selected":   None,
        "feedback":   None,   # None | "correct" | "wrong" | "timeout"
        "start_time": None,
        "quiz_done":  False,
        "submitted":  False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ── Helpers ────────────────────────────────────────────────────
def advance_to_next():
    """Move to the next question and CLEAR all previous-question state."""
    st.session_state.q_index   += 1
    st.session_state.feedback   = None   # ← THIS is the key fix
    st.session_state.selected   = None
    st.session_state.submitted  = False
    st.session_state.start_time = time.time()

    if st.session_state.q_index >= len(questions):
        st.session_state.quiz_done = True

def restart_quiz():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    init_state()

# ── Quiz Done screen ───────────────────────────────────────────
if st.session_state.quiz_done:
    score = st.session_state.score
    total = len(questions)
    pct   = (score / total) * 100

    st.title("📊 Quiz Results")
    st.metric("Score", f"{score} / {total}")
    st.metric("Percentage", f"{pct:.1f}%")

    if pct >= 80:
        st.success("🎉 Excellent Performance!")
    elif pct >= 60:
        st.info("👍 Not bad, good work!")
    else:
        st.warning("😰 Failed — try again!")

    if st.session_state.wrong:
        with st.expander("📋 Review your mistakes"):
            for item in st.session_state.wrong:
                st.markdown(item)

    st.button("🔄 Restart Quiz", on_click=restart_quiz)
    st.stop()

# ── Active question ────────────────────────────────────────────
qi  = st.session_state.q_index
q   = questions[qi]

# Start timer on first visit to this question
if st.session_state.start_time is None:
    st.session_state.start_time = time.time()

st.markdown(f"**QUESTION {qi+1} OF {len(questions)}**")
st.markdown(f"""
<div class="question-box">
    <h3 style="color:#e2e8f0; margin:0">{q['question']}</h3>
</div>
""", unsafe_allow_html=True)

# ── Radio options (disabled after submit) ─────────────────────
option_labels = [f"{k} · {v}" for k, v in q["options"].items()]
option_keys   = list(q["options"].keys())

selected_label = st.radio(
    "Choose your answer:",
    option_labels,
    index=None,
    key=f"radio_{qi}",                      # unique key per question
    disabled=st.session_state.submitted,
)

if selected_label:
    st.session_state.selected = selected_label[0]   # grab "A"/"B"/"C"/"D"

# ── Timer + Submit area ────────────────────────────────────────
col_timer, col_btn = st.columns([3, 2])
timer_placeholder    = col_timer.empty()
feedback_placeholder = st.empty()
next_placeholder     = st.empty()

# ── Submit button ──────────────────────────────────────────────
def handle_submit():
    if not st.session_state.selected:
        return
    st.session_state.submitted = True
    user = st.session_state.selected
    correct = q["answer"]

    if user == correct:
        st.session_state.feedback = "correct"
        st.session_state.score   += 1
    else:
        st.session_state.feedback = "wrong"
        st.session_state.wrong.append(
            f"**Q:** {q['question']}  \n"
            f"**Your answer:** {user} · {q['options'][user]}  \n"
            f"**Correct:** {correct} · {q['options'][correct]}\n\n---"
        )

if not st.session_state.submitted:
    col_btn.button(
        "Submit Answer →",
        on_click=handle_submit,
        disabled=(st.session_state.selected is None),
        use_container_width=True
    )

# ── Live countdown (only while not yet submitted) ──────────────
if not st.session_state.submitted:
    elapsed   = time.time() - st.session_state.start_time
    remaining = TIMER_SECONDS - int(elapsed)

    if remaining <= 0:
        # Timed out
        st.session_state.submitted = True
        st.session_state.feedback  = "timeout"
        st.session_state.wrong.append(
            f"**Q:** {q['question']}  \n"
            f"**Skipped (timeout)**  \n"
            f"**Correct:** {q['answer']} · {q['options'][q['answer']]}\n\n---"
        )
        st.rerun()
    else:
        color = "#22c55e" if remaining > 10 else "#f59e0b" if remaining > 5 else "#ef4444"
        timer_placeholder.markdown(
            f'<div class="timer-box" style="background:{color}22; color:{color}; '
            f'border:2px solid {color}">⏰ {remaining}s</div>',
            unsafe_allow_html=True
        )
        time.sleep(1)
        st.rerun()   # rerun every second to update countdown

# ── Show feedback ONLY for current question ────────────────────
# (feedback is set to None the moment we advance, so it never bleeds over)
if st.session_state.feedback == "correct":
    feedback_placeholder.success("✅ Correct! Well done.")

elif st.session_state.feedback == "wrong":
    correct_key = q["answer"]
    feedback_placeholder.error(
        f"❌ Wrong! Correct answer: **{correct_key} · {q['options'][correct_key]}**"
    )

elif st.session_state.feedback == "timeout":
    correct_key = q["answer"]
    feedback_placeholder.warning(
        f"⏰ Time's up! Correct answer: **{correct_key} · {q['options'][correct_key]}**"
    )

# ── Next question button (shown only after submit) ─────────────
if st.session_state.submitted:
    timer_placeholder.markdown(
        '<div class="timer-box" style="background:#6b728022; color:#9ca3af; '
        'border:2px solid #6b7280">⏰ --s</div>',
        unsafe_allow_html=True
    )
    label = "Next Question →" if qi + 1 < len(questions) else "See Results →"
    next_placeholder.button(label, on_click=advance_to_next, use_container_width=True)
