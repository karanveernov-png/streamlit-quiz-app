"""
subject_page.py — Subject selection & difficulty screen: preset subject
grid, bookmarks panel, custom-subject creation flow, and the AI question
refresh controls.
"""
import streamlit as st

from data import SUBJECT_DATA, PRESET_QUESTIONS
from db import clear_bookmarks
from ai_engine import generate_custom_questions, refresh_subject_questions
from quiz_logic import start_quiz, start_custom_quiz
from ui_components import render_brand, render_steps, render_badge
from utils import full_reset


def render():
    render_brand()
    render_steps(1)
    render_badge()

    st.markdown('''
    <div style="margin-bottom:6px;"><div class="section-chip">// SELECT MODULE</div></div>
    <div style="font-family:\'Orbitron\',sans-serif;font-size:19px;font-weight:800;color:#e8f8f0;margin-bottom:6px;letter-spacing:.5px;">
        CHOOSE YOUR SUBJECT
    </div>
    <div style="color:rgba(0,255,160,.35);font-size:13px;margin-bottom:20px;">
        Higher difficulty = more XP per question. Tap 🔄 to load fresh AI questions.
    </div>
    ''', unsafe_allow_html=True)

    # ── Quick access to bookmarks ───────────────────────────────────────────
    bookmarks = st.session_state.get("bookmarks", [])
    with st.expander(f"🔖 Bookmarks ({len(bookmarks)})"):
        if bookmarks:
            for i, b in enumerate(bookmarks, 1):
                st.markdown(f'''
                <div class="mk" style="border-left-color:#f59e0b;">
                    <div class="mk-q">Q{i}: {b['question']}</div>
                    <div class="mk-u" style="color:#94a3b8;">📚 {b.get("subject","")} · {b.get("difficulty","")}</div>
                    <div class="mk-c">✓ Answer: {b['answer']} → {b['options'][b['answer']]}</div>
                    <div class="mk-e">💡 {b['explanation']}</div>
                </div>''', unsafe_allow_html=True)
            if st.button("🗑️ Clear All Bookmarks", key="subj_clear_bookmarks", use_container_width=True):
                st.session_state.bookmarks = []
                if st.session_state.get("user_id"):
                    clear_bookmarks(st.session_state.user_id)
                st.rerun()
        else:
            st.caption("No bookmarks yet — save a question during a quiz to see it here.")

    chosen = st.session_state.get("subject_pick", None)

    subjects_list = list(SUBJECT_DATA.keys())
    # Only show the 6 preset subjects in the grid (filter out any dynamically added custom ones)
    preset_subjects = [s for s in subjects_list if s in PRESET_QUESTIONS]
    # Use 2 columns on mobile (Streamlit auto-stacks at narrow widths, but 2 cols is safer)
    row1 = st.columns(2)
    row2 = st.columns(2)
    row3 = st.columns(2)
    grid = list(zip([*row1, *row2, *row3], preset_subjects))

    for col, subj in grid:
        info = SUBJECT_DATA.get(subj, {"icon": "✏️", "desc": "Custom Quiz"})
        sel_c = "sel" if chosen == subj else ""
        is_refreshed = f"q_cache_{subj}_Easy" in st.session_state

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
                st.session_state.pop("custom_pick", None)
                st.rerun()

    # ── Custom Subject Card ────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    custom_sel_c = "sel" if chosen == "__custom__" else ""
    st.markdown(f'''
    <div class="s-card custom-card {custom_sel_c}">
        <div class="s-icon">✏️</div>
        <div class="s-name">Custom Subject</div>
        <div class="s-desc">Type your own subject &amp; topic — AI generates the quiz!</div>
    </div>
    ''', unsafe_allow_html=True)
    if st.button(f"{'✓ ' if chosen == '__custom__' else ''}+ Create Custom Quiz", key="pick_custom", use_container_width=True):
        st.session_state.subject_pick = "__custom__"
        st.rerun()

    # ── Custom Subject Input Panel ─────────────────────────────────────────
    if chosen == "__custom__":
        st.markdown('''
        <div class="custom-panel">
            <div class="custom-panel-title">✏️ Create Your Own Quiz</div>
            <div class="custom-panel-sub">Enter the subject and a specific topic — the AI will generate 15 fresh MCQs (Easy, Medium, Hard).</div>
        </div>
        ''', unsafe_allow_html=True)

        c_subj  = st.text_input("📘 Subject Name",  placeholder="e.g.  Physics, Economics, Music Theory…",     key="custom_subj_input")
        c_topic = st.text_input("🎯 Topic / Chapter", placeholder="e.g.  Newton's Laws,  Demand & Supply,  Scales…", key="custom_topic_input")

        is_ready = st.session_state.get("custom_ready", False)
        cready_subj  = st.session_state.get("custom_ready_subj", "")
        cready_topic = st.session_state.get("custom_ready_topic", "")

        if is_ready and cready_subj and cready_topic:
            st.markdown(f'''
            <div class="custom-ready-panel">
                <div style="font-size:26px">✅</div>
                <div>
                    <div class="custom-ready-text">Questions ready for "{cready_subj} — {cready_topic}"</div>
                    <div class="custom-ready-sub">Choose a difficulty mode below to start!</div>
                </div>
            </div>
            ''', unsafe_allow_html=True)

            cd1, cd2, cd3 = st.columns(3)
            st.markdown('<div class="diff-btn-wrap">', unsafe_allow_html=True)
            with cd1:
                if st.button("🌱 Easy\n30s · 1XP", key="cbtn_easy", use_container_width=True):
                    start_custom_quiz(cready_subj, cready_topic, "Easy", 30)
            with cd2:
                if st.button("⚖️ Medium\n20s · 2XP", key="cbtn_med", use_container_width=True):
                    start_custom_quiz(cready_subj, cready_topic, "Medium", 20)
            with cd3:
                if st.button(f"🔥 Hard\n15s · 3XP · {st.session_state.get('hard_question_count', 5)}Q", key="cbtn_hard", use_container_width=True):
                    start_custom_quiz(cready_subj, cready_topic, "Hard", 15)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            c_ref_col, c_new_col = st.columns(2)

            # Custom subject refresh limit tracking
            custom_refresh_key = f"refresh_count_custom_{cready_subj}_{cready_topic}"
            c_ref_count = st.session_state.get(custom_refresh_key, 0)
            c_rem = max(0, 2 - c_ref_count)

            with c_ref_col:
                if st.button(f"🔄 Refresh Questions ({c_rem} left)", key="cbtn_refresh", disabled=(c_ref_count >= 2), use_container_width=True):
                    with st.spinner(f"Generating fresh MCQs for {cready_subj} - {cready_topic}..."):
                        ok = generate_custom_questions(cready_subj, cready_topic)
                        if ok:
                            st.session_state[custom_refresh_key] = c_ref_count + 1
                            st.toast("✅ Custom questions refreshed!", icon="🤖")
                            st.rerun()
                        else:
                            st.error("❌ Failed to refresh questions.")
            with c_new_col:
                if st.button("➕ Create New Subject", key="cbtn_new", use_container_width=True):
                    st.session_state.pop("custom_ready", None)
                    st.session_state.pop("custom_ready_subj", None)
                    st.session_state.pop("custom_ready_topic", None)
                    st.rerun()

        else:
            st.markdown('<div class="gen-btn-wrap">', unsafe_allow_html=True)
            if st.button("🤖 Generate Questions with AI", key="gen_custom_qs", use_container_width=True):
                sn = c_subj.strip()
                tn = c_topic.strip()
                if not sn or not tn:
                    st.error("⚠️ Please fill in both Subject Name and Topic.")
                else:
                    with st.spinner(f'🤖 Generating MCQs for "{sn} - {tn}"... this takes ~10 seconds'):
                        ok = generate_custom_questions(sn, tn)
                    if ok:
                        st.session_state.custom_ready       = True
                        st.session_state.custom_ready_subj  = sn
                        st.session_state.custom_ready_topic = tn
                        st.toast(f"✅ Questions ready for {sn} — {tn}!", icon="🤖")
                        st.rerun()
                    else:
                        st.error("❌ Could not generate questions. Check your API keys and try again.")
            st.markdown('</div>', unsafe_allow_html=True)


    # ── Difficulty Selection Panel (preset subjects only) ─────────────────
    if chosen and chosen != "__custom__":
        cache_status = "⚡ AI questions loaded!" if is_refreshed else "// Using preset questions"
        st.markdown(f'''
        <div class="diff-panel">
            <div class="diff-title">MODULE: {info['icon']} {chosen}</div>
            <div style="font-size:10px; color:rgba(0,255,160,.35); margin-top:-10px; margin-bottom:8px; font-family:\'Orbitron\',sans-serif; letter-spacing:1px;">{cache_status}</div>
        </div>
        ''', unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        st.markdown('<div class="diff-btn-wrap">', unsafe_allow_html=True)
        with c1:
            if st.button("🌱 Easy\n30s · 1XP", key="btn_easy", use_container_width=True):
                start_quiz(chosen, "Easy", 30)
        with c2:
            if st.button("⚖️ Medium\n20s · 2XP", key="btn_med", use_container_width=True):
                start_quiz(chosen, "Medium", 20)
        with c3:
            if st.button(f"🔥 Hard\n15s · 3XP · {st.session_state.get('hard_question_count', 5)}Q", key="btn_hard", use_container_width=True):
                start_quiz(chosen, "Hard", 15)
        st.markdown('</div>', unsafe_allow_html=True)

        # ── Refresh button ──────────────────────────────────────────────────
        refresh_count_key = f"refresh_count_{chosen}"
        refresh_count = st.session_state.get(refresh_count_key, 0)
        rem_refreshes = max(0, 2 - refresh_count)

        refresh_label = f"🤖 AI ✓ Refreshed [{rem_refreshes} left]" if is_refreshed else f"🔄 Refresh All Questions [{rem_refreshes} left]"
        refreshed_class = "refreshed" if is_refreshed else ""

        st.markdown(f'<div class="refresh-btn-wrap {refreshed_class}">', unsafe_allow_html=True)
        if st.button(refresh_label, key="refresh_chosen_subj", disabled=(refresh_count >= 2), use_container_width=True):
            with st.spinner(f"Generating fresh {chosen} questions via AI…"):
                success = refresh_subject_questions(chosen)
            if success:
                st.session_state[refresh_count_key] = refresh_count + 1
                st.toast(f"✅ {chosen} — all 3 modes refreshed!", icon="🤖")
                st.rerun()
            else:
                st.error(f"❌ Could not generate questions for {chosen}. Check your API keys.")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="logout-area">', unsafe_allow_html=True)
    if st.button("← Log out", key="subj_logout"):
        full_reset()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)