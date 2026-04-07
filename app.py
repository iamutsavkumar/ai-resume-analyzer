"""
AI Resume Analyzer with Smart Feedback & Automation
=====================================================
Main Streamlit application entry point.
Run with: streamlit run app.py
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import os
import json

# Local module imports
from utils.pdf_extractor import extract_text_from_pdf
from utils.analyzer import analyze_resume
from utils.storage import save_to_csv, load_history
from utils.display import (
    render_score_gauge,
    render_section_feedback,
    render_missing_skills,
    render_weak_bullets,
    render_improved_bullets,
    render_automation_section,
)

if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""

# ─── Page Configuration ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    h1, h2, h3 {
        font-family: 'DM Serif Display', serif;
    }

    .main-header {
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
        padding: 2.5rem 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }

    .main-header h1 {
        font-size: 2.6rem;
        margin: 0;
        letter-spacing: -0.5px;
    }

    .main-header p {
        opacity: 0.75;
        font-size: 1.05rem;
        margin-top: 0.5rem;
    }

    .score-card {
        background: white;
        border: 1px solid #e8e8e8;
        border-radius: 14px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    }

    .score-number {
        font-family: 'DM Serif Display', serif;
        font-size: 4rem;
        color: #2c5364;
        line-height: 1;
    }

    .stButton > button {
        background: linear-gradient(135deg, #2c5364, #203a43);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.7rem 2rem;
        font-family: 'DM Sans', sans-serif;
        font-weight: 600;
        font-size: 1rem;
        width: 100%;
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }

    .section-card {
        background: white;
        border-radius: 12px;
        padding: 14px 16px;
        margin-bottom: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.06);
        border-left: 4px solid #2c5364;
    }
    .tag {
        display: inline-block;
        background: #e8f4f8;
        color: #2c5364;
        padding: 0.25rem 0.7rem;
        border-radius: 20px;
        font-size: 0.85rem;
        margin: 0.2rem;
        font-weight: 500;
    }

    .weak-bullet {
        background: #fff5f5;
        border-left: 4px solid #e53e3e;
        padding: 0.75rem 1rem;
        border-radius: 0 8px 8px 0;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
    }

    .strong-bullet {
        background: #f0fff4;
        border-left: 4px solid #38a169;
        padding: 0.75rem 1rem;
        border-radius: 0 8px 8px 0;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
    }

    .automation-card {
        background: linear-gradient(135deg, #f6f9fc, #eef2f7);
        border: 1px solid #d0dce8;
        border-radius: 14px;
        padding: 1.5rem;
        margin-top: 1rem;
    }

    div[data-testid="stSidebarContent"] {
        background: #f4f6f9;
    }
</style>
""", unsafe_allow_html=True)

# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>AI Resume Analyzer</h1>
    <p>Upload your resume · Get AI feedback · Land your dream job</p>
</div>
""", unsafe_allow_html=True)

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Settings")

    # OpenAI API Key input
    api_key = st.text_input(
        "Gemini API Key",
        type="password",
        placeholder="sk-...",
        help="Get your API key from Google AI Studio",
    )

    st.divider()

    # Job role selector
    st.markdown("### Target Job Role")
    job_roles = [
        "Software Engineer",
        "Data Scientist",
        "Product Manager",
        "Frontend Developer",
        "Backend Developer",
        "DevOps Engineer",
        "ML Engineer",
        "Full Stack Developer",
        "UX Designer",
        "Business Analyst",
        "Custom (type below)",
    ]
    selected_role = st.selectbox("Choose a role", job_roles)

    # Allow custom job role
    if selected_role == "Custom (type below)":
        job_role = st.text_input("Enter custom job role", placeholder="e.g., Blockchain Developer")
    else:
        job_role = selected_role

    st.divider()
    st.markdown("### Analysis History")

    # Show history button
    history_df = load_history()

    if history_df is not None and not history_df.empty:
        st.markdown("### 📜 Recent Analyses")

        for i, row in history_df.tail(5).iterrows():
            st.markdown(f"""
            <div style="
                background: white;
                padding: 12px 14px;
                border-radius: 12px;
                margin-bottom: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.06);
                border-left: 5px solid #2c5364;
            ">
                <div style="font-size: 13px; color: #666;">🕒 {row['timestamp']}</div>
                <div style="font-weight: 600; font-size: 15px;">🎯 {row['job_role']}</div>
                <div style="margin-top: 5px;">
                    <span style="
                        background:#e8f4f8;
                        padding:4px 10px;
                        border-radius:20px;
                        font-size:13px;
                        font-weight:600;
                        color:#2c5364;
                    ">
                        📊 {row['score']}/100
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns([1,1])

            # 📂 Load button
            with col2:
                if st.button(f"Load {i}", key=f"load_{i}"):
                    st.session_state.loaded_result = {
                        "score": row["score"],
                        "summary": row["summary"],
                        "missing_skills": json.loads(row["missing_skills"]),
                        "section_feedback": json.loads(row.get("section_feedback", "{}")),
                        "weak_bullets": json.loads(row.get("weak_bullets", "[]")),
                        "improved_bullets": json.loads(row.get("improved_bullets", "[]")),
                        }
                    st.success("Session loaded!")

            st.markdown("---")

    else:
        st.info("No analyses saved yet.")

# ─── Main Content ─────────────────────────────────────────────────────────────
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("### 📤 Upload Your Resume")

    tab_upload, tab_paste = st.tabs(["📎 Upload PDF", "✏️ Paste Text"])

    # ─── Upload Tab ───
    with tab_upload:
        uploaded_file = st.file_uploader(
            "Drop your PDF resume here",
            type=["pdf"],
        )

        if uploaded_file is not None:
            with st.spinner("Extracting text from PDF..."):
                text = extract_text_from_pdf(uploaded_file)
                st.session_state.resume_text = text

            if st.session_state.resume_text:
                st.success(f"✅ Extracted {len(st.session_state.resume_text.split())} words")
                st.text_area("Preview", st.session_state.resume_text[:1500], height=200)
            else:
                st.error("Could not extract text")

    # ─── Paste Tab ───
    with tab_paste:
        text_input = st.text_area("Paste resume here", height=300)

        if text_input:
            st.session_state.resume_text = text_input

with col2:
    st.markdown("### Analyze")
    
    resume_text = st.session_state.resume_text

    if not api_key:
        st.warning("⬅️ Please enter your Gemini API key in the sidebar to get started.")
    if not resume_text:
        st.info("⬅️ Upload a PDF or paste your resume text to begin.")
    if not job_role or job_role == "Custom (type below)":
        st.info("⬅️ Select a target job role from the sidebar.")

    st.markdown("<br>", unsafe_allow_html=True)

    # Analyze button
    resume_text = st.session_state.resume_text

    analyze_clicked = st.button("🔍 Analyze My Resume", disabled=(not api_key or not resume_text or not job_role))


# ─── Analysis Results ─────────────────────────────────────────────────────────
if analyze_clicked or "loaded_result" in st.session_state:

    st.divider()
    st.markdown("## 📊 Analysis Results")

    # ✅ Use loaded result OR run AI
    if "loaded_result" in st.session_state and not analyze_clicked:
        result = st.session_state.loaded_result
    else:
        with st.spinner("🤖 AI is analyzing your resume..."):
            result = analyze_resume(
                resume_text=resume_text,
                job_role=job_role,
                api_key=api_key,
            )

    if result.get("error"):
        st.error(f"❌ Analysis failed: {result['error']}")
        st.info("Check your API key and try again.")
    else:
        # ── Row 1: Score + Summary ──────────────────────────────────────────
        r1_col1, r1_col2 = st.columns([1, 2])

        with r1_col1:
            score = result.get("score", 0)
            
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #203a43, #2c5364);
                color: white;
                padding: 20px;
                border-radius: 16px;
                text-align: center;
            ">
                <div style="font-size: 14px; opacity: 0.8;">Resume Score</div>
                <div style="font-size: 48px; font-weight: bold;">{score}</div>
            </div>
            """, unsafe_allow_html=True)

        with r1_col2:
            st.markdown("#### 📝 Summary")
            st.markdown(f'<div class="section-card">{result.get("summary", "")}</div>', unsafe_allow_html=True)

        st.divider()

        # ── Section Feedback
        st.markdown("#### 🔍 Section-Wise Feedback")
        render_section_feedback(result.get("section_feedback", {}))

        st.divider()

        # ── Missing Skills
        st.markdown(f"#### 🧩 Missing Skills for *{job_role}*")
        render_missing_skills(result.get("missing_skills", []))

        st.divider()

        # ── Bullet Points
        st.markdown("#### ✍️ Bullet Point Analysis")
        weak = result.get("weak_bullets", [])
        improved = result.get("improved_bullets", [])

        if weak:
            b_col1, b_col2 = st.columns(2)
            with b_col1:
                st.markdown("**❌ Weak Bullet Points**")
                render_weak_bullets(weak)
            with b_col2:
                st.markdown("**✅ Rewritten (AI-Improved)**")
                render_improved_bullets(improved)
        else:
            st.success("🎉 No weak bullet points detected!")

        st.divider()

        # ── Save Results
        if analyze_clicked:
            save_to_csv(
                resume_text=resume_text,
                job_role=job_role,
                score=result.get("score", 0),
                summary=result.get("summary", ""),
                missing_skills=result.get("missing_skills", []),
                section_feedback=result.get("section_feedback", {}),
                weak_bullets=result.get("weak_bullets", []),
                improved_bullets=result.get("improved_bullets", []),
                )
            
            st.success("💾 Results saved to `data/results.csv`")

        # ── PDF DOWNLOAD (FIXED) ───────────────────────────────────────────
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        import io

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer)
        styles = getSampleStyleSheet()

        content = []

        content.append(Paragraph("AI Resume Analysis Report", styles["Title"]))
        content.append(Spacer(1, 12))

        content.append(Paragraph(f"<b>Role:</b> {job_role}", styles["Normal"]))
        content.append(Paragraph(f"<b>Score:</b> {result.get('score', 0)}/100", styles["Normal"]))
        content.append(Spacer(1, 12))

        content.append(Paragraph("<b>Summary:</b>", styles["Heading2"]))
        content.append(Paragraph(result.get("summary", ""), styles["Normal"]))
        content.append(Spacer(1, 12))

        content.append(Paragraph("<b>Missing Skills:</b>", styles["Heading2"]))
        content.append(Paragraph(", ".join(result.get("missing_skills", [])), styles["Normal"]))

        doc.build(content)

        pdf_data = buffer.getvalue()
        buffer.close()

        st.download_button(
            label="📄 Download PDF Report",
            data=pdf_data,
            file_name=f"resume_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf",
        )
# ─── Automation Section ────────────────────────────────────────────────────────
st.divider()
render_automation_section()
