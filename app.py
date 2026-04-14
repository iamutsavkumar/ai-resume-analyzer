"""
AI Resume Analyzer with Smart Feedback & Automation
=====================================================
Redesigned UI — premium SaaS aesthetic (Notion × Linear × Stripe)
Run with: streamlit run app.py
"""

import streamlit as st
from datetime import datetime



# Local module imports
from utils.pdf_extractor import extract_text_from_pdf
from utils.analyzer import analyze_resume
from utils.display import (
    render_section_feedback,
    render_missing_skills,
    render_weak_bullets,
    render_improved_bullets,
)

# ─── Session State Init ────────────────────────────────────────────────────────
if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False
if "result" not in st.session_state:
    st.session_state.result = None
if "current_job_role" not in st.session_state:
    st.session_state.current_job_role = ""
if "api_key_input" not in st.session_state:
    st.session_state.api_key_input = ""

# ─── Page Configuration ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="Resume AI · Instant Career Intelligence",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>

/* Fix headings */
h1, h2, h3, h4, h5, h6 {
    color: #e5e7eb !important;
}

/* Paragraph text */
p {
    color: #d1d5db !important;
}

/* Labels */
label {
    color: #d1d5db !important;
}

/* Section labels */
.section-label-text {
    color: #e5e7eb !important;
}

/* ---------------- TABS ---------------- */

div[data-baseweb="tab-list"] {
    background-color: #1f2937 !important;
    border-radius: 12px !important;
    padding: 4px !important;
}

button[data-baseweb="tab"] {
    background-color: transparent !important;
    color: #9ca3af !important;
    border-radius: 8px !important;
}

button[aria-selected="true"] {
    background-color: #111827 !important;
    color: #ffffff !important;
}

/* ---------------- FILE UPLOADER FIX ---------------- */

/* OUTER container (main fix) */
div[data-testid="stFileUploader"] > div {
    background-color: #111827 !important;
    border-radius: 12px !important;
    border: 1px dashed #374151 !important;
}

/* Remove white wrapper */
div[data-testid="stFileUploader"] {
    background-color: transparent !important;
}

/* Inner section */
div[data-testid="stFileUploader"] section {
    background-color: #111827 !important;
}

/* Upload button */
section[data-testid="stFileUploader"] button {
    background-color: #1f2937 !important;
    color: white !important;
    border: 1px solid #374151 !important;
}

</style>
""", unsafe_allow_html=True)

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #f7f8fa;
    color: #1a1d23;
}

/* Hide Streamlit chrome */
#MainMenu, footer {
    visibility: hidden;
}

.stDeployButton {
    display: none;
}

/* Sidebar toggle button (keep visible, subtle) */
[data-testid="collapsedControl"] {
    opacity: 0.4;
    transition: opacity 0.2s ease;
}

[data-testid="collapsedControl"]:hover {
    opacity: 1;
}

.block-container { padding-top: 0 !important; max-width: 1200px !important; margin: 0 auto; }

/* ── Typography ── */
h1, h2, h3, h4 { font-family: 'Syne', sans-serif; letter-spacing: -0.02em; }

/* ── Hero ── */
.hero {
    padding: 4rem 2rem 3rem;
    text-align: center;
    position: relative;
}
.hero-eyebrow {
    display: inline-block;
    background: #eef2ff;
    color: #4f46e5;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 0.35rem 0.9rem;
    border-radius: 100px;
    margin-bottom: 1.5rem;
}
.hero h1 {
    font-family: 'Syne', sans-serif;
    font-size: clamp(2.2rem, 5vw, 3.4rem);
    font-weight: 800;
    color: #0f1117;
    margin: 0 0 1rem;
    line-height: 1.08;
    letter-spacing: -0.03em;
}
            
/* Remove any link/anchor icons near headings */
a, a:link, a:visited {
    text-decoration: none !important;
}

h1 a {
    display: none !important;
}

/* Remove weird link icons injected by extensions */
[href]::after {
    display: none !important;
}
            
.hero h1 span {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #a855f7 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero p {
    font-size: 1.1rem;
    color: #6b7280;
    max-width: 520px;
    margin: 0 auto 0.5rem;
    line-height: 1.6;
    font-weight: 500;
}

/* ── Step Indicator ── */
.step-indicator {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0;
    margin: 2.5rem auto 3rem;
    max-width: 480px;
}
.step-dot {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 0.85rem;
    position: relative;
    z-index: 1;
    transition: all 0.3s ease;
}
.step-dot.active {
    background: #4f46e5;
    color: white;
    box-shadow: 0 0 0 4px rgba(79,70,229,0.15);
}
.step-dot.complete {
    background: #10b981;
    color: white;
}
.step-dot.inactive {
    background: #e5e7eb;
    color: #9ca3af;
}
.step-label {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    position: absolute;
    top: 44px;
    left: 50%;
    transform: translateX(-50%);
    white-space: nowrap;
    color: inherit;
}
.step-line {
    flex: 1;
    height: 2px;
    background: #e5e7eb;
    margin: 0;
    position: relative;
    top: 0;
}
.step-line.complete { background: #10b981; }
.step-wrapper { position: relative; display: flex; flex-direction: column; align-items: center; }

/* ── Cards ── */
.card {
    background: #ffffff;
    border: 1px solid #eaecf0;
    border-radius: 16px;
    padding: 1.75rem;
    margin-bottom: 1.25rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.04);
    transition: box-shadow 0.2s ease;
}
.card:hover { box-shadow: 0 2px 8px rgba(0,0,0,0.08), 0 8px 24px rgba(0,0,0,0.06); }
.card-label {
    font-family: 'Syne', sans-serif;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #9ca3af;
    margin-bottom: 0.75rem;
}
.card-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.05rem;
    font-weight: 700;
    color: #111827;
    margin-bottom: 0.35rem;
}

/* ── Score Ring ── */
.score-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 1.5rem 0;
}
.score-ring-container {
    position: relative;
    width: 160px;
    height: 160px;
}
.score-ring-container svg {
    transform: rotate(-90deg);
}
.score-inner {
    position: absolute;
    inset: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}
.score-number {
    font-family: 'Syne', sans-serif;
    font-size: 2.8rem;
    font-weight: 800;
    line-height: 1;
    letter-spacing: -0.03em;
}
.score-label {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #9ca3af;
    margin-top: 4px;
}
.score-tier {
    margin-top: 1rem;
    font-family: 'Syne', sans-serif;
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    padding: 0.3rem 0.9rem;
    border-radius: 100px;
}
.tier-high { background: #d1fae5; color: #065f46; }
.tier-mid  { background: #fef3c7; color: #92400e; }
.tier-low  { background: #fee2e2; color: #991b1b; }

/* ── Pills / Tags ── */
.pill {
    display: inline-block;
    background: #f3f4f6;
    color: #374151;
    padding: 0.3rem 0.8rem;
    border-radius: 100px;
    font-size: 0.8rem;
    font-weight: 500;
    margin: 0.2rem;
    border: 1px solid #e5e7eb;
    transition: all 0.15s;
}
.pill:hover { background: #eef2ff; border-color: #c7d2fe; color: #4f46e5; }
.pill-missing {
    display: inline-block;
    background: #fef9f0;
    color: #b45309;
    padding: 0.3rem 0.8rem;
    border-radius: 100px;
    font-size: 0.8rem;
    font-weight: 500;
    margin: 0.2rem;
    border: 1px solid #fde68a;
}

/* ── Bullet Cards ── */
.bullet-weak {
    background: #fff5f5;
    border: 1px solid #fecaca;
    border-left: 3px solid #ef4444;
    padding: 0.85rem 1rem;
    border-radius: 0 10px 10px 0;
    margin-bottom: 0.65rem;
    font-size: 0.875rem;
    line-height: 1.55;
    color: #7f1d1d;
}
.bullet-strong {
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    border-left: 3px solid #22c55e;
    padding: 0.85rem 1rem;
    border-radius: 0 10px 10px 0;
    margin-bottom: 0.65rem;
    font-size: 0.875rem;
    line-height: 1.55;
    color: #14532d;
}
.bullet-col-header {
    font-family: 'Syne', sans-serif;
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    padding: 0.4rem 0.8rem;
    border-radius: 8px;
    margin-bottom: 0.85rem;
    display: inline-block;
}
.bch-weak  { background: #fee2e2; color: #991b1b; }
.bch-strong { background: #dcfce7; color: #166534; }

/* ── Section Feedback Accordion ── */
.feedback-item {
    background: #f9fafb;
    border: 1px solid #f3f4f6;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.6rem;
}
.feedback-section-name {
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 0.9rem;
    color: #111827;
    margin-bottom: 0.4rem;
}
.feedback-text {
    font-size: 0.875rem;
    color: #4b5563;
    line-height: 1.6;
}

/* ── PRIMARY CTA BUTTONS (FINAL WORKING FIX) ── */

/* 1. Target ONLY main area buttons (Analyze buttons) */
section[data-testid="stAppViewContainer"] 
div[data-testid="stButton"] > button {

    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #a855f7 100%) !important;
    color: white !important;

    border: none !important;
    border-radius: 12px !important;

    min-width: 200px !important;
    padding: 0.9rem 1.6rem !important;

    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;

    box-shadow: 0 6px 18px rgba(79,70,229,0.35) !important;

    transition: all 0.2s ease-in-out !important;
}

/* 2. Fix text color inside button */
section[data-testid="stAppViewContainer"] 
div[data-testid="stButton"] > button * {
    color: white !important;
}

/* 3. Hover effect */
section[data-testid="stAppViewContainer"] 
div[data-testid="stButton"] > button:hover {
    background: linear-gradient(135deg, #4338ca 0%, #6d28d9 100%) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 10px 25px rgba(79,70,229,0.45) !important;
}

/* 4. PROTECT other buttons (IMPORTANT) */
.stDownloadButton > button {
    background: white !important;
    color: #4f46e5 !important;
}
              
/* ── Inputs (SAFE TARGETING) ── */

/* Target ONLY real text inputs (NOT Streamlit containers) */
input[type="text"],
textarea {
    border: 1.5px solid #e5e7eb !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9rem !important;
    transition: border-color 0.2s !important;
}

/* Focus styles */
input[type="text"]:focus,
textarea:focus {
    border-color: #4f46e5 !important;
    box-shadow: 0 0 0 3px rgba(79,70,229,0.1) !important;
}


/* ===== SELECTBOX FIX (CLEAN, NO HACKS) ===== */

/* Make it behave like a dropdown (pointer everywhere) */
.stSelectbox * {
    cursor: pointer !important;
}

/* ===== FINAL SELECTBOX FIX ===== */

/* Keep it functional but remove typing feel completely */
.stSelectbox input {
    opacity: 0 !important;          /* hide visually */
    position: absolute !important;  /* keep it in DOM */
    pointer-events: none !important; /* 🔥 prevent text cursor */
}

/* Remove blinking cursor + enforce pointer */
.stSelectbox div[role="combobox"] {
    caret-color: transparent !important;
    cursor: pointer !important;
}
/* ── File Uploader ── */
[data-testid="stFileUploader"] {
    border: 2px dashed #d1d5db;
    border-radius: 14px;
    padding: 1.5rem;
    background: #fafafa;
    transition: all 0.2s;
}
[data-testid="stFileUploader"]:hover {
    border-color: #4f46e5;
    background: #fafafe;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #f3f4f6;
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
    border: none;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 7px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    letter-spacing: 0.02em !important;
    padding: 0.45rem 1.1rem !important;
    color: #6b7280 !important;
    border: none !important;
    background: transparent !important;
}
.stTabs [aria-selected="true"] {
    background: white !important;
    color: #111827 !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.1) !important;
}
.stTabs [data-baseweb="tab-panel"] { padding-top: 1rem !important; }

/* ── Divider ── */
hr { border: none; border-top: 1px solid #f0f0f3; margin: 2.5rem 0; }


/* ── Success banner ── */
.success-banner {
    background: linear-gradient(135deg, #d1fae5, #a7f3d0);
    border: 1px solid #6ee7b7;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    text-align: center;
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    color: #065f46;
    font-size: 0.95rem;
    margin-bottom: 1.5rem;
}

/* ── Section divider label ── */
.section-label {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin: 2.5rem 0.2rem 1.27rem;
}
.section-label-text {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 1.1rem;
    color: #111827;
    white-space: nowrap;
}
.section-label-line {
    flex: 1;
    height: 1px;
    background: linear-gradient(to right, #e5e7eb, transparent);
}

/* ── API key expander ── */
details summary { cursor: pointer; }
.stExpander { border: 1px solid #eaecf0 !important; border-radius: 12px !important; }

/* ── Spinner ── */
.stSpinner > div { border-top-color: #4f46e5 !important; }

/* ── Download button ── */
.stDownloadButton > button {
    background: white !important;
    color: #4f46e5 !important;
    border: 1.5px solid #4f46e5 !important;
    border-radius: 10px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.88rem !important;
    box-shadow: none !important;
}
.stDownloadButton > button:hover {
    background: #eef2ff !important;
    transform: translateY(-1px) !important;
}

.stDownloadButton {
    margin-bottom: -10px !important;
}

div[data-testid="stButton"] > button {
    
    margin-left: 40px;
    margin-top: 5px;

    background: white !important;
    color: #4f46e5 !important;

    border: 1.5px solid #7c3aed !important;
    border-radius: 12px !important;

    min-width: 100px !important;
    padding: 0  !important;

    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;

    box-shadow: 0 4px 12px rgba(0,0,0,0.08) !important;

    transition: all 0.25s ease-in-out !important;
}

div[data-testid="stButton"] > button:hover {
    
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #a855f7 100%) !important;
    color: white !important;

    border: none !important;

    transform: translateY(-2px);
    box-shadow: 0 10px 25px rgba(79,70,229,0.45);
}
        
</style>
""", unsafe_allow_html=True)

# ─── Sidebar ──────────────────────────────────────────────────────────────────
# with st.sidebar:
#     st.markdown("""
#     <div style="font-family:'Syne',sans-serif;font-weight:800;padding-left:1.5rem;font-size:1.5rem;
#                 color:#111827;margin-bottom:1.5rem;padding-bottom:1rem;
#                 border-bottom:1px solid #f0f0f3;">
#         AI Resume 
#     </div>
#     <div style="font-family:'Syne',sans-serif;font-size:1rem;font-weight:700;padding-left:0.3rem;
#                 letter-spacing:0.1em;text-transform:uppercase;color:#9ca3af;margin-bottom:0.75rem;">
#         Analysis History
#     </div>
#     """, unsafe_allow_html=True)

#     # ✅ MOVE THIS INSIDE
#     history_df = load_history()

#     if history_df is not None and not history_df.empty:
#         for i, row in history_df.head(10).iterrows():
            
#             dt = datetime.strptime(row['timestamp'], "%Y-%m-%d %H:%M:%S")
#             formatted_time = dt.strftime("%d %b, %I:%M %p").replace(" ", "\u00A0")

#             label = f"{row['job_role']} • {row['score']}/100 • {formatted_time}"

#             if st.button(label, key=f"card_{i}"):
#                 st.session_state.loaded_result = {
#                     "score": row["score"],
#                     "summary": row["summary"],
#                     "missing_skills": json.loads(row["missing_skills"]),
#                     "section_feedback": json.loads(row.get("section_feedback", "{}")),
#                     "weak_bullets": json.loads(row.get("weak_bullets", "[]")),
#                     "improved_bullets": json.loads(row.get("improved_bullets", "[]")),
#                 }
#                 st.session_state.current_job_role = row["job_role"]
#                 st.session_state.analysis_done = True
#                 st.session_state.result = None
#                 st.success("Loaded!")
#     else:
#         st.markdown("""
#         <div style="font-size:0.85rem;color:#9ca3af;padding:1rem;
#                     background:#f9fafb;border-radius:10px;text-align:center;">
#             Your analyses will appear here
#         </div>
#         """, unsafe_allow_html=True)

# ─── Hero ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">AI-Powered · Instant · Actionable</div>
    <h1>Your resume,<br><span>reimagined.</span></h1>
    <p>Upload your resume, pick a target role, and get expert-level feedback in seconds.</p>
</div>
""", unsafe_allow_html=True)

# ─── Determine step ───────────────────────────────────────────────────────────
has_resume = bool(st.session_state.get("resume_text", "").strip())
has_role = bool(st.session_state.get("current_job_role", "").strip())
has_api = bool(st.session_state.get("api_key_input", "").strip())

if st.session_state.analysis_done:
    current_step = 3
elif has_resume and has_role and has_api:
    current_step = 2
else:
    current_step = 1

def step_classes(n):
    if n < current_step:
        return "complete"
    elif n == current_step:
        return "active"
    else:
        return "inactive"

def line_class(n):
    return "complete" if n < current_step else ""

st.markdown(f"""
<div class="step-indicator">
  <div class="step-wrapper">
    <div class="step-dot {step_classes(1)}">1<span class="step-label">Input</span></div>
  </div>
  <div class="step-line {line_class(1)}"></div>
  <div class="step-wrapper">
    <div class="step-dot {step_classes(2)}">2<span class="step-label">Configure</span></div>
  </div>
  <div class="step-line {line_class(2)}"></div>
  <div class="step-wrapper">
    <div class="step-dot {step_classes(3)}">3<span class="step-label">Results</span></div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── STEP 1 + 2: Input + Config ───────────────────────────────────────────────
analyze_clicked = False
if not st.session_state.analysis_done or "loaded_result" not in st.session_state:

    input_col, config_col = st.columns([3, 2], gap="large")

    # ── RIGHT: CONFIG ──
    with config_col:
        st.markdown("""
        <div class="section-label">
        <span class="section-label-text">Configure</span>
        <div class="section-label-line"></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<p style="font-size:0.9rem;font-weight:600;padding-left:0.3rem;color:#374151;margin-bottom:0.4rem;">Target Job Role</p>', unsafe_allow_html=True)

        job_roles = [
            "Select a role...",
            "Software Engineer", "Data Scientist", "Product Manager",
            "Frontend Developer", "Backend Developer", "DevOps Engineer",
            "ML Engineer", "Full Stack Developer", "UX Designer",
            "Business Analyst", "Custom (type below)",
        ]

        selected_role = st.selectbox(
            "Role",
            job_roles,
            index=0,
            label_visibility="collapsed"
        )

        # 🔥 Clear custom input if not selected
        if selected_role != "Custom (type below)":
            st.session_state.pop("custom_role_input", None)

        # 🔥 Conditional rendering
        if selected_role == "Custom (type below)":
            job_role = st.text_input(
                "Custom role",
                placeholder="e.g., Blockchain Developer",
                label_visibility="collapsed",
                key="custom_role_input"
            )
        elif selected_role == "Select a role...":
            job_role = ""
        else:
            job_role = selected_role

        st.session_state.current_job_role = job_role

        st.markdown('<div style="margin-top:6px;"></div>', unsafe_allow_html=True)

        with st.expander(" API Key", expanded=True):
            api_key = st.text_input(
                "Gemini API Key",
                type="password",
                placeholder="Paste your Gemini API key…",
                label_visibility="collapsed",
                key="api_key_input" 
            )

            st.info(" This app requires your own Gemini API key. Your key is NOT stored anywhere.")

        # ✅ LOGIC
        resume_ready = bool(st.session_state.get("resume_text", "").strip())
        role_ready = selected_role != "Select a role..." and bool(job_role.strip())
        key_ready = bool(st.session_state.get("api_key_input", "").strip())

    # ── LEFT: INPUT ──
    with input_col:
        st.markdown("""
        <div class="section-label">
         <span class="section-label-text"> Resume</span>
        <div class="section-label-line"></div>
        </div>
        """, unsafe_allow_html=True)

        tab_upload, tab_paste = st.tabs([" Upload PDF ", " Paste Text "])

        with tab_upload:
            uploaded_file = st.file_uploader(
                "Drop your PDF resume here",
                type=["pdf"],
                label_visibility="collapsed",
            )

            if uploaded_file is not None:
                if "uploaded_file_name" not in st.session_state or \
                st.session_state.uploaded_file_name != uploaded_file.name:

                    with st.spinner("Extracting text…"):
                        text = extract_text_from_pdf(uploaded_file)
                        st.session_state.resume_text = text
                        st.session_state.uploaded_file_name = uploaded_file.name

        with tab_paste:

            if "resume_input" not in st.session_state:
                st.session_state.resume_input = ""

            st.text_area(
                "Resume text",
                height=220,
                placeholder="Paste your full resume here…",
                label_visibility="collapsed",
                key="resume_input"
            )

            # 🔥 Persist safely
            if st.session_state.resume_input.strip():
                st.session_state.resume_text = st.session_state.resume_input


        left_col, right_col = st.columns([3, 2])
        
        
        with left_col:
            if not key_ready:
                st.markdown(
                    '<p style="color:#9ca3af; margin:2px 0 0 0; line-height:1.3;">⬡ Enter API key</p>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    '<p style="color:#16a34a; margin:2px 0 0 0; line-height:1.3;">✓ API key added</p>',
                    unsafe_allow_html=True
                )

            if not role_ready:
                st.markdown(
                    '<p style="color:#9ca3af; margin:2px 0 0 0; line-height:1.3;">⬡ Select role</p>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    '<p style="color:#16a34a; margin:2px 0 0 0; line-height:1.3;">✓ Role selected</p>',
                    unsafe_allow_html=True
                )
        with right_col:
            analyze_clicked = st.button(
                "Analyze My Resume",
                key="main_cta_button",
                disabled=(not resume_ready or not role_ready or not key_ready)
                
                )
# ─── Run Analysis ─────────────────────────────────────────────────────────────
if analyze_clicked:
    job_role = st.session_state.current_job_role

    with st.spinner("AI is analyzing your resume…"):
        result = analyze_resume(
            resume_text=st.session_state.resume_text,
            job_role=job_role,
            api_key=st.session_state.get("api_key_input", ""),
        )
    if result.get("error"):
        st.error(f"Analysis failed: {result['error']}")
        st.info("Check your API key and try again.")
        st.stop()
    else:
        st.session_state.result = result
        st.session_state.analysis_done = True
        st.session_state.current_job_role = job_role
        # save_to_csv(
        #     resume_text=st.session_state.resume_text,
        #     job_role=job_role,
        #     score=result.get("score", 0),
        #     summary=result.get("summary", ""),
        #     missing_skills=result.get("missing_skills", []),
        #     section_feedback=result.get("section_feedback", {}),
        #     weak_bullets=result.get("weak_bullets", []),
        #     improved_bullets=result.get("improved_bullets", []),
        # )
        st.rerun()

# ─── STEP 3: Results ──────────────────────────────────────────────────────────
if st.session_state.analysis_done:

    if "loaded_result" in st.session_state and not st.session_state.result:
        result = st.session_state.loaded_result
    else:
        result = st.session_state.result

    if result:
        score = result.get("score", 0)
        job_role_display = st.session_state.current_job_role

        st.markdown("""
        <div class="success-banner">
            ✓ Analysis complete
        </div>
        """, unsafe_allow_html=True)

        # ── Score + Summary Row ──
        score_col, summary_col = st.columns([1, 2], gap="large")

        with score_col:
            # Color thresholds
            if score >= 75:
                ring_color = "#22c55e"
                tier_class = "tier-high"
                tier_label = "Strong"
            elif score >= 50:
                ring_color = "#f59e0b"
                tier_class = "tier-mid"
                tier_label = "Needs Work"
            else:
                ring_color = "#ef4444"
                tier_class = "tier-low"
                tier_label = "Needs Major Work"

            radius = 68
            circ = 2 * 3.14159 * radius
            dash = circ * (score / 100)
            gap = circ - dash

            st.markdown(f"""
            <div class="card" style="text-align:center;padding:2rem 1.5rem;">
                <div class="card-label">Resume Score</div>
                <div class="score-wrapper">
                    <div class="score-ring-container">
                        <svg viewBox="0 0 160 160" width="160" height="160">
                            <circle cx="80" cy="80" r="{radius}" fill="none"
                                    stroke="#f3f4f6" stroke-width="10"/>
                            <circle cx="80" cy="80" r="{radius}" fill="none"
                                    stroke="{ring_color}" stroke-width="10"
                                    stroke-dasharray="{dash:.1f} {gap:.1f}"
                                    stroke-linecap="round"/>
                        </svg>
                        <div class="score-inner">
                            <div class="score-number" style="color:{ring_color};">{score}</div>
                            <div class="score-label">out of 100</div>
                        </div>
                    </div>
                    <div class="score-tier {tier_class}">{tier_label}</div>
                </div>
                <div style="font-size:0.8rem;color:#6b7280;margin-top:0.5rem;">
                    Target: <b style="color:#111827;">{job_role_display}</b>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with summary_col:
            st.markdown("""
            <div class="section-label" style="margin-top:0;">
              <span class="section-label-text">Overview</span>
              <div class="section-label-line"></div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"""
            <div class="card">
                <div class="card-label">AI Summary</div>
                <p style="font-size:0.93rem;line-height:1.75;color:#374151;margin:0;">
                    {result.get("summary", "")}
                </p>
            </div>
            """, unsafe_allow_html=True)

        # ─── Results Tabs ───────────────────────────────────────────────────
        tab1, tab2, tab3, tab4 = st.tabs([
            "   Section Feedback  ",
            "   Missing Skills  ",
            "   Bullet Analysis  ",
            "   Export  ",
        ])

        # ── Tab 1: Section Feedback ──
        with tab1:
            section_fb = result.get("section_feedback", {})
            if section_fb:
                for section, feedback in section_fb.items():
                    st.markdown(f"""
                    <div class="feedback-item">
                        <div class="feedback-section-name">{section}</div>
                        <div class="feedback-text">{feedback}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                render_section_feedback(section_fb)

        # ── Tab 2: Missing Skills ──
        with tab2:
            missing = result.get("missing_skills", [])
            if missing:
                st.markdown(f"""
                <div class="card-label" style="margin-bottom:0.75rem;">
                    Skills to add for <b>{job_role_display}</b>
                </div>
                <div style="margin-bottom:1.5rem;">
                """, unsafe_allow_html=True)
                pills_html = "".join([f'<span class="pill-missing">{s}</span>' for s in missing])
                st.markdown(f'<div style="margin-bottom:1.5rem;">{pills_html}</div>', unsafe_allow_html=True)
                st.markdown(f"""
                <div style="background:#fffbeb;border:1px solid #fde68a;border-radius:12px;
                            padding:1rem 1.25rem;font-size:0.85rem;color:#78350f;line-height:1.6;">
                    💡 Consider adding these skills through projects, certifications, or coursework —
                    then highlight them clearly in your resume.
                </div>
                """, unsafe_allow_html=True)
            else:
                st.success("🎉 Great news — no critical missing skills detected!")

        # ── Tab 3: Bullet Analysis ──
        with tab3:
            weak = result.get("weak_bullets", [])
            improved = result.get("improved_bullets", [])

            if weak:
                b_col1, b_col2 = st.columns(2, gap="medium")
                with b_col1:
                    st.markdown('<span class="bullet-col-header bch-weak">❌ Weak Bullets</span>', unsafe_allow_html=True)
                    for b in weak:
                        st.markdown(f'<div class="bullet-weak">{b}</div>', unsafe_allow_html=True)
                with b_col2:
                    st.markdown('<span class="bullet-col-header bch-strong">✅ AI-Improved</span>', unsafe_allow_html=True)
                    for b in improved:
                        st.markdown(f'<div class="bullet-strong">{b}</div>', unsafe_allow_html=True)
            else:
                st.success("🎉 No weak bullet points detected — your bullets look strong!")

        # ── Tab 4: Export ──
        with tab4:
            from reportlab.platypus import (
                SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            )
            from reportlab.lib import colors
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.pagesizes import A4
            import io

            buffer = io.BytesIO()

            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=40,
                leftMargin=40,
                topMargin=50,
                bottomMargin=40
            )

            styles = getSampleStyleSheet()

            # 🎨 Styles
            title_style = ParagraphStyle(
                name="Title",
                fontSize=22,
                leading=26,
                textColor=colors.white,
                alignment=1,
            )

            section_title = ParagraphStyle(
                name="SectionTitle",
                fontSize=14,
                leading=18,
                textColor=colors.HexColor("#111827"),
                spaceAfter=6,
                spaceBefore=14
            )

            normal = ParagraphStyle(
                name="Normal",
                fontSize=10.5,
                leading=15,
                textColor=colors.HexColor("#374151"),
            )

            highlight = ParagraphStyle(
                name="Highlight",
                fontSize=10.5,
                leading=15,
                textColor=colors.HexColor("#4f46e5"),
            )

            content = []

            # ───────── HEADER ─────────
            header = Table(
                [[Paragraph("AI Resume Analysis Report", title_style)]],
                colWidths=[450]
            )
            header.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#4f46e5")),
                ("INNERPADDING", (0, 0), (-1, -1), 14),
            ]))

            content.append(header)
            content.append(Spacer(1, 18))
            
            
            # ───────── SCORE COLOR ─────────
            
            if score >= 75:
                score_color = "#22c55e"
            elif score >= 50:
                score_color = "#f59e0b"
            else:
                score_color = "#ef4444"

            # ───────── SCORE CARD (ALWAYS RUNS) ─────────
            score_card = Table(
                [[
                    Paragraph(f"<b>Target Role</b><br/>{job_role_display}", normal),
                    Paragraph(
                        f"<para align='right'><font size=18 color='{score_color}'><b>{score}/100</b></font></para>",
                        normal
                    )
                ]],
                colWidths=[300, 150]
            )

            score_card.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f9fafb")),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#e5e7eb")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ]))

            content.append(score_card)
            content.append(Spacer(1, 12))

            # Divider
            content.append(Table([[""]], colWidths=[450], style=[
                ("LINEBELOW", (0, 0), (-1, -1), 1, colors.HexColor("#e5e7eb"))
            ]))

            # ───────── SUMMARY (CARD STYLE) ─────────
            content.append(Paragraph("Summary", section_title))

            summary_box = Table(
                [[Paragraph(result.get("summary", ""), normal)]],
                colWidths=[450]
            )
            summary_box.setStyle(TableStyle([
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#e5e7eb")),
                ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                ("INNERPADDING", (0, 0), (-1, -1), 12),
            ]))

            content.append(summary_box)

            # ───────── SECTION FEEDBACK ─────────
            content.append(Paragraph("Section Feedback", section_title))

            for section, feedback in result.get("section_feedback", {}).items():
                box = Table(
                    [[Paragraph(f"<b>{section.title()}</b><br/>{feedback}", normal)]],
                    colWidths=[450]
                )
                box.setStyle(TableStyle([
                    ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#e5e7eb")),
                    ("INNERPADDING", (0, 0), (-1, -1), 10),
                ]))
                content.append(box)
                content.append(Spacer(1, 6))

            # ───────── MISSING SKILLS ─────────
            skills = result.get("missing_skills", [])
            if skills:
                content.append(Paragraph("Missing Skills", section_title))

                table_data = [[s] for s in skills]

                table = Table(table_data, colWidths=[450])
                table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#eef2ff")),
                    ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#1e3a8a")),
                    ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#c7d2fe")),
                    ("INNERPADDING", (0, 0), (-1, -1), 8),
                ]))

                content.append(table)

            # ───────── BULLET IMPROVEMENTS (2-COLUMN) ─────────
            content.append(Paragraph("Bullet Improvements", section_title))

            for w, i in zip(
                result.get("weak_bullets", []),
                result.get("improved_bullets", [])
            ):
                row = [
                    Paragraph(f"<b>❌ Before</b><br/>{w}", normal),
                    Paragraph(f"<b>✅ After</b><br/>{i}", highlight),
                ]

                table = Table([row], colWidths=[225, 225])

                table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#fef2f2")),
                    ("BACKGROUND", (1, 0), (1, 0), colors.HexColor("#f0fdf4")),
                    ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#e5e7eb")),
                    ("INNERPADDING", (0, 0), (-1, -1), 10),
                ]))

                content.append(table)
                content.append(Spacer(1, 10))

            # ───────── FOOTER ─────────
            def add_footer(canvas, doc):
                canvas.setFont("Helvetica", 8)
                canvas.setFillColor(colors.grey)
                canvas.drawString(40, 20, "Generated by AI Resume Analyzer")

            # ───────── BUILD ─────────
            doc.build(content, onFirstPage=add_footer, onLaterPages=add_footer)

            pdf_data = buffer.getvalue()
            buffer.close()

            st.markdown("""
            <div class="card" style="text-align:center;padding:2.5rem;">
                <div style="font-size:2.5rem;margin-bottom:1rem;">📄</div>
                <div class="card-title">Download Your Report</div>
                <p style="font-size:0.875rem;color:#6b7280;margin-bottom:1.5rem;">
                    Get a PDF summary of your analysis to share or save.
                </p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<div style='margin-bottom: 5px;'></div>", unsafe_allow_html=True)
            st.download_button(
                label="⬇ Download PDF Report",
                data=pdf_data,
                file_name=f"resume_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf",
            )
        # ── Re-analyze button ──
        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
        if st.button("↺ Analyze a Different Resume", key="reanalyze_button"):
            st.session_state.resume_text = ""
            st.session_state.analysis_done = False
            st.session_state.result = None
            if "loaded_result" in st.session_state:
                del st.session_state.loaded_result
                st.rerun()

