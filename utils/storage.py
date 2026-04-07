"""
utils/storage.py
────────────────
Handles saving analysis results to a local CSV file
and loading history for display in the sidebar.

Now stores FULL analysis for session replay.
"""

import os
import csv
import json
import pandas as pd
from datetime import datetime

# Path to the data directory and CSV file
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
CSV_PATH = os.path.join(DATA_DIR, "results.csv")

# ✅ UPDATED columns (important)
CSV_COLUMNS = [
    "timestamp",
    "job_role",
    "score",
    "summary",
    "missing_skills",
    "resume_snippet",
    "resume_text",
    "section_feedback",
    "weak_bullets",
    "improved_bullets",
]


def _ensure_data_dir():
    """Create the data/ directory if it doesn't exist."""
    os.makedirs(DATA_DIR, exist_ok=True)


def _ensure_csv_exists():
    """Create CSV file with headers if not exists."""
    _ensure_data_dir()

    if not os.path.exists(CSV_PATH):
        with open(CSV_PATH, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
            writer.writeheader()


def save_to_csv(
    resume_text: str,
    job_role: str,
    score: int,
    summary: str,
    missing_skills: list,
    section_feedback: dict,
    weak_bullets: list,
    improved_bullets: list,
) -> bool:
    """
    Save full analysis result to CSV.
    """
    _ensure_csv_exists()

    try:
        row = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "job_role": job_role,
            "score": score,
            "summary": summary.replace("\n", " "),
            "missing_skills": json.dumps(missing_skills),

            # Preview + full text
            "resume_snippet": resume_text[:200].replace("\n", " "),
            "resume_text": resume_text,

            # ✅ FULL RESULT STORAGE
            "section_feedback": json.dumps(section_feedback),
            "weak_bullets": json.dumps(weak_bullets),
            "improved_bullets": json.dumps(improved_bullets),
        }

        with open(CSV_PATH, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
            writer.writerow(row)

        return True

    except Exception as e:
        print(f"[storage] Failed to save: {e}")
        return False


def load_history() -> pd.DataFrame | None:
    """
    Load all saved analysis history.
    """
    _ensure_csv_exists()

    try:
        df = pd.read_csv(CSV_PATH)

        if df.empty:
            return None

        # Sort latest first
        df = df.sort_values("timestamp", ascending=False).reset_index(drop=True)
        return df

    except Exception as e:
        print(f"[storage] Failed to load: {e}")
        return None


def get_score_trend() -> list[dict]:
    """
    Optional: return score trend over time.
    """
    df = load_history()

    if df is None or df.empty:
        return []

    return df[["timestamp", "score"]].sort_values("timestamp").to_dict("records")