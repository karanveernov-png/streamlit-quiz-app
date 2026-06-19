"""
quiz_logic.py — The quiz state machine: starting/resetting a quiz,
in-session scoring history, and Streamlit session-state initialisation.
"""
import re
import time
import streamlit as st

# If the file is named dictionary_data.py
from data import SUBJECT_DATA, PRESET_QUESTIONS
from ai_engine import get_extended_hard_questions, get_extended_custom_hard_questions

# ── Reset helpers ─────────────────────────────────────────────────────────
def quiz_reset():
    for k in ["question_index", "score", "wrong_answers", "start_time", "current_xp", "current_questions",
              "skips_used", "hints_used_total", "xp_flash"]:
        st.session_state.pop(k, None)
    st.session_state.streak = 0   # reset streak per quiz but keep best_streak
    # Clear per-question radio, bookmark, hint keys
    clear_keys = [k for k in st.session_state if isinstance(k, str) and
                  re.match(r'^(q|bm|hint|xp_flash)_\d+', k)]
    for k in clear_keys:
        st.session_state.pop(k, None)


def save_quiz_to_history(subj, diff, score, total, xp_earned, wrongs):
    """Save a completed quiz session to session history (in-session only)."""
    import datetime
    if "quiz_history" not in st.session_state:
        st.session_state.quiz_history = []
    entry = {
        "subject":   subj,
        "difficulty": diff,
        "score":     score,
        "total":     total,
        "pct":       int((score / total) * 100) if total > 0 else 0,
        "xp":        xp_earned,
        "wrongs":    len(wrongs),
        "timestamp": datetime.datetime.now().strftime("%H:%M"),
    }
    st.session_state.quiz_history.insert(0, entry)
    # Keep last 10
    st.session_state.quiz_history = st.session_state.quiz_history[:10]


# ── Start a quiz ──────────────────────────────────────────────────────────
def start_custom_quiz(subj_name, topic, difficulty, timer_sec):
    """Start a quiz using custom AI-generated questions."""
    want_hard = difficulty == "Hard" and st.session_state.get("hard_question_count", 5) > 5
    if want_hard:
        with st.spinner(f"Preparing {st.session_state.hard_question_count} Hard questions…"):
            questions = get_extended_custom_hard_questions(
                subj_name, topic, st.session_state.hard_question_count
            )
        if not questions:
            st.error("❌ Couldn't prepare extra Hard questions. Try again.")
            return False
    else:
        cache_key = f"q_cache_CUSTOM_{subj_name}_{topic}_{difficulty}"
        if cache_key not in st.session_state:
            # This will show a red error box on your screen instead of doing nothing!
            st.error(f"❌ Cannot start quiz: The Hard questions are missing from memory. The AI might have failed to generate them.")
            return False
        questions = st.session_state[cache_key]
    display_name = f"{subj_name} — {topic}"

    # Register dynamically into SUBJECT_DATA AND persist in session_state so
    # it survives Streamlit reruns (module-level dicts reset every run)
    entry = {"icon": "✏️", "desc": f"Custom: {topic}"}
    SUBJECT_DATA[display_name] = entry
    st.session_state[f"custom_subj_entry_{display_name}"] = entry

    st.session_state.subject      = display_name
    st.session_state.difficulty   = difficulty
    st.session_state.timer_seconds = timer_sec

    quiz_reset()
    st.session_state.current_questions = questions
    st.session_state.question_index    = 0
    st.session_state.score             = 0
    st.session_state.current_xp        = 0
    st.session_state.wrong_answers     = []
    st.session_state.start_time        = time.time()
    st.session_state.page              = "quiz"
    st.rerun()


def start_quiz(subj, difficulty, timer_sec):
    """Start the quiz — instant, no API call made here (unless topping up Hard mode to 10Q)."""
    st.session_state.subject = subj
    st.session_state.difficulty = difficulty
    st.session_state.timer_seconds = timer_sec

    want_hard = difficulty == "Hard" and st.session_state.get("hard_question_count", 5) > 5
    if want_hard:
        with st.spinner(f"Preparing {st.session_state.hard_question_count} Hard questions…"):
            questions = get_extended_hard_questions(subj, st.session_state.hard_question_count)
        if not questions:
            st.error("❌ No questions found for this subject. Please generate them first.")
            return
    else:
        cache_key = f"q_cache_{subj}_{difficulty}"
        if cache_key in st.session_state:
            questions = st.session_state[cache_key]
        elif subj in PRESET_QUESTIONS:
            questions = PRESET_QUESTIONS[subj][difficulty]
        else:
            st.error("❌ No questions found for this subject. Please generate them first.")
            return

    quiz_reset()
    st.session_state.current_questions = questions
    st.session_state.question_index = 0
    st.session_state.score = 0
    st.session_state.current_xp = 0
    st.session_state.wrong_answers = []
    st.session_state.start_time = time.time()
    st.session_state.page = "quiz"
    st.rerun()


def init_session_state():
    """
    Initialise all required keys in st.session_state on first run, and
    restore any custom subjects created earlier this session back into
    SUBJECT_DATA (module-level dicts reset on every Streamlit rerun, but
    session_state persists).
    """
    if "page" not in st.session_state:
        st.session_state.page = "login"
    if "total_xp" not in st.session_state:
        st.session_state.total_xp = 0
    if "streak" not in st.session_state:
        st.session_state.streak = 0          # correct answers in a row
    if "best_streak" not in st.session_state:
        st.session_state.best_streak = 0
    if "bookmarks" not in st.session_state:
        st.session_state.bookmarks = []      # list of bookmarked question dicts
    if "skips_used" not in st.session_state:
        st.session_state.skips_used = 0
    if "hints_used_total" not in st.session_state:
        st.session_state.hints_used_total = 0
    if "quiz_history" not in st.session_state:
        st.session_state.quiz_history = []
    if "user_id" not in st.session_state:
        st.session_state.user_id = None      # Supabase auth user id, set on login
    if "hard_question_count" not in st.session_state:
        st.session_state.hard_question_count = 5   # user can bump this to 10 from the result page

    # ── Restore any custom subjects into SUBJECT_DATA on every rerun ─────────────
    # (module-level dicts reset on each Streamlit rerun; session_state persists)
    for _key, _val in list(st.session_state.items()):
        if isinstance(_key, str) and _key.startswith("custom_subj_entry_"):
            _display_name = _key[len("custom_subj_entry_"):]
            if _display_name not in SUBJECT_DATA:
                SUBJECT_DATA[_display_name] = _val