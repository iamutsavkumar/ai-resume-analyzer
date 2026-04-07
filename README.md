# 📄 AI Resume Analyzer with Smart Feedback & Automation

An intelligent resume analysis tool built with **Python**, **Streamlit**, and **OpenAI GPT-4o-mini**.
Upload your resume, pick a target job role, and get instant AI-powered feedback with an overall score,
section-wise analysis, missing skills, and rewritten bullet points.

---

## 🗂️ Project Structure

```
ai_resume_analyzer/
│
├── app.py                   # 🚀 Main Streamlit app (entry point)
│
├── utils/
│   ├── __init__.py          # Package marker
│   ├── analyzer.py          # 🤖 OpenAI API call + prompt engineering
│   ├── pdf_extractor.py     # 📄 PDF → text extraction
│   ├── storage.py           # 💾 CSV read/write for history
│   └── display.py           # 🎨 All Streamlit UI rendering functions
│
├── data/
│   └── results.csv          # 📊 Auto-created; stores analysis history
│
├── .streamlit/
│   └── config.toml          # 🎨 Streamlit theme configuration
│
├── .env.example             # 🔑 Template for environment variables
├── .gitignore               # 🚫 Files to exclude from Git
├── requirements.txt         # 📦 Python dependencies
└── README.md                # 📖 This file
```

---

## ✨ Features

| Feature | Description |
|---|---|
| 📤 Resume Input | Upload PDF or paste raw text |
| 🤖 AI Analysis | GPT-powered score (0–100) + section feedback |
| 🧩 Missing Skills | Skills absent from resume for the target role |
| ✍️ Bullet Rewriter | Weak bullets rewritten with metrics + action verbs |
| 💾 Auto Save | Every analysis saved to `data/results.csv` |
| 📊 History Viewer | See past scores in the sidebar |
| ⬇️ JSON Export | Download full analysis as JSON |
| 🔗 Automation Guide | n8n / Zapier integration instructions |

---

## ⚡ Quick Start (Step-by-Step)

### Step 1: Clone or Download the Project

```bash
git clone https://github.com/yourname/ai-resume-analyzer.git
cd ai_resume_analyzer
```

Or just download and unzip it.

---

### Step 2: Create a Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

---

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `streamlit` — for the web UI
- `openai` — to talk to GPT
- `PyMuPDF` + `pdfplumber` — for PDF text extraction
- `pandas` — for CSV history storage

---

### Step 4: Get an OpenAI API Key

1. Go to [platform.openai.com](https://platform.openai.com)
2. Sign up or log in
3. Navigate to **API Keys** → **Create new secret key**
4. Copy the key (starts with `sk-...`)

> **Cost:** GPT-4o-mini is very affordable — roughly $0.01–0.05 per resume analysis.

---

### Step 5: Run the App

```bash
streamlit run app.py
```

Your browser will open automatically at `http://localhost:8501`

---

### Step 6: Use the App

1. **Enter your OpenAI API key** in the left sidebar
2. **Select a target job role** (e.g., Software Engineer)
3. **Upload a PDF resume** or paste text in the "Paste Text" tab
4. Click **"🔍 Analyze My Resume"**
5. Wait ~20–30 seconds for the AI to process
6. Review your score, feedback, missing skills, and improved bullets
7. Download the JSON or check `data/results.csv` for history

---

## 🔑 Environment Variable (Optional)

Instead of pasting your API key every time, create a `.env` file:

```bash
cp .env.example .env
```

Edit `.env`:
```
OPENAI_API_KEY=sk-your-actual-key-here
```

Then in `app.py`, you could auto-load it:
```python
from dotenv import load_dotenv
import os
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY", "")
```

---

## 🔗 Extending with n8n Automation

See the **"Extend With Automation"** section at the bottom of the running app for detailed workflow diagrams. Quick summary:

### Workflow 1: Auto Email Feedback
```
User submits resume → Webhook → AI Analyzer → Gmail/SendGrid → Email delivered
```

### Workflow 2: Track Improvement Over Time
```
Scheduled analysis → Google Sheets log → Monthly comparison → Email progress report
```

### Workflow 3: Job Match Alerts
```
Skills extracted → Job board API → Matching → Slack/Telegram notification
```

---

## 🛠️ Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` again |
| `AuthenticationError` | Check your OpenAI API key — must start with `sk-` |
| `RateLimitError` | Wait 60 seconds and retry |
| PDF text is garbled | Try pasting the text manually instead |
| App doesn't open | Make sure port 8501 isn't blocked; try `--server.port 8502` |

---

## 🧑‍💻 Tech Stack

- **Python 3.10+**
- **Streamlit** — UI framework
- **OpenAI GPT-4o-mini** — AI analysis engine
- **PyMuPDF / pdfplumber** — PDF parsing
- **Pandas** — CSV data storage
- **n8n** (optional) — workflow automation

---

## 📄 License

MIT License. Free to use, modify, and distribute.

