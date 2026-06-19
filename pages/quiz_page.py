"""
quiz_page.py — Active quiz screen: question rendering, live countdown
timer (auto-skip on timeout), streak banners, hint/bookmark/skip actions,
and answer submission with XP/streak scoring.
"""
import time
import streamlit as st

from data import SUBJECT_DATA
from db import save_progress, save_bookmark
from ai_engine import get_ai_hint
from quiz_logic import quiz_reset
from ui_components import render_brand, render_steps, render_badge


def render():
    subj   = st.session_state.subject
    diff   = st.session_state.difficulty
    timer  = st.session_state.timer_seconds

    xp_multiplier = {"Easy": 1, "Medium": 2, "Hard": 3}[diff]
    info          = SUBJECT_DATA.get(subj, {"icon": "✏️", "desc": "Custom Quiz"})

    qs    = st.session_state.current_questions
    total = len(qs)
    idx   = st.session_state.get("question_index", 0)

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

    # ── Timer — isolated fragment so ONLY the timer div re-renders ─────────
    @st.fragment(run_every=1)
    def live_timer():
        remaining = timer - int(time.time() - st.session_state.start_time)
        remaining = max(remaining, 0)

        if remaining > (timer * 0.5):   tc, ti = "t-safe",   "🟢"
        elif remaining > (timer * 0.25): tc, ti = "t-warn",  "🟡"
        else:                            tc, ti = "t-danger", "🔴"

        st.markdown(
            f'<div class="tmr {tc}">{ti}&nbsp;&nbsp;{remaining} seconds remaining</div>',
            unsafe_allow_html=True
        )

        if remaining <= 0 and st.session_state.get("question_index") == idx:
            ca = q["answer"]
            st.session_state.wrong_answers.append({
                "question":    q["question"],
                "your_answer": "⏰ Time up — skipped",
                "correct":     f"{ca} → {q['options'][ca]}",
                "explanation": q.get("explanation", "No explanation available.")
            })
            st.session_state.question_index += 1
            st.session_state.start_time = time.time()
            st.rerun()

    live_timer()

    st.markdown(f'<div class="subj-pill">{info["icon"]} {subj} — {diff} Mode (+{xp_multiplier} XP)</div>', unsafe_allow_html=True)

    # ── Streak / combo banner ──────────────────────────────────────────────
    streak = st.session_state.get("streak", 0)
    best   = st.session_state.get("best_streak", 0)
    skips_used = st.session_state.get("skips_used", 0)
    max_skips  = 1  # allow 1 skip per quiz

    if streak >= 10:
        st.markdown(f'<div class="combo-banner combo-10">👑 {streak}× LEGENDARY STREAK — UNSTOPPABLE!</div>', unsafe_allow_html=True)
    elif streak >= 5:
        st.markdown(f'<div class="combo-banner combo-5">🔥 {streak}× HOT STREAK — ON FIRE!</div>', unsafe_allow_html=True)
    elif streak >= 3:
        st.markdown(f'<div class="combo-banner combo-3">⚡ {streak}× STREAK — KEEP GOING!</div>', unsafe_allow_html=True)

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

    # Compact CSS so action buttons (hint/bookmark/skip/back/submit) stay light on small screens
    st.markdown("""
    <style>
    div[data-testid="column"] div[data-testid="stButton"] > button {
        padding: 4px 6px !important; font-size: 10px !important; height: auto !important;
        min-height: unset !important; line-height: 1.3 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── Hint button ────────────────────────────────────────────────────────
    hint_key   = f"hint_{idx}"
    hints_used = st.session_state.get("hints_used_total", 0)
    max_hints  = 2  # max hints per quiz

    # ONLY SHOW IN HARD MODE
    if diff == "Hard":
        hint_col, _ = st.columns([1, 3])
        with hint_col:
            st.markdown('<div class="hint-btn-wrap">', unsafe_allow_html=True)
            if st.button(f"💡 Hint ({max_hints - hints_used} left)", key=f"hint_btn_{idx}",
                         disabled=(hints_used >= max_hints or hint_key in st.session_state)):
                with st.spinner("Generating hint…"):
                    hint_text = get_ai_hint(q["question"], q["options"])
                    st.session_state[hint_key] = hint_text
                    st.session_state["hints_used_total"] = hints_used + 1

                    # SECRET TIMER BOOST: Adds 3 seconds to the remaining time
                    st.session_state.start_time += 3

                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        # Show hint if generated
        if hint_key in st.session_state:
            st.markdown(f'''
            <div class="hint-box">
                <div class="hint-label">💡 AI Hint</div>
                <div class="hint-text">{st.session_state[hint_key]}</div>
            </div>
            ''', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
   # ── NEW MOBILE LAYOUT: Submit -> Bookmark & Skip -> Back ──────────────
    bm_key  = f"bm_{idx}"
    already_bookmarked = any(b.get("question") == q["question"] for b in st.session_state.bookmarks)
    bm_label = "🔖 Saved" if already_bookmarked else "🔖 Bookmark"

    # 1. SUBMIT BUTTON (Top position, full width)
    st.markdown('<div class="submit-btn-wrap">', unsafe_allow_html=True)
    if st.button("Submit Answer →", use_container_width=True, key=f"submit_{idx}"):
        if selected is None:
            st.warning("⚠️ Pick an option first.")
        else:
            if selected == q["answer"]:
                bonus = 0
                new_streak = st.session_state.get("streak", 0) + 1
                # Streak bonus XP: +1 bonus every 3 in a row
                if new_streak % 3 == 0:
                    bonus = 1
                earned = xp_multiplier + bonus
                st.session_state.score      = st.session_state.get("score", 0) + 1
                st.session_state.current_xp += earned
                st.session_state.total_xp   += earned
                st.session_state.streak = new_streak
                if new_streak > st.session_state.get("best_streak", 0):
                    st.session_state.best_streak = new_streak
                # Track XP flash message
                flash_msg = f"+{earned} XP" + (" 🔥 STREAK BONUS!" if bonus else "")
                st.session_state["xp_flash"] = flash_msg
                if st.session_state.get("user_id"):
                    save_progress(
                        st.session_state.user_id,
                        st.session_state.total_xp,
                        st.session_state.best_streak,
                    )
            else:
                ca = q["answer"]
                st.session_state.wrong_answers.append({
                    "question":    q["question"],
                    "your_answer": f"{selected} → {q['options'][selected]}",
                    "correct":     f"{ca} → {q['options'][ca]}",
                    "explanation": q.get("explanation", "No explanation available."),
                })
                st.session_state.streak = 0
                st.session_state.pop("xp_flash", None)
            st.session_state.question_index += 1
            st.session_state.start_time = time.time()
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # 2 & 3. BOOKMARK and SKIP (Side-by-side in the middle)
    st.markdown('<div class="quiz-action-btns">', unsafe_allow_html=True)
    col_bm, col_skip = st.columns(2)
    with col_bm:
        if st.button(bm_label, use_container_width=True, key=bm_key, disabled=already_bookmarked):
            new_bm = {
                "question": q["question"],
                "options":  q["options"],
                "answer":   q["answer"],
                "explanation": q.get("explanation", ""),
                "subject":  subj,
                "difficulty": diff,
            }
            st.session_state.bookmarks.append(new_bm)
            if st.session_state.get("user_id"):
                save_bookmark(st.session_state.user_id, new_bm)
            st.toast("🔖 Bookmarked!", icon="📌")
            st.rerun()
    with col_skip:
        skip_label = f"⏭️ Skip ({max_skips - skips_used} left)"
        if st.button(skip_label, use_container_width=True, key=f"skip_{idx}",
                     disabled=(skips_used >= max_skips)):
            ca = q["answer"]
            st.session_state.wrong_answers.append({
                "question":    q["question"],
                "your_answer": "⏭️ Skipped",
                "correct":     f"{ca} → {q['options'][ca]}",
                "explanation": q.get("explanation", "No explanation available.")
            })
            st.session_state.skips_used = skips_used + 1
            st.session_state.streak = 0
            st.session_state.question_index += 1
            st.session_state.start_time = time.time()
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # 4. BACK BUTTON (Bottom position)
    st.markdown('<div class="back-btn-wrap">', unsafe_allow_html=True)
    if st.button("← Back", use_container_width=True, key=f"back_{idx}"):
        quiz_reset()
        st.session_state.pop("subject_pick", None)
        st.session_state.pop("subject",      None)
        st.session_state.pop("difficulty",   None)
        st.session_state.page = "subject"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # Show XP flash if just answered correctly (on the NEXT question render)
    if st.session_state.get("xp_flash") and idx > 0:
        st.markdown(f'<div class="xp-flash">{st.session_state["xp_flash"]}</div>', unsafe_allow_html=True)
        st.session_state.pop("xp_flash", None)