"""
utils/display.py
────────────────
All Streamlit rendering functions live here.
Keeps app.py clean and focused on layout/flow.

Each function takes data and renders it to the Streamlit UI.
"""

import streamlit as st


def render_score_gauge(score: int):
    """
    Render the overall score as a styled card with a color-coded rating.

    Args:
        score: Integer score between 0 and 100
    """
    # Determine color and label based on score range
    if score >= 80:
        color = "#38a169"   # Green
        label = "Excellent 🎉"
    elif score >= 65:
        color = "#d69e2e"   # Yellow/Gold
        label = "Good 👍"
    elif score >= 50:
        color = "#dd6b20"   # Orange
        label = "Average ⚠️"
    else:
        color = "#e53e3e"   # Red
        label = "Needs Work 🔧"

    st.markdown(f"""
    <div class="score-card">
        <div style="font-size: 0.85rem; color: #888; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0.5rem;">
            Overall Score
        </div>
        <div class="score-number" style="color: {color};">{score}</div>
        <div style="font-size: 0.75rem; color: #aaa; margin-top: 0.2rem;">out of 100</div>
        <div style="margin-top: 1rem;">
            <div style="background: #f0f0f0; border-radius: 20px; height: 10px; overflow: hidden;">
                <div style="background: {color}; width: {score}%; height: 100%; border-radius: 20px; transition: width 1s ease;"></div>
            </div>
        </div>
        <div style="margin-top: 0.75rem; font-weight: 600; color: {color}; font-size: 1.1rem;">{label}</div>
    </div>
    """, unsafe_allow_html=True)


def render_section_feedback(section_feedback: dict):
    """
    Render section-by-section AI feedback in expandable cards.

    Args:
        section_feedback: Dict with keys like 'skills', 'experience', etc.
    """
    # Icons for each section
    icons = {
        "skills": "🛠️",
        "experience": "💼",
        "projects": "🚀",
        "education": "🎓",
        "formatting": "📐",
    }

    # Determine rating color based on keywords in feedback text
    def get_rating_color(text: str) -> str:
        text_lower = text.lower()
        if any(w in text_lower for w in ["excellent", "strong", "great", "outstanding", "impressive"]):
            return "#38a169"
        elif any(w in text_lower for w in ["missing", "absent", "lacks", "no ", "not found", "weak", "poor"]):
            return "#e53e3e"
        else:
            return "#d69e2e"

    cols = st.columns(2)

    for i, (section, feedback) in enumerate(section_feedback.items()):
        icon = icons.get(section, "📌")
        color = get_rating_color(feedback)
        col = cols[i % 2]

        with col:
            st.markdown(f"""
            <div style="border: 1px solid #e2e8f0; border-radius: 12px; padding: 1rem; margin-bottom: 1rem; border-top: 3px solid {color};">
                <div style="font-weight: 600; font-size: 0.95rem; margin-bottom: 0.5rem; color: #2d3748;">
                    {icon} {section.title()}
                </div>
                <div style="font-size: 0.88rem; color: #4a5568; line-height: 1.5;">
                    {feedback}
                </div>
            </div>
            """, unsafe_allow_html=True)


def render_missing_skills(missing_skills: list):
    """
    Render missing skills as tag pills.

    Args:
        missing_skills: List of skill name strings
    """
    if not missing_skills:
        st.success("✅ No critical missing skills detected for this role!")
        return

    st.markdown(
        "<div style='line-height: 2.2;'>"
        + "".join([f'<span class="tag">⚡ {skill}</span>' for skill in missing_skills])
        + "</div>",
        unsafe_allow_html=True,
    )

    st.caption(f"Consider adding these {len(missing_skills)} skills to strengthen your resume for this role.")


def render_weak_bullets(weak_bullets: list):
    """
    Render weak/poor bullet points highlighted in red.

    Args:
        weak_bullets: List of weak bullet point strings
    """
    if not weak_bullets:
        st.success("No weak bullets found!")
        return

    for bullet in weak_bullets:
        st.markdown(
            f'<div class="weak-bullet">❌ {bullet}</div>',
            unsafe_allow_html=True,
        )


def render_improved_bullets(improved_bullets: list):
    """
    Render AI-rewritten improved bullet points highlighted in green.

    Args:
        improved_bullets: List of improved bullet point strings
    """
    if not improved_bullets:
        st.info("No improvements generated.")
        return

    for bullet in improved_bullets:
        st.markdown(
            f'<div class="strong-bullet">✅ {bullet}</div>',
            unsafe_allow_html=True,
        )


def render_automation_section():
    """
    Render the automation/extension ideas section.
    This is purely informational — shows how the tool can be extended
    using workflow automation platforms like n8n or Zapier.
    """
    st.markdown("##  Extend With Automation")

    st.markdown("""
    <div class="automation-card">
        <h4 style="margin-top: 0; font-family: 'DM Serif Display', serif;">
            How to Automate This Tool Further
        </h4>
        <p style="color: #4a5568; margin-bottom: 1.5rem;">
            This tool can be extended into a full automation pipeline using 
            <strong>n8n</strong> (open-source), <strong>Zapier</strong>, or <strong>Make</strong>.
            Here are powerful workflows you can build:
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        #### Auto Email Feedback
        **n8n Workflow:**
        1. User submits resume via form
        2. n8n triggers this analyzer via webhook
        3. AI generates feedback JSON
        4. n8n sends formatted email with score + tips
        5. Feedback arrives in inbox automatically

        **Tools:** n8n + Gmail/SendGrid + Webhook node
        """)

    with col2:
        st.markdown("""
        #### Track Improvement Over Time
        **n8n Workflow:**
        1. User re-analyzes resume monthly
        2. Each result saved to Google Sheets
        3. n8n runs scheduled comparison job
        4. Generates "improvement report" chart
        5. Sends progress email to user

        **Tools:** n8n + Google Sheets + Cron node
        """)

    with col3:
        st.markdown("""
        ####  Job Match Alerts
        **n8n Workflow:**
        1. Extract skills from resume analysis
        2. n8n searches LinkedIn/job APIs daily
        3. Matches open roles to your skill profile
        4. Sends Slack/Telegram alerts for matches
        5. Tracks application status in Notion

        **Tools:** n8n + LinkedIn API + Slack/Telegram
        """)

    with st.expander(" How to Set Up n8n for This Project"):
        st.markdown("""
        **Step 1: Install n8n locally**
        ```bash
        npm install -g n8n
        n8n start
        ```

        **Step 2: Create a Webhook node in n8n**
        - Open n8n at `http://localhost:5678`
        - Create a new workflow
        - Add a **Webhook** node — this becomes your API endpoint

        **Step 3: Call the webhook from this Streamlit app**
        - In `utils/storage.py`, after saving to CSV, add:
        ```python
        import requests
        requests.post("http://localhost:5678/webhook/resume", json={
            "score": score,
            "job_role": job_role,
            "email": "user@example.com",
            "summary": summary
        })
        ```

        **Step 4: Add Gmail / SendGrid node in n8n**
        - Connect the Webhook → Gmail node
        - Template the email body with the JSON data
        - Activate workflow — done! 🎉

        **Result:** Every time someone analyzes a resume, an email is auto-sent with their score and top tips.
        """)
