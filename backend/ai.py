import os
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()


def is_gemini_configured():
    key = os.getenv("GEMINI_API_KEY")
    return bool(key and key.strip() and key.strip() != "your_gemini_api_key")


def generate(prompt):
    key = os.getenv("GEMINI_API_KEY")
    if not is_gemini_configured():
        # Graceful fallback mock response generator when API key is not configured
        return _mock_ai_response(prompt)

    try:
        genai.configure(api_key=key.strip())
        model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        return response.text
    except Exception as exc:
        # If API key has quota exceeded or temporary network error, return helpful fallback with error note
        fallback = _mock_ai_response(prompt)
        return f"> ⚠️ **Notice**: Gemini API encountered an issue ({exc}). Showing institutional fallback model.\n\n{fallback}"


def generate_study_plan(subjects, hours, exam_context="None supplied"):
    prompt = f"""You are Ruia AI, an elite academic mentor at Ramnarain Ruia Autonomous College, Mumbai.
Generate an empowering, personalized 7-day weekly study timetable in Markdown for an ambitious undergraduate student.

STUDENT PROFILE:
- Subjects & Self-Assessed Difficulty:
{subjects}
- Dedicated Focused Study Hours Per Day: {hours} hours
- Upcoming Exam Horizons: {exam_context or 'None specified'}

TIMETABLE REQUIREMENTS:
1. Academic Rhythm: Prioritize highest-difficulty subjects during high-energy morning/afternoon study blocks.
2. Structure: Present a clean, organized Day-by-Day (Monday to Sunday) schedule table with Morning, Afternoon, and Evening slots.
3. Techniques: Incorporate Spaced Repetition, Feynman technique, and Active Recall checkpoints.
4. Wellness: Include Pomodoro intervals (50m study / 10m break) and adequate rest.
5. Provide 3 high-impact Ruia Collegiate Study Habits tailored to their subjects."""
    return generate(prompt)


def generate_assignment_reminders(title, due_date):
    prompt = f"""You are Ruia AI, the academic deadline companion at Ramnarain Ruia Autonomous College.
Generate a structured, strategic reminder milestone schedule for a major collegiate assignment:

ASSIGNMENT DETAILS:
- Title: {title}
- Official Submission Deadline: {due_date}

MILESTONES TO GENERATE:
Create a 4-stage deadline preparation roadmap in clean Markdown with calendar dates and bullet points:
1. 📚 Stage 1: Topic Breakdown & Primary Research (Initial checkpoint)
2. ✍️ Stage 2: Structural Outline & First Working Draft
3. 🔍 Stage 3: Peer Review, Citation Formatting & Ruia Faculty Rubric Audit
4. 🎯 Stage 4: Final Submission Day Protocol

Add a 1-sentence encouraging Ruia College academic motto at the bottom."""
    return generate(prompt)


def generate_resume_review(resume_text, target_role="Internship / Academic Placement"):
    prompt = f"""You are the Director of Career Advisory and Placement Cell at Ramnarain Ruia Autonomous College.
Review this undergraduate student's resume with high editorial standards for clarity, impact, typography, and ATS compatibility.

TARGET ROLE / DOMAIN: {target_role}

STUDENT RESUME:
{resume_text}

RESPONSE STRUCTURE (Markdown):
1. **Ruia Placement Readiness Score**: Give an objective rating out of 100 with a 1-sentence executive summary.
2. **🌟 Key Core Strengths**: 3 distinct bullet points detailing what is already impressive.
3. **⚡ High-Priority Improvements**: 3 actionable fixes (e.g. quantifiable action verbs, metric outcomes, STAR methodology).
4. **✨ Polished, ATS-Optimized Version**: A fully revised, publication-grade version of their resume preserving all factual truths while vastly elevating grammar and impact."""
    return generate(prompt)


def generate_quiz(subject, topic, format_type="multiple-choice questions", count=10):
    prompt = f"""You are a distinguished professor at Ramnarain Ruia Autonomous College, Mumbai.
Create an academic practice set of {count} {format_type} for an undergraduate student.

SUBJECT: {subject}
TOPIC: {topic}

REQUIREMENTS:
- Academic rigor suitable for Mumbai University / Autonomous College syllabus.
- If Multiple-Choice: Provide 4 options (A, B, C, D) for each question.
- Always include an expandable or clearly demarcated **Answer & Detailed Explanation** for each question.
- Include conceptual rationale connecting to real-world applications or syllabus foundations."""
    return generate(prompt)


def generate_revision_schedule(exams_list):
    prompt = f"""You are Ruia AI, the chief examination strategist at Ramnarain Ruia Autonomous College.
Design an intensive yet balanced Spaced Repetition Revision Timetable based on the student's upcoming examination calendar:

UPCOMING EXAMS:
{exams_list}

REQUIREMENTS:
1. Reverse-engineered timetable prioritizing the closest exams while preventing neglect of later papers.
2. Day-by-day table highlighting subject focus, past paper solving, and formula/concept review.
3. Specific stress-management and cognitive recovery protocols for exam days. Format in pristine Markdown."""
    return generate(prompt)


def _mock_ai_response(prompt):
    prompt_lower = prompt.lower()
    prefix = "> ✦ **Ruia AI Academic Companion** *(Local Intelligent Mode — Add your `GEMINI_API_KEY` in `.env` for custom live generation)*\n\n"

    if "study plan" in prompt_lower or "timetable" in prompt_lower:
        return prefix + """### 🏛️ Official Ruia College 7-Day Academic Plan

| Day | Focus Block 1 (Morning · High Energy) | Focus Block 2 (Afternoon · Application) | Focus Block 3 (Evening · Review) |
| :--- | :--- | :--- | :--- |
| **Monday** | Core Theory Deep-Dive (Active Recall) | Problem Solving & Code Exercises | Flashcard Review & Tomorrow Prep |
| **Tuesday** | Difficult Subject Concepts (Feynman Technique) | Lab Journal / Assignment Draft | Spaced Repetition Quiz |
| **Wednesday** | Core Syllabus Module 2 | Numerical Problems & Case Studies | Summary Notes Consolidation |
| **Thursday** | Past Paper Analysis & Question Practice | Secondary Subject Reading | Quick Recall Self-Test |
| **Friday** | Integrated Topic Synthesis | Practical Project Work | Weekly Doubts Resolution |
| **Saturday** | Full Mock Test Simulation | Error Analysis & Weak Area Fixes | Light Reading & Concept Maps |
| **Sunday** | Active Rest & Weekly Restructure | 1-Hour Overview of Upcoming Week | Mental Recharge & Leisure |

#### 🎓 Three Golden Ruia Study Principles:
1. **The 50/10 Focus Protocol**: Study with complete phone isolation for 50 minutes, followed by a mandatory 10-minute non-screen recovery.
2. **Active Retrieval Over Passive Reading**: Close the book and write the core concepts from memory before verifying accuracy.
3. **Sleep Consolidation**: Target 7–8 hours of consistent sleep—memory consolidation occurs during rapid eye movement cycles."""

    elif "reminder" in prompt_lower or "deadline" in prompt_lower:
        return prefix + """### ⏳ Ruia AI Milestone Reminder Schedule

- **📍 Milestone 1 (T - 7 Days): Research & Outline Validation**
  * Finalize scope, gather certified academic sources from the Ruia library / digital portal, and draft the thesis framework.
- **📍 Milestone 2 (T - 4 Days): Full Working Draft**
  * Complete body paragraphs, implement technical arguments, and integrate citations.
- **📍 Milestone 3 (T - 2 Days): Rubric Audit & Polish**
  * Check against professor guidelines, run spell/syntax verification, and verify bibliography.
- **📍 Milestone 4 (T - 12 Hours): Final Submission Readiness**
  * Convert to PDF, verify formatting integrity, and submit cleanly before the cutoff hour.

*“Success is the sum of small efforts, repeated day in and day out.” — Ruia AI Companion*"""

    elif "resume" in prompt_lower:
        return prefix + """### 📑 Ruia Placement Cell — Resume Diagnostic

**Overall Placement Readiness Score**: `88 / 100`  
*Solid technical foundation with strong academic pedigree; high potential with enhanced action verb quantification.*

---

#### 🌟 Key Strengths:
- **Clear Academic Progression**: Degree credentials and coursework at Ruia College are clearly highlighted.
- **Relevant Technical Arsenal**: Strong alignment with current industry tooling and coursework standards.
- **Clean Structure**: Consistent reverse-chronological flow and logical sectioning.

#### ⚡ Priority Refinements:
1. **Quantify Achievements (STAR Methodology)**: Convert passive tasks (e.g., "worked on project") into measured outcomes (e.g., "Architected a full-stack system reducing response latency by 35%").
2. **Action Verb Optimization**: Replace repetitive descriptions with dynamic keywords like *Engineered, Spearheaded, Orchestrated, Synthesized*.
3. **Targeted Technical Profiling**: Group skills into distinct categories (Languages, Frameworks, Developer Tools, Core Competencies).

---

### ✨ Polished, ATS-Optimized Resume

```markdown
# [STUDENT NAME]
Matunga East, Mumbai · student@ruiacollege.edu · linkedin.com/in/student · github.com/student

## EDUCATION
Ramnarain Ruia Autonomous College, Mumbai
Bachelor of Science / Arts · CGPA: 8.9 / 10.0
Relevant Coursework: Advanced Data Structures, Artificial Intelligence, Database Engineering

## KEY TECHNICAL COMPETENCIES
- Programming: Python, SQL, C++, Modern JavaScript
- Tools & Libraries: Streamlit, Git, MySQL, Pandas, Docker
- Core Skills: Algorithmic Problem Solving, Agile Collaboration, Data Analysis

## ACADEMIC & TECHNICAL PROJECTS
Ruia AI Student Companion | Lead Developer
- Engineered a full-stack academic companion using Streamlit, MySQL, and Generative AI.
- Implemented parameterized relational schemas supporting multi-user assignment and exam tracking.
- Designed an editorial collegiate interface adhering to Ruia College branding standards.

## LEADERSHIP & EXTRA-CURRICULAR
Active Member, Ruia College Technical Association (RCTA)
- Organized annual inter-collegiate hackathons engaging 300+ student participants.
```"""

    elif "quiz" in prompt_lower:
        return prefix + """### 🎯 Ruia College Academic Practice Set

**Subject**: Practice Assessment · **Mode**: Interactive Mastery

#### Question 1
**What is the primary advantage of utilizing Spaced Repetition in long-term academic retention?**
- A) It eliminates the need for conceptual understanding
- B) It exploits the psychological spacing effect to flatten the forgetting curve
- C) It guarantees 100% test accuracy without revision
- D) It reduces the total amount of study time to zero

<details>
<summary><b>🔍 Reveal Answer & Rationale</b></summary>
<b>Correct Answer: B</b><br>
<i>Rationale: Hermann Ebbinghaus's forgetting curve demonstrates that memory decay is exponential. Spaced repetition interrupts this decay at precisely timed intervals, strengthening neural pathways and consolidating information into long-term storage.</i>
</details>

---

#### Question 2
**In relational database architectures (such as MySQL), what is the role of an Index on a foreign key column?**
- A) To encrypt data stored on disk
- B) To dramatically speed up JOIN operations and prevent table-scan bottlenecks
- C) To automatically delete unreferenced rows
- D) To allow null values in primary keys

<details>
<summary><b>🔍 Reveal Answer & Rationale</b></summary>
<b>Correct Answer: B</b><br>
<i>Rationale: B-tree indexes enable logarithmic time-complexity search (O(log n)) rather than linear table scans (O(n)), which is critical when joining relational tables such as students, assignments, and exams.</i>
</details>

---

#### Question 3
**When applying the Feynman Technique to study complex university coursework, what is the ultimate test of understanding?**
- A) Memorizing the professor's lecture verbatim
- B) Explaining the concept in simple, jargon-free language to a novice
- C) Highlighting 90% of the textbook page
- D) Re-reading the lecture slides five consecutive times

<details>
<summary><b>🔍 Reveal Answer & Rationale</b></summary>
<b>Correct Answer: B</b><br>
<i>Rationale: Richard Feynman emphasized that complexity often masks gaps in understanding. If you cannot explain a concept using simple analogies, you have identified your exact knowledge deficit.</i>
</details>"""

    elif "revision" in prompt_lower or "exam" in prompt_lower:
        return prefix + """### 📅 Ruia Autonomous Examination Revision Master Schedule

| Date / Phase | Strategic Focus | Method & Target | Recovery Protocol |
| :--- | :--- | :--- | :--- |
| **T - 10 to 7 Days** | Core Concepts Consolidation | High-yield syllabus units & formula derivations | 15-min mindfulness walk |
| **T - 6 to 4 Days** | Past 5-Year Question Papers | Timed paper solving with answer key review | Hydration & screen detox |
| **T - 3 to 2 Days** | Weak Areas Targeted Drill | Flashcard recall & professor doubt sessions | Light stretching & healthy diet |
| **T - 1 Day** | High-Level Synopsis & Rest | Concept map review (No late-night cramming) | 8-hour sleep requirement |
| **Exam Morning** | Calm Warm-up | 20-min formula sheet scan & mental readiness | Deep breathing & early arrival |

*“Confidence comes from discipline and training.” — Ramnarain Ruia Autonomous College*"""

    return prefix + "Ruia AI Companion is ready to assist your academic journey."
