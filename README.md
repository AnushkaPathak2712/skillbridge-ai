# SkillBridge AI 🎯

**Bridging the gap between MCA education and industry requirements with AI-powered personalized learning.**

SkillBridge AI is a full-stack web application that analyzes the skill gaps of Master of Computer Applications (MCA) students against industry benchmarks and generates personalized 4-week learning roadmaps using Generative AI.

This project is based on the peer-reviewed research paper: *"Skill Gap Analysis between MCA Curriculum and Industry Requirements: A Study of Mumbai University Students"* (153 participants: 87 students, 66 industry professionals).

## 🚀 Live Demo
[**Click here to view the live application**](https://skillbridge-ai-9rfx.onrender.com) *(Replace with your actual Render URL once deployed)*

### Demo Accounts:
*   **Student:** `student@skillbridge.com` / `student123`
*   **Faculty:** `faculty@skillbridge.com` / `faculty123`

---

## ✨ Key Features

*   **14-Skill Assessment:** Students rate their proficiency in 10 technical and 4 soft skills.
*   **Industry Gap Analysis:** Real-time visualization (using Chart.js) of the gap between student skills and actual industry expectations.
*   **AI-Powered Roadmaps:** Integrates Google Gemini API to generate a personalized, actionable 4-week learning plan with specific free resources and milestones.
*   **Dual Dashboards:**
    *   *Student:* Track progress, view AI roadmaps, compare past assessments, and earn XP/Badges.
    *   *Faculty:* Department-wide analytics, aggregate skill gap heatmaps, and student performance tracking.
*   **Gamification:** Earn XP, level up, and unlock badges for completing assessments and closing skill gaps.

---

## 🛠️ Tech Stack

*   **Backend:** Python, Flask, Flask-Login, Flask-Bcrypt
*   **Database:** PostgreSQL (Hosted on [Neon.tech](https://neon.tech))
*   **ORM:** SQLAlchemy (Flask-SQLAlchemy)
*   **AI/LLM:** Google Gemini API (`gemini-1.5-flash`)
*   **Frontend:** HTML, Tailwind CSS, Chart.js, FontAwesome
*   **Deployment:** Render (Web Service & Gunicorn)

---

## 💻 Local Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/your-username/skillbridge-ai.git
cd skillbridge-ai