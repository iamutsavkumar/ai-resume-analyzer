"""
utils/analyzer.py
─────────────────
Core AI analysis module. Sends resume text to OpenAI's API
and parses structured JSON feedback back.

The prompt is carefully engineered to return a consistent
JSON structure that the rest of the app can rely on.
"""

import json
import re
import google.generativeai as genai


# ─── Prompt Template ──────────────────────────────────────────────────────────

SYSTEM_PROMPT = """
You are an expert resume reviewer and career coach with 15+ years of experience
hiring for top tech companies. Your job is to analyze resumes critically and
provide actionable, specific feedback.

You MUST respond ONLY with valid JSON. No preamble, no explanation, just JSON.
""".strip()


def build_user_prompt(resume_text: str, job_role: str) -> str:
    """
    Build the analysis prompt with resume content and target role injected.

    Args:
        resume_text: Full resume text
        job_role: Target job role (e.g., "Software Engineer")

    Returns:
        str: Formatted prompt string
    """
    return f"""
Analyze the following resume for a candidate applying to the role of: **{job_role}**

---RESUME START---
{resume_text[:4000]}  
---RESUME END---

Return a JSON object with EXACTLY this structure:

{{
  "score": <integer 0-100>,
  "summary": "<2-3 sentence overall assessment>",
  "section_feedback": {{
    "skills": "<specific feedback about skills section>",
    "experience": "<specific feedback about experience section>",
    "projects": "<specific feedback about projects section>",
    "education": "<specific feedback about education section>",
    "formatting": "<feedback on formatting and structure>"
  }},
  "missing_skills": ["<skill1>", "<skill2>", "<skill3>", ...],
  "weak_bullets": [
    "<exact weak bullet point from resume>",
    ...
  ],
  "improved_bullets": [
    "<rewritten version of bullet 1 with metrics and action verbs>",
    ...
  ]
}}

Rules:
- score: Be honest. 70+ is good, 50-69 is average, below 50 needs major work.
- missing_skills: List 5-10 skills important for {job_role} that are absent.
- weak_bullets: Find up to 5 bullets that are vague, passive, or lack metrics.
- improved_bullets: Must be the same count as weak_bullets, in the same order.
- improved bullets must start with a strong action verb and include metrics where possible.
- If a section is missing from the resume, note it in section_feedback.
- Return ONLY the JSON object. No markdown fences, no extra text.
""".strip()


# ─── Main Analyzer ────────────────────────────────────────────────────────────

def analyze_resume(resume_text: str, job_role: str, api_key: str) -> dict:
    """
    Send resume to OpenAI API and return structured analysis.

    Args:
        resume_text: Extracted resume text
        job_role: Target job role for analysis
        api_key: OpenAI API key

    Returns:
        dict: Parsed analysis result, or dict with "error" key on failure
    """
    # Basic validation
    if not resume_text or len(resume_text.strip()) < 50:
        return {"error": "Resume text is too short or empty. Please provide more content."}
    
    if not api_key:
        return {"error": "API key is required."}

    try:
        # Initialize the OpenAI client with the provided key
        genai.configure(api_key=api_key)

        # Automatically find a working model
        models = genai.list_models()

        model = None
        for m in models:
            if "generateContent" in str(m.supported_generation_methods):
                model = genai.GenerativeModel(m.name)
                print("Using model:", m.name)
                break

        if model is None:
            return {"error": "No compatible Gemini model found."}

        response = model.generate_content(
            SYSTEM_PROMPT + "\n\n" + build_user_prompt(resume_text, job_role)
        )

        raw_content = response.text.strip()

        # Parse JSON (handle cases where model adds markdown fences)
        parsed = safe_parse_json(raw_content)

        if parsed is None:
            return {"error": "AI returned an unexpected response format. Please try again."}

        # Validate and fill any missing keys with defaults
        return validate_and_fill(parsed)

    except Exception as e:
        error_msg = str(e)

        # Provide friendlier messages for common errors
        if "authentication" in error_msg.lower() or "api key" in error_msg.lower():
            return {"error": "Invalid API key. Please check your Gemini key."}
        elif "rate limit" in error_msg.lower():
            return {"error": "Rate limit hit. Please wait a moment and try again."}
        elif "quota" in error_msg.lower():
            return {"error": "Quota exceeded. Please check your Gemini usage limits."}
        else:
            return {"error": f"Unexpected error: {error_msg}"}


# ─── Helpers ──────────────────────────────────────────────────────────────────

def safe_parse_json(text: str) -> dict | None:
    """
    Safely parse JSON from a string, stripping markdown fences if present.

    Args:
        text: Raw string from API response

    Returns:
        dict or None if parsing fails
    """
    # Strip markdown code fences like ```json ... ```
    cleaned = re.sub(r"```(?:json)?", "", text).strip().strip("`").strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Try to extract JSON object using regex as a last resort
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass
        return None


def validate_and_fill(data: dict) -> dict:
    """
    Ensure all required keys exist in the parsed response.
    Fill with sensible defaults if anything is missing.

    Args:
        data: Parsed dict from AI response

    Returns:
        dict: Validated and filled result dict
    """
    defaults = {
        "score": 50,
        "summary": "Analysis complete.",
        "section_feedback": {
            "skills": "No feedback available.",
            "experience": "No feedback available.",
            "projects": "No feedback available.",
            "education": "No feedback available.",
            "formatting": "No feedback available.",
        },
        "missing_skills": [],
        "weak_bullets": [],
        "improved_bullets": [],
    }

    # Fill top-level missing keys
    for key, default_value in defaults.items():
        if key not in data:
            data[key] = default_value

    # Ensure score is a valid integer in range [0, 100]
    try:
        data["score"] = max(0, min(100, int(data["score"])))
    except (ValueError, TypeError):
        data["score"] = 50

    # Ensure lists are actually lists
    for list_key in ["missing_skills", "weak_bullets", "improved_bullets"]:
        if not isinstance(data.get(list_key), list):
            data[list_key] = []

    # Ensure section_feedback is a dict
    if not isinstance(data.get("section_feedback"), dict):
        data["section_feedback"] = defaults["section_feedback"]

    return data
