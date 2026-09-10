# 🏛️ Ruia AI Student Companion
### *The Digital Extension of Ramnarain Ruia Autonomous College, Mumbai*

[![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-FF4B4B.svg?style=flat&logo=streamlit)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB.svg?style=flat&logo=python)](https://python.org)
[![MySQL](https://img.shields.io/badge/MySQL-8.0+-4479A1.svg?style=flat&logo=mysql)](https://mysql.com)
[![Gemini AI](https://img.shields.io/badge/Google%20Gemini-1.5%20Flash-8E75B2.svg?style=flat&logo=google)](https://ai.google.dev)
[![Institution](https://img.shields.io/badge/Institution-Ramnarain%20Ruia%20Autonomous%20College-800000.svg)](https://www.ruiacollege.edu)

---

## 🌟 Project Overview & Vision

**Ruia AI Student Companion** is a human-crafted, production-ready digital academic companion built specifically for the undergraduate and postgraduate scholars of **Ramnarain Ruia Autonomous College, Matunga East, Mumbai** (Affiliated with the University of Mumbai, NAAC 'A+' Grade, CGPA 3.70, Star College Status, Estd. 1937).

Rather than being a generic AI wrapper, this application functions as an authentic **institutional digital extension** of Ruia College. It unifies collegiate study planning, multi-stage assignment milestones, placement cell resume critique, interactive syllabus mastery quizzes, and exam countdowns with spaced-repetition revision schedules.

---

## 🎨 Design Language & Aesthetic Standard

Adhering strictly to the **Ruia College Official Identity**, the visual design system combines:
- **Imperial Maroon** (`#6B0F1A`, `#800000`): Signifying collegiate prestige and 87+ years of academic heritage.
- **Royal Champagne Gold** (`#C9A86A`, `#E5C383`): Accent trims, active highlight states, and golden borders.
- **Warm Editorial Ivory & Cream** (`#FAF8F5`, `#FFFFFF`): Clean reading surfaces with gentle depth and glassmorphism.
- **Typography**: Headings in regal **Playfair Display** paired with clean, accessible modern sans-serif (**Plus Jakarta Sans** / **DM Sans**).
- **Official Institutional Asset**: High-resolution embedded logo of Ramnarain Ruia Autonomous College.

---

## 🚀 Core Features (All 5 Mandatory Pillars)

### 1. 📅 Personalized AI Study Planner
- Custom syllabus inputs with course-specific difficulty ratings (High / Medium / Low).
- Focused daily study hours configuration with Pomodoro study-rest pacing.
- Generates a structured **7-Day Day-by-Day Timetable** with morning high-energy, afternoon application, and evening review blocks.
- Incorporates Spaced Repetition, Active Recall, and the Feynman Technique.
- Persisted to MySQL `study_plans` table with downloadable Markdown report.

### 2. ⏳ Assignment Desk & Milestone Reminders
- Course linkage to Ruia Autonomous departmental papers (or custom coursework).
- Automated generation of a **4-stage deadline preparation roadmap**:
  - *Stage 1*: Topic Breakdown & Primary Research (T - 7 Days)
  - *Stage 2*: Structural Outline & First Working Draft (T - 4 Days)
  - *Stage 3*: Citation Verification & Faculty Rubric Audit (T - 2 Days)
  - *Stage 4*: Final Submission Day Protocol (T - 12 Hours)
- Interactive completion toggle to archive finished deliverables.
- Persisted to `assignments` and `reminders` tables.

### 3. 📑 Placement Cell Resume Lab
- Career advisory diagnostics across Software Engineering, Data Science, Quantitative Finance, Biotechnology, and Corporate Consulting.
- Evaluates grammar, structure, quantifiable metrics (STAR method), and ATS keyword compatibility.
- Instant 1-click **Ruia Student Sample Resume** template loader for immediate benchmarking.
- Provides Placement Readiness Score (out of 100), core strengths, priority improvements, and an ATS-formatted Markdown output with instant download.

### 4. 🎯 Quiz Studio & Active Recall Vault
- Generates rigorous practice problems from Ruia syllabus lecture units.
- Supports Multiple-Choice Questions (with expandable answer & conceptual rationale), Short-Answer University Questions, and Study Flashcards.
- Interactive question-by-question answer reveals for in-app self-testing.
- Vault history tab archiving previously synthesized assessments in the `quizzes` table.

### 5. ⏱️ Exam Map & Revision Master Schedule
- Registers upcoming Autonomous examination papers with date, session/time, and campus venue.
- Real-time **countdown clocks** with visual urgency badges (`<3 days` critical red, `<7 days` amber, normal maroon).
- Reverse-engineers a comprehensive **Spaced-Repetition Revision Timetable** prioritizing nearest papers while safeguarding cumulative memory retention.
- Persisted to `exams` and `courses` tables.

---

## 🗄️ Database Architecture (`schema.sql`)

```sql
CREATE DATABASE IF NOT EXISTS ruia_companion;
USE ruia_companion;

CREATE TABLE students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    program VARCHAR(100) NOT NULL,
    year INT NOT NULL
);

CREATE TABLE courses (
    course_id INT AUTO_INCREMENT PRIMARY KEY,
    course_name VARCHAR(100) NOT NULL,
    course_code VARCHAR(50) NOT NULL UNIQUE,
    year INT NOT NULL
);

CREATE TABLE assignments (
    assignment_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NULL,
    title VARCHAR(200) NOT NULL,
    due_date DATE NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'Pending',
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE SET NULL
);

CREATE TABLE exams (
    exam_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NULL,
    exam_date DATE NOT NULL,
    exam_time VARCHAR(20),
    venue VARCHAR(100),
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE SET NULL
);

CREATE TABLE study_plans (
    plan_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    generated_plan TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
);

CREATE TABLE reminders (
    reminder_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    assignment_id INT NOT NULL,
    reminder_text TEXT NOT NULL,
    reminder_date DATE NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (assignment_id) REFERENCES assignments(assignment_id) ON DELETE CASCADE
);

CREATE TABLE quizzes (
    quiz_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    subject VARCHAR(100) NOT NULL,
    topic VARCHAR(100) NOT NULL,
    generated_quiz TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
);
```

---

## 📂 Project Structure

```
ruia_ai_companion/
│
├── app.py                     # Main application entry point, sidebar branding & routing
├── schema.sql                 # Complete MySQL relational database schema
├── requirements.txt           # Python dependencies (Streamlit, MySQL Connector, Gemini, Dotenv)
├── .env.example               # Template environment configuration
│
├── assets/
│   ├── logo.png               # Official Ramnarain Ruia Autonomous College logo
│   └── styles.css             # Imperial Maroon & Royal Gold collegiate CSS design system
│
├── backend/
│   ├── __init__.py            # Module exports
│   ├── db.py                  # Parameterized MySQL database connector & queries
│   ├── ai.py                  # Gemini AI integration boundary with prompt engineering & fallbacks
│   ├── planner_logic.py       # Study timetable generation & storage
│   ├── reminder_logic.py      # Staged assignment reminder workflows
│   ├── resume_logic.py        # Resume ATS evaluation & revision engine
│   ├── quiz_logic.py          # Interactive quiz curation & vault retrieval
│   └── exam_logic.py          # Exam countdowns & revision timetable builder
│
└── frontend/
    ├── __init__.py            # View exports
    ├── home.py                # Welcome hero, college credentials, & feature cards
    ├── dashboard.py           # Academic command center with metrics & assignment completion
    ├── planner.py             # 7-day study timetable builder & markdown exporter
    ├── assignments.py         # Coursework tracking & milestone reminders
    ├── resume.py              # Placement cell resume auditor & sample loader
    ├── quiz.py                # Active recall question studio & vault
    └── exams.py               # Examination map & spaced repetition scheduler
```

---

## ⚡ Quickstart & Local Setup

### 1. Prerequisites
- Python 3.10+ (tested on Python 3.14)
- MySQL 8.0+ (Local MySQL Server or Cloud instance such as Aiven / AWS RDS)

### 2. Configure Environment
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Ensure your database credentials and optional Gemini API Key are set in `.env`:
```env
MYSQL_HOST=mysql-abc218a-gauravsb77777-b366.i.aivencloud.com
MYSQL_PORT=13141
MYSQL_USER=avnadmin
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=ruia_companion
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-1.5-flash
```

### 3. Initialize MySQL Database
Run `schema.sql` on your MySQL instance:
```bash
mysql -h <host> -P <port> -u <user> -p < schema.sql
```

### 4. Install Dependencies
```bash
python -m venv .venv
# On Windows:
.venv\Scripts\pip install -r requirements.txt
# On Linux/macOS:
.venv/bin/pip install -r requirements.txt
```

### 5. Launch the Application
```bash
# On Windows:
.venv\Scripts\streamlit run app.py
# On Linux/macOS:
.venv/bin/streamlit run app.py
```
Open your browser at **`http://localhost:8501`**.

---

## 🌐 Cloud Deployment Guide

1. **Streamlit Community Cloud**:
   - Push repository to GitHub.
   - Link repository on [share.streamlit.io](https://share.streamlit.io).
   - Set app entrypoint to `app.py`.
   - Add `.env` variables under **App Settings > Secrets**.

2. **Render / Railway**:
   - Use Dockerfile or Python buildpack.
   - Start Command: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
   - Set environment variables in the project dashboard.

---

## 🏛️ Institutional Accreditation & Brand Notice
Designed with reverence for **Ramnarain Ruia Autonomous College**, Matunga, Mumbai.  
*“Explore • Experience • Excel”*
