"""
styles.py — Injects the global CSS block for the app (fonts, layout fixes,
neon theme, responsive breakpoints, component styling). Call inject_css()
once near the top of app.py.
"""
import streamlit as st

@st.cache_data(ttl=None)
def _css_block():
    """Return the full CSS string. Cached so it is computed only once."""
    return '''
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700;800;900&family=DM+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>

/* ─── Base ───────────────────────────────────────────────────────────── */
#MainMenu, footer, header { visibility: hidden; }
* { box-sizing: border-box; }
html, body, .stApp {
    background: #070a0f !important;
    font-family: 'DM Sans', sans-serif;
    color: #c8d8e8;
}

/* ─── Fix Streamlit layout ──────────────────────────────────────────── */
.block-container {
    max-width: 760px !important;
    padding: 2.5rem 1.5rem 5rem !important;
    margin-left: auto !important;
    margin-right: auto !important;
    width: 100% !important;
}
section[data-testid="stAppViewContainer"] > div:first-child,
section.main > div,
div[data-testid="stAppViewBlockContainer"] {
    padding-left: 0 !important;
    padding-right: 0 !important;
}

/* ─── Scanline texture overlay ─────────────────────────────────────── */
.stApp::before {
    content: "";
    position: fixed; inset: 0; z-index: 0; pointer-events: none;
    background-image: repeating-linear-gradient(
        0deg,
        transparent,
        transparent 3px,
        rgba(0,255,200,.018) 3px,
        rgba(0,255,200,.018) 4px
    );
}

/* ─── Grid bg pattern ──────────────────────────────────────────────── */
.stApp::after {
    content: "";
    position: fixed; inset: 0; z-index: 0; pointer-events: none;
    background-image:
        linear-gradient(rgba(0,255,160,.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,255,160,.04) 1px, transparent 1px);
    background-size: 48px 48px;
}

/* ─── Mobile overrides (≤ 640px) ─────────────────────────────────────── */
@media (max-width: 640px) {
    .block-container {
        padding: 1.2rem 0.9rem 4rem !important;
        max-width: 100% !important;
    }
    .brand-logo { font-size: 30px !important; }
    .brand-tag  { font-size: 9px !important; letter-spacing: 2px !important; }
    .stepbar { max-width: 100% !important; gap: 0 !important; }
    .step-circle { width: 26px !important; height: 26px !important; font-size: 10px !important; }
    .step-label  { font-size: 8px !important; }
    div[data-testid="stTextInput"] input, div[data-testid="stPasswordInput"] input {
        font-size: 16px !important; padding: 12px 14px !important;
    }
    div[data-testid="stButton"] > button { font-size: 13px !important; padding: 11px 14px !important; }
    .ubadge { padding: 8px 12px !important; gap: 8px !important; }
    .uavatar { width: 28px !important; height: 28px !important; font-size: 11px !important; }
    .s-card { padding: 14px 8px !important; }
    .s-icon { font-size: 26px !important; }
    .s-name { font-size: 12px !important; }
    .qcard { padding: 16px 14px !important; }
    .qtxt  { font-size: 15px !important; }
    .tmr { font-size: 15px !important; padding: 8px 12px !important; }
    div[data-testid="stRadio"] > div > label { padding: 6px 10px !important; font-size: 11px !important; }
    div[data-testid="stRadio"] > div > label:hover { transform: none !important; }
    .res-emoji { font-size: 48px !important; }
    .res-grade { font-size: 22px !important; }
    .yt-grid { grid-template-columns: 1fr 1fr !important; gap: 8px !important; }
    .mk { padding: 10px 12px !important; }
    div[data-testid="metric-container"] { padding: 8px !important; }
    div[data-testid="metric-container"] label { font-size: 10px !important; }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] { font-size: 20px !important; }
}

/* ─── Tablet overrides (641px – 768px) ───────────────────────────────── */
@media (min-width: 641px) and (max-width: 768px) {
    .block-container { padding: 2rem 1.2rem 4rem !important; }
    .brand-logo { font-size: 38px !important; }
    .yt-grid { grid-template-columns: repeat(2, 1fr) !important; }
}

/* ─── Neon corner glows ─────────────────────────────────────────────── */
.orb-a {
    position: fixed; width: 500px; height: 500px;
    top: -200px; right: -150px;
    background: radial-gradient(circle, rgba(0,255,160,.12) 0%, transparent 65%);
    border-radius: 50%; pointer-events: none; z-index: 0;
}
.orb-b {
    position: fixed; width: 450px; height: 450px;
    bottom: -150px; left: -120px;
    background: radial-gradient(circle, rgba(0,180,255,.09) 0%, transparent 65%);
    border-radius: 50%; pointer-events: none; z-index: 0;
}

/* ─── Brand ──────────────────────────────────────────────────────────── */
.brand-wrap { text-align: center; margin-bottom: 2px; margin-top: 8px; }
.brand-logo {
    display: inline-block;
    font-family: 'Orbitron', sans-serif;
    font-weight: 900; font-size: 44px; letter-spacing: 2px; line-height: 1;
    color: #00ffa0;
    text-shadow:
        0 0 8px rgba(0,255,160,.9),
        0 0 24px rgba(0,255,160,.5),
        0 0 60px rgba(0,255,160,.2);
}
.brand-tag {
    text-align: center; letter-spacing: 5px; font-size: 10px;
    text-transform: uppercase; color: rgba(0,255,160,.35); font-weight: 600;
    margin-bottom: 26px;
}

/* ─── Step bar ────────────────────────────────────────────────────────── */
.stepbar {
    display: flex; align-items: center; justify-content: center;
    gap: 0; margin: 0 auto 28px; max-width: 360px;
}
.step-item {
    display: flex; flex-direction: column; align-items: center; gap: 5px;
    flex: 1;
}
.step-circle {
    width: 32px; height: 32px; border-radius: 4px;
    display: flex; align-items: center; justify-content: center;
    font-size: 13px; font-weight: 700;
    transition: all .3s ease;
}
.step-circle.done   { background: rgba(0,255,160,.12); color: #00ffa0; border: 1.5px solid rgba(0,255,160,.5); }
.step-circle.active { background: rgba(0,255,160,.18); color: #00ffa0; border: 1.5px solid #00ffa0; box-shadow: 0 0 14px rgba(0,255,160,.5), inset 0 0 8px rgba(0,255,160,.1); }
.step-circle.idle   { background: rgba(255,255,255,.03); color: rgba(255,255,255,.18); border: 1.5px solid rgba(255,255,255,.07); }
.step-label { font-size: 9px; letter-spacing: 1.5px; text-transform: uppercase; font-weight: 700; }
.step-label.done   { color: rgba(0,255,160,.55); }
.step-label.active { color: #00ffa0; }
.step-label.idle   { color: rgba(255,255,255,.15); }
.step-line      { flex: 1; height: 1px; background: rgba(255,255,255,.06); margin-top: -22px; }
.step-line.done { background: rgba(0,255,160,.4); box-shadow: 0 0 6px rgba(0,255,160,.3); }

/* ─── Login card ───────────────────────────────────────────────────── */
.login-header {
    background: rgba(0,15,10,.85);
    border: 1px solid rgba(0,255,160,.18);
    border-radius: 4px 4px 0 0;
    padding: 32px 36px 8px; margin-bottom: 0; position: relative; overflow: hidden;
}
.login-header::before {
    content:""; position:absolute; top:0; left:0; right:0; height:2px;
    background: linear-gradient(90deg, transparent, #00ffa0, #00b4ff, transparent);
    animation: shimmer 3s ease-in-out infinite;
}
@keyframes shimmer { 0%,100% { opacity:.5; } 50% { opacity:1; } }
.login-footer {
    background: rgba(0,15,10,.85);
    border: 1px solid rgba(0,255,160,.18); border-top: none;
    border-radius: 0 0 4px 4px; padding: 8px 36px 28px;
}
.section-chip {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(0,255,160,.08); border: 1px solid rgba(0,255,160,.3);
    color: #00ffa0; font-size: 10px; font-weight: 700; letter-spacing: 2px;
    text-transform: uppercase; padding: 4px 12px; border-radius: 2px; margin-bottom: 12px;
    font-family: 'Orbitron', sans-serif;
}
.login-title { font-family: 'Orbitron', sans-serif; font-size: 22px; font-weight: 800; color: #e8f8f0; margin-bottom: 6px; }
.login-sub { color: rgba(0,255,160,.35); font-size: 13px; margin-bottom: 20px; line-height: 1.6; }
.divider-line { height: 1px; background: linear-gradient(90deg,transparent,rgba(0,255,160,.2),transparent); margin: 20px 0; }

/* ─── Inputs & Buttons ──────────────────────────────────────────────── */
div[data-testid="stTextInput"] label, div[data-testid="stPasswordInput"] label {
    font-size: 10px !important; font-weight: 700 !important; letter-spacing: 2.5px;
    text-transform: uppercase; color: rgba(0,255,160,.5) !important; margin-bottom: 5px;
    font-family: 'Orbitron', sans-serif !important;
}
div[data-testid="stTextInput"] input, div[data-testid="stPasswordInput"] input {
    background: rgba(0,20,12,.6) !important; border: 1px solid rgba(0,255,160,.2) !important;
    border-radius: 3px !important; color: #00ffa0 !important; font-size: 15px !important;
    padding: 12px 15px !important; font-family: 'DM Sans', sans-serif !important;
}
div[data-testid="stTextInput"] input:focus, div[data-testid="stPasswordInput"] input:focus {
    border-color: rgba(0,255,160,.7) !important; box-shadow: 0 0 0 2px rgba(0,255,160,.12), 0 0 16px rgba(0,255,160,.1) !important;
    background: rgba(0,30,18,.7) !important;
}
div[data-testid="stButton"] > button {
    width: 100%; background: transparent;
    color: #00ffa0; font-family: 'Orbitron', sans-serif; font-size: 13px; font-weight: 700;
    letter-spacing: 1px; border: 1px solid rgba(0,255,160,.5); border-radius: 3px;
    padding: 13px 22px; height: auto;
    box-shadow: 0 0 12px rgba(0,255,160,.12), inset 0 0 12px rgba(0,255,160,.04);
    transition: all .2s ease; text-transform: uppercase;
}
div[data-testid="stButton"] > button:hover {
    background: rgba(0,255,160,.08);
    border-color: #00ffa0;
    box-shadow: 0 0 24px rgba(0,255,160,.3), inset 0 0 16px rgba(0,255,160,.08);
    transform: translateY(-1px);
    color: #fff;
}
div[data-testid="stButton"] > button:active { transform: translateY(0); }

.logout-area div[data-testid="stButton"] > button {
    background: transparent !important; border: 1px solid rgba(255,255,255,.1) !important;
    color: rgba(255,255,255,.25) !important; font-size: 11px !important; box-shadow: none !important;
    letter-spacing: 1px !important; width: auto !important; padding: 7px 18px !important;
    text-transform: uppercase !important;
}

/* ─── Test-API button ─────────────────────────────────────────────── */
.test-api-wrap div[data-testid="stButton"] > button {
    width: auto !important; padding: 4px 12px !important; font-size: 10px !important;
    font-weight: 700 !important; letter-spacing: 1px !important; border-radius: 2px !important;
    box-shadow: none !important; background: transparent !important;
    border: 1px solid rgba(0,255,160,.25) !important; color: rgba(0,255,160,.6) !important;
    height: auto !important; min-height: unset !important; line-height: 1.4 !important;
}
.test-api-wrap div[data-testid="stButton"] > button:hover {
    background: rgba(0,255,160,.08) !important; transform: none !important; box-shadow: none !important;
}

/* ─── Refresh button ────────────────────────────────────────────── */
.refresh-btn-wrap div[data-testid="stButton"] > button {
    width: auto !important; padding: 7px 14px !important; font-size: 11px !important;
    font-weight: 700 !important; letter-spacing: 1px !important; border-radius: 2px !important;
    box-shadow: none !important; background: transparent !important;
    border: 1px solid rgba(0,180,255,.3) !important; color: rgba(0,180,255,.7) !important;
    height: auto !important; min-height: unset !important; line-height: 1.3 !important; margin-top: 4px !important;
}
.refresh-btn-wrap div[data-testid="stButton"] > button:hover {
    background: rgba(0,180,255,.08) !important; border-color: rgba(0,180,255,.6) !important;
    color: #00b4ff !important; transform: none !important; box-shadow: none !important;
}
.refresh-btn-wrap.refreshed div[data-testid="stButton"] > button {
    border-color: rgba(0,255,160,.4) !important; color: #00ffa0 !important;
}

/* ─── Subject cards & Difficulty Panel ───────────────────────────────── */
.s-card {
    background: rgba(0,20,12,.5); border: 1px solid rgba(0,255,160,.1);
    border-radius: 3px; padding: 20px 12px; text-align: center; transition: all .22s ease;
    position: relative; overflow: hidden;
}
.s-card::before {
    content:""; position:absolute; inset:0;
    background: linear-gradient(145deg, rgba(0,255,160,.03), transparent);
    border-radius: 3px;
}
.s-card:hover {
    border-color: rgba(0,255,160,.45); background: rgba(0,255,160,.06);
    transform: translateY(-3px); box-shadow: 0 8px 28px rgba(0,255,160,.12), 0 0 0 1px rgba(0,255,160,.15);
}
.s-card.sel {
    border-color: rgba(0,255,160,.8); background: rgba(0,255,160,.08);
    box-shadow: 0 0 0 2px rgba(0,255,160,.25), 0 8px 28px rgba(0,255,160,.15);
}
.s-icon { font-size: 34px; line-height: 1; margin-bottom: 8px; }
.s-name { font-family: 'Orbitron', sans-serif; font-size: 13px; font-weight: 800; color: #e8f8f0; margin-bottom: 4px; letter-spacing: .5px; }
.s-desc { font-size: 11px; color: rgba(0,255,160,.35); font-weight: 500; }

.diff-panel {
    background: rgba(0,15,10,.7);
    border: 1px solid rgba(0,255,160,.2);
    border-radius: 3px;
    padding: 22px; margin-top: 14px; text-align: center; animation: fadeIn .35s ease;
}
@keyframes fadeIn { from { opacity: 0; transform: translateY(-8px); } to { opacity: 1; transform: translateY(0); } }
.diff-title { font-family: 'Orbitron', sans-serif; font-size: 15px; font-weight: 700; color: #00ffa0; margin-bottom: 14px; letter-spacing: .5px; }

/* ─── User badge ────────────────────────────────────────────────────── */
.ubadge {
    display: flex; align-items: center; gap: 12px; background: rgba(0,20,12,.6);
    border: 1px solid rgba(0,255,160,.12); border-radius: 3px; padding: 10px 16px; margin-bottom: 20px;
}
.uavatar {
    width: 34px; height: 34px; border-radius: 3px; flex-shrink: 0;
    background: rgba(0,255,160,.15); border: 1px solid rgba(0,255,160,.4);
    display: flex; align-items: center;
    justify-content: center; font-family: 'Orbitron', sans-serif; font-weight: 900; font-size: 13px;
    color: #00ffa0;
}
.uname  { font-weight: 600; font-size: 13px; color: #c8f0d8; }
.uemail { font-size: 11px; color: rgba(0,255,160,.3); }
.uxp    { color: #00b4ff; font-weight: 700; font-size: 11px; letter-spacing: 0.5px; font-family: 'Orbitron', sans-serif; }

/* ─── Timer & Progress ─────────────────────────────────────────────────── */
.stProgress > div > div { background: rgba(0,255,160,.07) !important; border-radius: 2px !important; height: 4px !important; }
.stProgress > div > div > div > div { background: linear-gradient(90deg,#00ffa0,#00b4ff) !important; box-shadow: 0 0 8px rgba(0,255,160,.4) !important; }

.tmr {
    border-radius: 3px; padding: 10px 18px; text-align: center; font-family: 'Orbitron', sans-serif;
    font-size: 18px; font-weight: 800; margin-bottom: 14px; border: 1px solid;
    display: flex; align-items: center; justify-content: center; gap: 10px; letter-spacing: 1px;
}
.t-safe   { background:rgba(0,255,160,.05);  border-color:rgba(0,255,160,.3);  color:#00ffa0; text-shadow: 0 0 10px rgba(0,255,160,.5); }
.t-warn   { background:rgba(255,200,0,.05);  border-color:rgba(255,200,0,.3);  color:#ffd700; text-shadow: 0 0 10px rgba(255,200,0,.4); }
.t-danger { background:rgba(255,50,50,.06);  border-color:rgba(255,50,50,.4);  color:#ff5050; text-shadow: 0 0 10px rgba(255,50,50,.5); animation: pulse 0.8s ease infinite; }
@keyframes pulse { 0%,100% { opacity:1; } 50% { opacity:.6; } }

/* ─── Score spill ───────────────────────────────────────────────────── */
.spill {
    font-family: 'Orbitron', sans-serif; font-size: 13px; font-weight: 800;
    color: #00b4ff; text-align: right; padding-top: 4px;
    text-shadow: 0 0 8px rgba(0,180,255,.5);
}

/* ─── Subject pill ──────────────────────────────────────────────────── */
.subj-pill {
    display: inline-block; background: rgba(0,180,255,.08);
    border: 1px solid rgba(0,180,255,.25); border-radius: 2px;
    padding: 4px 14px; font-size: 11px; font-weight: 700; letter-spacing: 1px;
    color: #00b4ff; margin-bottom: 12px; font-family: 'Orbitron', sans-serif; text-transform: uppercase;
}

/* ─── H-divider ─────────────────────────────────────────────────────── */
.h-divider { height: 1px; background: linear-gradient(90deg,transparent,rgba(0,255,160,.2),transparent); margin: 24px 0; }

/* ─── Question card ─────────────────────────────────────────────────── */
.qcard {
    background: rgba(0,15,10,.85);
    border: 1px solid rgba(0,255,160,.18); border-radius: 3px; padding: 26px 28px;
    margin: 10px 0 18px; position: relative; overflow: hidden;
}
.qcard::before {
    content:""; position:absolute; top:0; left:0; width:3px; bottom:0;
    background: linear-gradient(180deg,#00ffa0,#00b4ff);
    box-shadow: 0 0 12px rgba(0,255,160,.5);
}
.qcard::after {
    content:""; position:absolute; top:0; right:0; left:0; height:1px;
    background: linear-gradient(90deg,transparent,rgba(0,255,160,.3),transparent);
}
.qnum { font-size: 9px; font-weight: 700; letter-spacing: 3px; text-transform: uppercase; color: rgba(0,255,160,.4); margin-bottom: 10px; font-family: 'Orbitron', sans-serif; }
.qtxt { font-family: 'DM Sans', sans-serif; font-size: 19px; font-weight: 700; color: #e0f0e8; line-height: 1.55; }

/* ─── Radio options ──────────────────────────────────────────────────── */
/* ─── Radio options ──────────────────────────────────────────────────── */
div[data-testid="stRadio"] > label { display: none; }
div[data-testid="stRadio"] > div { gap: 5px !important; flex-direction: column; }
div[data-testid="stRadio"] > div > label {
    background: rgba(0,20,12,.4) !important; border: 1px solid rgba(0,255,160,.1) !important;
    border-radius: 3px !important; padding: 7px 12px !important; 
    font-size: 12px !important; transition: all .18s ease !important;
    
    /* FIX CODE: Force the text to be completely solid bright white/light green */
    color: #e0f8e8 !important; 
    opacity: 1 !important;
}

/* FIX CODE: Targets the paragraph text block inner tags generated by Streamlit modern engines */
div[data-testid="stRadio"] p,
div[data-testid="stRadio"] span {
    color: #ffffff !important;
    opacity: 1 !important;
}
div[data-testid="stRadio"] > div > label:hover {
    background: rgba(0,255,160,.07) !important; border-color: rgba(0,255,160,.4) !important;
    color: #e0f8e8 !important; transform: translateX(4px);
    box-shadow: 0 0 12px rgba(0,255,160,.08) !important;
}
div[data-testid="stRadio"] > div > label[data-checked="true"] {
    background: rgba(0,255,160,.1) !important; border-color: rgba(0,255,160,.6) !important;
    color: #00ffa0 !important; box-shadow: 0 0 14px rgba(0,255,160,.12) !important;
}

/* ─── Auth tab radio (Log In / Create Account) — force side-by-side ───── */
.st-key-auth_tab div[data-testid="stRadio"] > div,
.st-key-auth_tab[data-testid="stRadio"] > div {
    flex-direction: row !important;
    gap: 10px !important;
}
.st-key-auth_tab div[data-testid="stRadio"] > div > label,
.st-key-auth_tab[data-testid="stRadio"] > div > label {
    flex: 1 1 0;
    justify-content: center;
    text-align: center;
    
    /* FIX CODE: Force the login tab text to be solid bright white/light green */
    color: #e0f8e8 !important;
    opacity: 1 !important;
}

/* FIX CODE: Targets the text element inner blocks inside the Auth container */
.st-key-auth_tab div[data-testid="stRadio"] p,
.st-key-auth_tab div[data-testid="stRadio"] span {
    color: #ffffff !important;
    opacity: 1 !important;
}

/* ─── Mistake cards ──────────────────────────────────────────────────── */
.mk { background:rgba(255,50,50,.05); border:1px solid rgba(255,80,80,.18); border-radius:3px; padding:14px 16px; margin:8px 0;
      border-left: 3px solid rgba(255,80,80,.6); }
.mk-q  { color:#9ab8a8; font-size:14px; margin-bottom:5px; line-height:1.5; font-weight: 600; }
.mk-u  { color:rgba(255,120,120,.8); font-size:12px; margin-bottom:3px; }
.mk-c  { color:#00ffa0; font-size:12px; font-weight:700; margin-bottom:6px; }
.mk-e  { color:rgba(200,220,210,.5); font-size:12px; margin-top:6px; line-height:1.6;
         border-top: 1px dashed rgba(0,255,160,.1); padding-top:8px; }

/* ─── Result UI & Badges ────────────────────────────────────────────── */
.res-hero { text-align:center; padding:12px 0 10px; }
.res-emoji { font-size:68px; line-height:1; margin-bottom:8px; }
.res-grade { font-family:'Orbitron',sans-serif; font-size:28px; font-weight:900; margin-bottom:6px; letter-spacing:1px; }
.res-msg { color:rgba(0,255,160,.45); font-size:15px; margin-bottom:20px; }
.badge-card {
    display: inline-block; background: rgba(0,15,10,.7); border: 1px solid;
    border-radius: 3px; padding: 12px 26px; font-family: 'Orbitron', sans-serif;
    font-size: 18px; font-weight: 800; margin-bottom: 14px; letter-spacing: 1px;
    box-shadow: 0 0 24px rgba(0,0,0,.6);
}

/* ─── YouTube Resources Section ──────────────────────────────────── */
.yt-section-title {
    font-family: 'Orbitron', sans-serif; font-size: 17px; font-weight: 800;
    color: #e8f8f0; margin-bottom: 5px; display: flex; align-items: center; gap: 10px; letter-spacing: .5px;
}
.yt-section-sub { font-size: 12px; color: rgba(0,255,160,.35); margin-bottom: 16px; line-height: 1.5; }
.yt-grid {
    display: grid; grid-template-columns: repeat(auto-fill, minmax(190px, 1fr));
    gap: 10px; margin-bottom: 8px;
}
.yt-card {
    background: rgba(0,10,5,.8);
    border: 1px solid rgba(255,50,50,.18); border-radius: 3px; padding: 14px 12px;
    text-decoration: none; transition: all .2s ease; display: block; position: relative;
    overflow: hidden;
}
.yt-card::before {
    content:""; position:absolute; top:0; left:0; width:2px; bottom:0;
    background: linear-gradient(180deg,#ff4040,rgba(255,100,100,.3));
}
.yt-card:hover {
    border-color: rgba(255,80,80,.5); background: rgba(255,40,40,.05);
    transform: translateY(-2px); box-shadow: 0 6px 20px rgba(255,0,0,.1);
}
.yt-icon { font-size: 26px; margin-bottom: 7px; line-height: 1; }
.yt-title { font-family: 'Orbitron', sans-serif; font-size: 11px; font-weight: 700; color: #e8f0e8; margin-bottom: 4px; line-height: 1.4; letter-spacing: .3px; }
.yt-desc  { font-size: 11px; color: rgba(0,255,160,.3); line-height: 1.4; }
.yt-tag {
    display: inline-block; background: rgba(255,50,50,.1); border: 1px solid rgba(255,50,50,.25);
    color: rgba(255,100,100,.8); font-size: 9px; font-weight: 700; letter-spacing: 1px;
    border-radius: 2px; padding: 2px 7px; margin-top: 5px; font-family: 'Orbitron', sans-serif; text-transform: uppercase;
}
.ai-tip-box {
    background: rgba(0,20,15,.7);
    border: 1px solid rgba(0,180,255,.2); border-radius: 3px; padding: 16px 20px;
    margin: 10px 0 18px; position: relative;
    border-left: 3px solid rgba(0,180,255,.5);
}
.ai-tip-label {
    font-size: 9px; font-weight: 700; letter-spacing: 2.5px; text-transform: uppercase;
    color: rgba(0,180,255,.6); margin-bottom: 7px; font-family: 'Orbitron', sans-serif;
}
.ai-tip-text { font-size: 13px; color: rgba(200,230,220,.65); line-height: 1.7; }

/* ─── Back button override ────────────────────────────────────────── */
.back-btn-wrap div[data-testid="stButton"] > button {
    background: transparent !important;
    border: 1px solid rgba(255,255,255,.08) !important;
    color: rgba(255,255,255,.25) !important;
    box-shadow: none !important;
    font-size: 10px !important;
    padding: 5px 10px !important;
    letter-spacing: 1px !important;
    font-family: 'Orbitron', sans-serif !important;
    font-weight: 700 !important;
    border-radius: 2px !important;
    text-transform: uppercase !important;
    height: auto !important; min-height: unset !important; line-height: 1.4 !important;
}
.back-btn-wrap div[data-testid="stButton"] > button:hover {
    background: rgba(0,255,160,.06) !important;
    border-color: rgba(0,255,160,.3) !important;
    color: rgba(0,255,160,.7) !important;
    box-shadow: none !important; transform: none !important;
}

/* ─── Custom Subject Card & Panel ────────────────────────────────── */
.s-card.custom-card {
    border-color: rgba(0,180,255,.2);
    background: rgba(0,10,20,.5);
}
.s-card.custom-card:hover {
    border-color: rgba(0,180,255,.5);
    background: rgba(0,180,255,.07);
    box-shadow: 0 8px 28px rgba(0,180,255,.12);
}
.s-card.custom-card.sel {
    border-color: rgba(0,180,255,.75);
    background: rgba(0,180,255,.08);
    box-shadow: 0 0 0 2px rgba(0,180,255,.2), 0 8px 28px rgba(0,180,255,.12);
}
.custom-panel {
    background: rgba(0,12,20,.8);
    border: 1px solid rgba(0,180,255,.22); border-radius: 3px;
    padding: 24px 26px; margin-top: 14px; animation: fadeIn .3s ease;
    position: relative; overflow: hidden;
    border-left: 3px solid rgba(0,180,255,.5);
}
.custom-panel-title {
    font-family: 'Orbitron', sans-serif; font-size: 16px; font-weight: 800;
    color: #00b4ff; margin-bottom: 4px; letter-spacing: .5px;
}
.custom-panel-sub {
    font-size: 12px; color: rgba(0,180,255,.35); margin-bottom: 18px; line-height: 1.5;
}
.gen-btn-wrap div[data-testid="stButton"] > button {
    border-color: rgba(0,180,255,.5) !important; color: #00b4ff !important;
    box-shadow: 0 0 16px rgba(0,180,255,.12) !important;
}
.gen-btn-wrap div[data-testid="stButton"] > button:hover {
    background: rgba(0,180,255,.08) !important; box-shadow: 0 0 28px rgba(0,180,255,.25) !important;
    border-color: #00b4ff !important; color: #fff !important;
}

/* ─── Difficulty mode buttons (Easy/Medium/Hard) — compact size ─────── */
.diff-btn-wrap div[data-testid="stButton"] > button {
    padding: 7px 10px !important; font-size: 11px !important;
    font-weight: 700 !important; letter-spacing: .5px !important;
    border-radius: 3px !important; height: auto !important;
    min-height: unset !important; line-height: 1.4 !important;
}

/* ─── MCQ/Quiz action buttons (Bookmark, Skip) — compact ─ */
.quiz-action-btns div[data-testid="stButton"] > button {
    padding: 5px 10px !important; font-size: 10px !important;
    font-weight: 700 !important; height: auto !important;
    min-height: unset !important; line-height: 1.4 !important;
    letter-spacing: .5px !important;
}

/* ─── Submit button — compact but prominent ─────────────────── */
.submit-btn-wrap div[data-testid="stButton"] > button {
    padding: 7px 14px !important; font-size: 12px !important;
    font-weight: 800 !important; height: auto !important;
    min-height: unset !important; line-height: 1.4 !important;
    letter-spacing: 1px !important;
    border-color: rgba(0,255,160,.7) !important;
    color: #00ffa0 !important;
    box-shadow: 0 0 14px rgba(0,255,160,.2) !important;
}
.submit-btn-wrap div[data-testid="stButton"] > button:hover {
    background: rgba(0,255,160,.1) !important;
    box-shadow: 0 0 22px rgba(0,255,160,.35) !important;
    color: #fff !important;
}

/* ─── Hint button ─────────────────────────────────────────────── */
.hint-btn-wrap div[data-testid="stButton"] > button {
    padding: 4px 9px !important; font-size: 10px !important;
    font-weight: 700 !important; height: auto !important; width: auto !important;
    min-height: unset !important; line-height: 1.4 !important;
    letter-spacing: .5px !important;
    background: transparent !important;
    border: 1px solid rgba(255,200,0,.3) !important;
    color: rgba(255,200,0,.7) !important;
    box-shadow: none !important; border-radius: 2px !important;
}
.hint-btn-wrap div[data-testid="stButton"] > button:hover {
    background: rgba(255,200,0,.07) !important;
    border-color: rgba(255,200,0,.6) !important;
    color: #ffd700 !important; transform: none !important;
}
.custom-ready-panel {
    background: rgba(0,20,12,.7);
    border: 1px solid rgba(0,255,160,.25); border-radius: 3px;
    padding: 12px 18px; margin-bottom: 14px;
    display: flex; align-items: center; gap: 12px;
}
.custom-ready-text { font-size: 13px; color: #00ffa0; font-weight: 600; }
.custom-ready-sub  { font-size: 11px; color: rgba(0,255,160,.3); margin-top: 2px; }

/* ─── Hint box ────────────────────────────────────────────────────────── */
.hint-box {
    background: rgba(255,200,0,.04); border: 1px solid rgba(255,200,0,.2);
    border-radius: 3px; padding: 10px 14px; margin: 6px 0 10px;
    border-left: 3px solid rgba(255,200,0,.5); animation: fadeIn .25s ease;
}
.hint-label { font-size: 9px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase;
    color: rgba(255,200,0,.6); margin-bottom: 5px; font-family: 'Orbitron', sans-serif; }
.hint-text  { font-size: 12px; color: rgba(220,210,160,.75); line-height: 1.6; }

/* ─── Combo/streak flash banner ──────────────────────────────────────── */
.combo-banner {
    text-align: center; padding: 6px 0; font-family: 'Orbitron', sans-serif;
    font-size: 11px; font-weight: 800; letter-spacing: 2px; text-transform: uppercase;
    border-radius: 3px; margin-bottom: 8px;
    animation: pulse 1s ease infinite;
}
.combo-3  { color: #00ffa0; background: rgba(0,255,160,.06); border: 1px solid rgba(0,255,160,.2); }
.combo-5  { color: #00b4ff; background: rgba(0,180,255,.07); border: 1px solid rgba(0,180,255,.25);
            text-shadow: 0 0 12px rgba(0,180,255,.6); }
.combo-10 { color: #ffd700; background: rgba(255,215,0,.07); border: 1px solid rgba(255,215,0,.3);
            text-shadow: 0 0 14px rgba(255,215,0,.7); animation: pulse .5s ease infinite; }

/* ─── XP flash ───────────────────────────────────────────────────────── */
.xp-flash {
    text-align: center; font-family: 'Orbitron', sans-serif; font-size: 16px;
    font-weight: 900; color: #00ffa0; letter-spacing: 2px;
    text-shadow: 0 0 14px rgba(0,255,160,.8);
    animation: xpPop .6s ease forwards;
}
@keyframes xpPop { 0% { opacity:0; transform:scale(.7) translateY(6px); }
    60% { opacity:1; transform:scale(1.15) translateY(-2px); }
    100% { opacity:1; transform:scale(1) translateY(0); } }

/* ─── Dark mode select override ──────────────────────────────────────── */
div[data-testid="stSelectbox"] > div { border-color: rgba(0,255,160,.2) !important; }

/* ─── Metrics ──────────────────────────────────────────────────────── */
div[data-testid="metric-container"] {
    background: rgba(0,20,12,.5) !important; border: 1px solid rgba(0,255,160,.1) !important;
    border-radius: 3px !important; padding: 12px !important;
}
div[data-testid="metric-container"] label {
    color: rgba(0,255,160,.4) !important; font-family: 'Orbitron', sans-serif !important;
    font-size: 9px !important; letter-spacing: 1.5px !important; text-transform: uppercase !important;
}
div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
    color: #00ffa0 !important; font-family: 'Orbitron', sans-serif !important;
    font-size: 24px !important; font-weight: 800 !important;
    text-shadow: 0 0 12px rgba(0,255,160,.4) !important;
}

/* ─── Expanders ─────────────────────────────────────────────────────── */
div[data-testid="stExpander"] {
    background: rgba(0,15,10,.6) !important; border: 1px solid rgba(0,255,160,.12) !important;
    border-radius: 3px !important;
}
div[data-testid="stExpander"] summary {
    color: rgba(0,255,160,.7) !important; font-family: 'Orbitron', sans-serif !important;
    font-size: 11px !important; letter-spacing: 1px !important; text-transform: uppercase !important;
}

/* ─── Performance ───────────────────────────────────────────────────── */
.stApp { contain: layout style; }
iframe { will-change: auto !important; }
div[data-testid="stVerticalBlock"] { contain: layout; }
</style>
<div class="orb-a"></div>
<div class="orb-b"></div>
'''

def inject_css():
    """Inject the global CSS block into the page. Call once per app run."""
    # Remove empty lines so Markdown parser doesn't break, and inject unconditionally
    safe_css = _css_block().replace("\n\n", "\n")
    st.markdown(safe_css, unsafe_allow_html=True)