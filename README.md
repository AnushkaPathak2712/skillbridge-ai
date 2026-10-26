# MCA Skill Gap → AI Learning Roadmap Generator

A Flask web app that takes a student's self-rated skill profile, computes their personalised gap against the MCA Mumbai University industry benchmark dataset, and generates a 4-week AI-powered learning roadmap using the Claude API.

## Project Structure

```
roadmap_app/
├── app.py              ← Flask backend + prompt engineering logic
├── requirements.txt
├── templates/
│   └── index.html      ← Frontend (skill form + gap bars + roadmap display)
└── README.md
```

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Get your Anthropic API key
Sign up at https://console.anthropic.com and create an API key.

### 3. Set the API key as an environment variable
```bash
# Mac / Linux
export ANTHROPIC_API_KEY="sk-ant-..."

# Windows (PowerShell)
$env:ANTHROPIC_API_KEY = "sk-ant-..."
```

> Note: The app reads this key automatically. Never hardcode it in your source files.

### 4. Run the app
```bash
python app.py
```

Then open http://localhost:5000 in your browser.

---

## How the Prompt Engineering Works

The key insight is **injecting your real research data into the LLM prompt** so the AI gives specific, grounded advice rather than generic tips.

The prompt is structured in 4 layers:

### Layer 1 — Research Context
Your paper's findings (153 respondents, key gap numbers) are stated upfront so the model understands the academic framework it's operating in.

### Layer 2 — Industry Benchmarks
The exact industry expectation scores from your `industry_cleaned.xlsx` are embedded — the model knows what 3.30/4 for Programming means in your specific context.

### Layer 3 — Student's Personal Gap Profile
Per-skill gap, tier classification (Critical/High/Moderate/Low), and cohort comparison are all computed server-side and injected as a structured data block.

### Layer 4 — Structured Output Format
The prompt specifies exact section headers, so the response can be parsed and rendered as clean Markdown without any post-processing.

---

## Customisation

- **Add more skills**: edit `INDUSTRY_BENCHMARKS` and `COHORT_AVG` in `app.py`
- **Change the roadmap format**: edit the `=== YOUR TASK ===` section in `build_prompt()`
- **Add a PDF export**: use `weasyprint` or `pdfkit` on the rendered HTML
- **Add a database**: store responses with `sqlite3` to build an analytics dashboard over time

---

## Research Paper Reference

Pathak, A., Naik, N., Panda, P., Patel, K., & Gupta, S. (2025).
*Skill Gap Analysis between MCA Curriculum and Industry Requirements: A Study of Mumbai University Students.*
SIES College of Management Studies, Mumbai.
