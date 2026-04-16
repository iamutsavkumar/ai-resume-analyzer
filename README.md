# AI Resume Analyzer with Smart Feedback & Automation

An intelligent resume analysis tool built with **Python**, **Streamlit**, and **AI (Gemini/OpenAI)**.
Upload your resume, select a target role, and receive **instant, structured feedback** with scoring, improvements, and insights.

---

## Live Demo

**Try the app here:** [https://utsav-kumar-link.streamlit.app](https://resume-analyzer-utsavkumar.streamlit.app/)

---

## UI Preview

![UI Preview](assets/ui.png)

---

## Features

* LLM-powered resume analysis with structured JSON output
* Role-specific evaluation and scoring (0–100)
* Skill gap detection based on target job role
* Section-wise feedback (Skills, Experience, Projects, etc.)
* AI-generated bullet point improvements
* PDF upload + text extraction (PyMuPDF/pdfplumber)
* Export detailed analysis as PDF report
* Persistent analysis history (CSV storage)
* Automation-ready workflows (n8n / Zapier)

---

## Project Structure

```
ai_resume_analyzer/
│
├── app.py                   # Main Streamlit app
│
├── utils/
│   ├── analyzer.py          # AI analysis logic
│   ├── pdf_extractor.py     # PDF text extraction
│   ├── storage.py           # CSV storage + history
│   └── display.py           # UI rendering functions
│
├── assets/
│   └── ui.png               # UI preview image
│
├── data/
│   └── results.csv          # Stored results
│
├── requirements.txt         # Dependencies
├── .env.example             # Environment variables template
└── README.md                # Documentation
```

---

## ⚡ Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/ai-resume-analyzer.git
cd ai_resume_analyzer
```

---

### 2. Create Virtual Environment

```bash
python -m venv venv

# Activate
# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Add API Key

Create `.env` file:

```bash
cp .env.example .env
```

Then add:

```
GEMINI_API_KEY=your_api_key_here
```

---

### 5. Run the App

```bash
streamlit run app.py
```

Open: http://localhost:8501

---

## How It Works

1. Resume text is extracted from PDF or user input
2. A prompt-engineered request is sent to a Gemini LLM
3. The LLM returns structured JSON containing:
   - Score
   - Summary
   - Section-wise feedback
   - Missing skills
   - Improved bullet points
4. The response is parsed, validated, and rendered in the UI
5. Results are stored locally for history tracking

---

## Tech Stack

* Python
* Streamlit
* Google Gemini API (LLM)
* Prompt Engineering
* PyMuPDF / pdfplumber
* Pandas
---

## Automation Ideas

* Auto-email resume feedback
* Track improvement over time
* Job match alerts

---

## Troubleshooting

| Issue            | Fix                    |
| ---------------- | ---------------------- |
| API key error    | Check key validity     |
| PDF not reading  | Try pasting text       |
| Module not found | Reinstall requirements |
| App not opening  | Try different port     |

---

## Author

**Utsav Kumar**

---

## If you like this project

Give it a ⭐ on GitHub!
