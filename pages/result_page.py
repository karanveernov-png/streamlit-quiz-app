"""
result_page.py — Post-quiz results screen: score hero/grade, stats,
mistake review, session history, AI study tip, YouTube resource cards,
Hard-mode question-count preference, and the retry/play-again/logout
actions.
"""
import streamlit as st

from data import SUBJECT_DATA, YOUTUBE_RESOURCES
from db import sign_out
from ai_engine import get_ai_study_tip, generate_custom_yt_resources
from quiz_logic import save_quiz_to_history, start_quiz, start_custom_quiz, quiz_reset
from ui_components import render_brand, render_steps, render_badge
from utils import get_badge_info, full_reset


def render():
    user_name = st.session_state.get("user_name", "Challenger")
    subj      = st.session_state.subject
    diff      = st.session_state.difficulty
    info      = SUBJECT_DATA.get(subj, {"icon": "✏️", "desc": "Custom Quiz"})
    fs        = st.session_state.score
    total     = len(st.session_state.current_questions)
    pct       = (fs / total) * 100 if total > 0 else 0
    wrongs    = st.session_state.wrong_answers

    current_xp_earned = st.session_state.get("current_xp", 0)
    total_xp          = st.session_state.get("total_xp", 0)
    badge_name, badge_col, badge_msg = get_badge_info(total_xp)

    render_brand()
    render_steps(3)
    render_badge()
    st.balloons()

    # ── Save to session history ───────────────────────────────────────────
    hist_saved_key = f"hist_saved_{subj}_{diff}_{fs}"
    if hist_saved_key not in st.session_state:
        save_quiz_to_history(subj, diff, fs, total, current_xp_earned, wrongs)
        st.session_state[hist_saved_key] = True

    if pct == 100:   em, gr = "🏆", "FLAWLESS VICTORY"
    elif pct >= 80:  em, gr = "⚡", "EXCELLENT WORK"
    elif pct >= 60:  em, gr = "✅", "MISSION COMPLETE"
    else:            em, gr = "💪", "KEEP TRAINING"

    hero_html = (
        '<div class="res-hero">'
        + '<div class="res-emoji">' + em + '</div>'
        + '<div class="res-grade" style="color:' + badge_col + ';text-shadow:0 0 18px ' + badge_col + '80;">' + gr + '</div>'
        + '<div class="res-msg">WELL EXECUTED, <strong style="color:' + badge_col + ';">' + user_name.upper() + '</strong> — REVIEW YOUR STATS BELOW.</div>'
        + '<div class="badge-card" style="border-color:' + badge_col + '; color:' + badge_col + '; box-shadow: 0 0 18px ' + badge_col + '40;">' + badge_name + '</div>'
        + '<div style="font-size:13px; color:rgba(0,255,160,.35); font-style:italic; margin-bottom:20px; font-family:\'Orbitron\',sans-serif; font-size:11px; letter-spacing:1px;">'
        + '&#8220;' + badge_msg + '&#8221;'
        + '</div></div>'
    )
    st.markdown(hero_html, unsafe_allow_html=True)

    st.progress(min(fs / total, 1.0) if total > 0 else 0.0)
    st.markdown("<br>", unsafe_allow_html=True)

    best_streak = st.session_state.get("best_streak", 0)
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: st.metric("✅ Correct",  fs)
    with c2: st.metric("❌ Wrong",    total - fs)
    with c3: st.metric("📊 Accuracy", f"{pct:.0f}%")
    with c4: st.metric("⚡ XP Earned", f"+{current_xp_earned}")
    with c5: st.metric("🔥 Best Streak", best_streak)

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
        st.success(f"⚡ ZERO MISTAKES — ABSOLUTE PERFECTION, {user_name.upper()}!")

    # ── Session History ───────────────────────────────────────────────────
    history = st.session_state.get("quiz_history", [])
    if len(history) > 1:
        with st.expander(f"📈 Session History ({len(history)} quizzes today)"):
            hist_html = '<div style="display:grid;gap:6px;">'
            for i, h in enumerate(history):
                pct_c = "#00ffa0" if h["pct"] >= 80 else ("#ffd700" if h["pct"] >= 60 else "#ff5050")
                hist_html += f'''
                <div style="background:rgba(0,15,10,.5);border:1px solid rgba(0,255,160,.08);
                    border-radius:3px;padding:8px 12px;display:flex;align-items:center;gap:12px;">
                    <div style="font-family:Orbitron,sans-serif;font-size:10px;color:rgba(0,255,160,.3);">#{i+1}</div>
                    <div style="flex:1;">
                        <div style="font-size:12px;font-weight:600;color:#c8d8e8;">{h["subject"]} · {h["difficulty"]}</div>
                        <div style="font-size:10px;color:rgba(0,255,160,.35);">{h["timestamp"]}</div>
                    </div>
                    <div style="text-align:right;">
                        <div style="font-family:Orbitron,sans-serif;font-size:14px;font-weight:800;color:{pct_c};">{h["pct"]}%</div>
                        <div style="font-size:10px;color:rgba(0,180,255,.6);">+{h["xp"]} XP</div>
                    </div>
                </div>'''
            hist_html += '</div>'
            st.markdown(hist_html, unsafe_allow_html=True)

    # ── YouTube Study Resources ────────────────────────────────────────────
    st.markdown('<div class="h-divider"></div>', unsafe_allow_html=True)

    # AI-generated personalised study tip
    tip_key = f"ai_tip_{subj}_{diff}_{fs}"
    if tip_key not in st.session_state:
        with st.spinner("🤖 Generating personalised study tip…"):
            tip = get_ai_study_tip(subj, diff, fs, total)
            st.session_state[tip_key] = tip
    else:
        tip = st.session_state[tip_key]

    if tip:
        st.markdown(f'''
        <div class="ai-tip-box">
            <div class="ai-tip-label">🤖 AI Study Coach · Personalised for You</div>
            <div class="ai-tip-text">{tip}</div>
        </div>
        ''', unsafe_allow_html=True)

    # YouTube resource cards — preset subjects use YOUTUBE_RESOURCES dict;
    # custom subjects (subj contains " — ") use AI-generated cards cached in session_state.
    is_custom_subj = " — " in subj
    if is_custom_subj:
        yt_cache_key = f"yt_resources_{subj}"
        if yt_cache_key not in st.session_state:
            # Parse subj_name and topic back from "SubjName — Topic"
            parts = subj.split(" — ", 1)
            c_subj_name = parts[0].strip()
            c_topic     = parts[1].strip() if len(parts) > 1 else subj
            with st.spinner("🤖 Generating YouTube study resources for your topic…"):
                cards = generate_custom_yt_resources(c_subj_name, c_topic)
            st.session_state[yt_cache_key] = cards
        yt_resources = st.session_state.get(yt_cache_key, [])
    else:
        yt_resources = YOUTUBE_RESOURCES.get(subj, [])

    if yt_resources:
        subj_icon = SUBJECT_DATA.get(subj, {"icon": "✏️", "desc": "Custom Quiz"})["icon"]
        yt_label  = "🤖 AI-Curated" if is_custom_subj else "Handpicked"
        st.markdown(f'''
        <div class="yt-section-title">▶️ YouTube Resources — {subj_icon} {subj}</div>
        <div class="yt-section-sub">
            {yt_label} YouTube topics to deepen your understanding of <strong style="color:#e2e8f0">{subj}</strong>.
            Click any card to search on YouTube.
        </div>
        ''', unsafe_allow_html=True)

        # ── Render clickable YouTube cards ─────────────────────────────────
        cards_html = '<div class="yt-grid">'
        for r in yt_resources:
            icon  = r.get("icon",  "▶️")
            title = r.get("title", "Watch on YouTube")
            desc  = r.get("desc",  "")
            url   = r.get("url",   "#")
            tag   = r.get("tag",   "")
            # Ensure url is a clean string (AI sometimes wraps in markdown)
            url = str(url).strip().strip("[]()").split("](")[-1].rstrip(")")
            if not url.startswith("http"):
                url = "https://www.youtube.com/results?search_query=" + "+".join(title.split())
            cards_html += (
                f'<a class="yt-card" href="{url}" target="_blank" rel="noopener noreferrer">'
                f'  <div class="yt-icon">{icon}</div>'
                f'  <div class="yt-title">{title}</div>'
                f'  <div class="yt-desc">{desc}</div>'
                f'  <span class="yt-tag">▶ {tag}</span>'
                f'</a>'
            )
        cards_html += '</div>'
        st.markdown(cards_html, unsafe_allow_html=True)

    # ── Hard Mode length preference (ask after the quiz, on this last page) ─
    # Only shown when the quiz just played was Hard — Easy/Medium stay fixed-length.
    st.markdown('<div class="h-divider"></div>', unsafe_allow_html=True)

    if diff == "Hard":
        hard_q = st.session_state.get("hard_question_count", 5)

        col_box, col_label = st.columns([1, 5])
        with col_box:
            new_hard_q = st.number_input(
                "Hard mode question count",
                min_value=1,
                max_value=10,
                value=hard_q,
                step=1,
                label_visibility="collapsed",
                key="hard_q_input"
            )
        with col_label:
            st.markdown(
                '<div style="padding-top:8px;color:#c8d8e8;font-size:14px;">'
                '🔥 Questions for next Hard quiz (1–10)</div>',
                unsafe_allow_html=True
            )

        new_hard_q = int(new_hard_q)
        if new_hard_q != hard_q:
            st.session_state.hard_question_count = new_hard_q
            st.toast(f"🔥 Next Hard quiz will have {new_hard_q} questions!", icon="🔥")
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    a, b, c = st.columns(3)
    with a:
        if st.button("🔄 Retry Same", use_container_width=True):
            if is_custom_subj:
                parts = subj.split(" — ", 1)
                c_subj_name = parts[0].strip()
                c_topic     = parts[1].strip() if len(parts) > 1 else subj
                start_custom_quiz(c_subj_name, c_topic, diff, st.session_state.timer_seconds)
            else:
                start_quiz(subj, diff, st.session_state.timer_seconds)
    with b:
        if st.button("📚 Play Again", use_container_width=True):
            quiz_reset()
            if is_custom_subj:
                st.session_state.subject_pick = "__custom__"
            else:
                st.session_state.pop("subject_pick", None)
            st.session_state.pop("subject",      None)
            st.session_state.pop("difficulty",   None)
            st.session_state.page = "subject"
            st.rerun()
    with c:
        if st.button("🚪 Log Out", use_container_width=True):
            sign_out()
            full_reset()
            st.rerun()