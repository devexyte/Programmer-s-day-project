import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()


def get_active_api_key():
    try:
        import streamlit as st
        k = st.session_state.get("custom_gemini_api_key")
        if k and k.strip():
            return k.strip()
    except Exception:
        pass
    key = os.getenv("GEMINI_API_KEY")
    if key and key.strip() and key.strip() != "AQ.Ab8RN6LtGNoYrzkwT0lBLyNcaFgc4QZcG7Srb-nORTSNWVI1jw":
        return key.strip()
    return None


def is_gemini_configured():
    return bool(get_active_api_key())


def find_working_model(key):
    key_clean = key.strip()
    genai.configure(api_key=key_clean)
    
    # 1. Dynamically query available models from list_models()
    try:
        available = []
        for m in genai.list_models():
            methods = getattr(m, "supported_generation_methods", [])
            if "generateContent" in methods:
                name = m.name.replace("models/", "")
                available.append(name)
        
        if available:
            # Prefer fast flash models (gemini-3.6-flash is recommended for new users)
            priority = [
                "gemini-3.6-flash",
                "gemini-3.5-flash",
                "gemini-flash-latest",
                "gemini-2.5-flash",
                "gemini-2.0-flash",
                "gemini-1.5-flash-latest",
                "gemini-1.5-flash",
                "gemini-1.5-pro",
                "gemini-pro"
            ]
            for p in priority:
                if p in available:
                    return p, available
            return available[0], available
    except Exception:
        pass

    # 2. Fallback candidate probing
    candidates = [
        "gemini-3.6-flash",
        "gemini-3.5-flash",
        "gemini-flash-latest",
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash-latest",
        "gemini-1.5-flash"
    ]
    for c in candidates:
        try:
            m = genai.GenerativeModel(c)
            r = m.generate_content("Ping")
            if r and r.text:
                return c, [c]
        except Exception:
            continue

    return "gemini-2.5-flash", []


def save_api_key_to_env(key, model_name="gemini-2.5-flash"):
    key_clean = key.strip()
    env_path = Path(".env")
    if not env_path.exists():
        env_path = Path(__file__).resolve().parent.parent / ".env"

    lines = []
    if env_path.exists():
        lines = env_path.read_text(encoding="utf-8").splitlines()

    new_lines = []
    replaced_key = False
    replaced_model = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("GEMINI_API_KEY=") or stripped.startswith("#GEMINI_API_KEY="):
            new_lines.append(f"GEMINI_API_KEY={key_clean}")
            replaced_key = True
        elif stripped.startswith("GEMINI_MODEL=") or stripped.startswith("#GEMINI_MODEL="):
            new_lines.append(f"GEMINI_MODEL={model_name}")
            replaced_model = True
        else:
            new_lines.append(line)

    if not replaced_key:
        new_lines.append(f"GEMINI_API_KEY={key_clean}")
    if not replaced_model:
        new_lines.append(f"GEMINI_MODEL={model_name}")

    env_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    os.environ["GEMINI_API_KEY"] = key_clean
    os.environ["GEMINI_MODEL"] = model_name


def test_gemini_connection(key):
    try:
        best_model, all_models = find_working_model(key)
        
        # Test content generation with discovered model
        model = genai.GenerativeModel(best_model)
        resp = model.generate_content("Respond with: Ruia AI Connected.")
        
        return True, best_model, resp.text.strip()
    except Exception as e:
        err_str = str(e)
        if "API_KEY_INVALID" in err_str or "API key not valid" in err_str:
            friendly = "Invalid API Key. Please verify the key copied from Google AI Studio."
        elif "PERMISSION_DENIED" in err_str or "Generative Language API" in err_str:
            friendly = "Generative Language API is not enabled for this key. Get a key directly from https://aistudio.google.com/app/apikey"
        elif "404" in err_str:
            friendly = "Model not found on this API endpoint. Ensure your key is generated from Google AI Studio (https://aistudio.google.com/app/apikey)."
        else:
            friendly = err_str
        return False, None, friendly


def generate(prompt):
    active_key = get_active_api_key()
    if not active_key:
        return _mock_ai_response(prompt)

    try:
        genai.configure(api_key=active_key)
        configured_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        
        # Priority list of model candidates for resilient fallback
        candidates = [
            configured_model,
            "gemini-2.5-flash",
            "gemini-2.0-flash",
            "gemini-1.5-flash-latest",
            "gemini-1.5-flash",
            "gemini-1.5-pro",
            "gemini-pro"
        ]
        
        # Deduplicate while preserving order
        seen = set()
        unique_candidates = [c for c in candidates if not (c in seen or seen.add(c))]

        last_exc = None
        for cand in unique_candidates:
            try:
                model = genai.GenerativeModel(cand)
                response = model.generate_content(prompt)
                if response and response.text:
                    return response.text
            except Exception as e:
                last_exc = e
                continue
                
        if last_exc:
            raise last_exc
        return _mock_ai_response(prompt)
    except Exception as exc:
        fallback = _mock_ai_response(prompt)
        return f"> ⚠️ **Notice**: Live Gemini call encountered an issue ({exc}). Displaying Ruia College curriculum model.\n\n{fallback}"


def generate_study_plan(subjects, hours, exam_context="None supplied"):
    prompt = f"""You are Ruia AI, the chief academic mentor at Ramnarain Ruia Autonomous College, Mumbai (https://www.ruiacollege.edu).
Generate an empowering, personalized 7-day weekly study timetable in Markdown for an ambitious undergraduate student.

STUDENT PROFILE & AUTONOMOUS COURSEWORK:
- Course Modules & Autonomous Units (DSC/DSE/SEC/AEC):
{subjects}
- Dedicated Focused Study Hours Per Day: {hours} hours
- Assessment Pacing & Exam Context: {exam_context or 'Balanced CIA (40 marks) + SEE (60 marks)'}

ACADEMIC REQUIREMENTS (Matching Ruia College Autonomous Standard):
1. Curriculum Rhythm: Prioritize Discipline Specific Core (DSC) theory & 3-hour practical lab preparation during peak morning energy blocks.
2. Structure: Present a clean, organized Day-by-Day (Monday to Sunday) schedule table with Morning (Theory & Active Recall), Afternoon (Lab Projects & Numerical Problem Solving), and Evening (Spaced Repetition & Revision) slots.
3. Continuous Internal Assessment (CIA): Include dedicated checkpoints for Ruia College class tests, seminar presentations, and assignment drafts.
4. Techniques: Incorporate Spaced Repetition, Feynman technique, and active recall.
5. Provide 3 high-impact Ruia Collegiate Study Habits tailored to autonomous degree scholars."""
    return generate(prompt)


def generate_assignment_reminders(title, due_date):
    prompt = f"""You are Ruia AI, the academic deadline companion at Ramnarain Ruia Autonomous College (https://www.ruiacollege.edu).
Generate a structured, strategic reminder milestone schedule for a collegiate assignment:

ASSIGNMENT DETAILS:
- Title: {title}
- Official Submission Deadline: {due_date}

MILESTONES TO GENERATE:
Create a 4-stage deadline preparation roadmap in clean Markdown with calendar dates and bullet points:
1. 📚 Stage 1: Topic Breakdown & Primary Research (Consulting Ruia Library / Digital Portals)
2. ✍️ Stage 2: Structural Outline & First Working Draft
3. 🔍 Stage 3: Peer Review, Citation Formatting & Ruia Faculty Rubric Audit
4. 🎯 Stage 4: Final Submission Protocol (PDF conversion & submission verification)

Add a 1-sentence encouraging Ruia College academic motto at the bottom."""
    return generate(prompt)


def generate_resume_review(resume_text, target_role="Internship / Academic Placement"):
    prompt = f"""You are the Director of Career Advisory and Placement Cell at Ramnarain Ruia Autonomous College (https://www.ruiacollege.edu).
Review this undergraduate student's resume with high editorial standards for clarity, impact, typography, and ATS compatibility.

TARGET ROLE / DOMAIN: {target_role}

STUDENT RESUME:
{resume_text}

RESPONSE STRUCTURE (Markdown):
1. **Ruia Placement Readiness Score**: Give an objective rating out of 100 with an executive summary.
2. **🌟 Key Core Strengths**: 3 distinct bullet points detailing collegiate achievements.
3. **⚡ High-Priority Improvements**: 3 actionable fixes using STAR methodology and quantifiable metrics.
4. **✨ Polished, ATS-Optimized Version**: A publication-grade version of their resume preserving all factual truths while elevating grammar, typography, and impact."""
    return generate(prompt)


def generate_quiz(subject, topic, format_type="multiple-choice questions", count=10):
    prompt = f"""You are a professor at Ramnarain Ruia Autonomous College, Mumbai (https://www.ruiacollege.edu).
Create an academic practice set of {count} {format_type} for an undergraduate student.

SUBJECT: {subject}
TOPIC: {topic}

REQUIREMENTS:
- Academic rigor suitable for Mumbai University / Ruia Autonomous College syllabus.
- If Multiple-Choice: Provide 4 options (A, B, C, D) for each question.
- Always include an expandable or clearly demarcated **Answer & Detailed Explanation** for each question.
- Include conceptual rationale connecting to syllabus foundations and continuous assessment."""
    return generate(prompt)


def generate_revision_schedule(exams_list):
    prompt = f"""You are Ruia AI, the chief examination strategist at Ramnarain Ruia Autonomous College (https://www.ruiacollege.edu).
Design an intensive yet balanced Spaced Repetition Revision Timetable based on the student's upcoming examination calendar:

UPCOMING EXAMS:
{exams_list}

REQUIREMENTS:
1. Reverse-engineered timetable prioritizing the closest papers while safeguarding cumulative retention.
2. Day-by-day table highlighting subject focus, past 5-year paper solving, and formula/concept review.
3. Specific stress-management and cognitive recovery protocols for exam days. Format in pristine Markdown."""
    return generate(prompt)


def _mock_ai_response(prompt):
    prompt_lower = prompt.lower()
    prefix = "> ✦ **Ruia AI Academic Companion** *(Official Autonomous Curriculum Model · Add `GEMINI_API_KEY` in `.env` or in Sidebar Settings for custom live generation)*\n\n"

    if "study plan" in prompt_lower or "timetable" in prompt_lower:
        return prefix + """### 🏛️ Ramnarain Ruia Autonomous College · 7-Day Academic Timetable
*Aligned with NEP 2020 Autonomous Curriculum (DSC · DSE · SEC · AEC) & CIA/SEE Pacing*

| Day | Focus Block 1 (Morning · High Energy Theory) | Focus Block 2 (Afternoon · Practical/Lab) | Focus Block 3 (Evening · Active Recall) |
| :--- | :--- | :--- | :--- |
| **Monday** | **DSC 1 Core Theory**: Conceptual breakdown & Active Recall notes | **Laboratory Practical**: Journal compilation & Experiment analysis | **Spaced Retrieval**: 20-min flashcards & formula derivations |
| **Tuesday** | **DSC 2 Core Theory**: Advanced problem-solving & Feynman method | **CIA Internal Prep**: Mini-project draft or research paper review | **Error Log Review**: Re-solve past test mistakes |
| **Wednesday** | **DSE Department Elective**: In-depth chapter reading & diagrams | **Numerical & Code Practice**: Problem sets / Lab simulation | **Weekly Doubts Synthesis**: Collate questions for faculty |
| **Thursday** | **SEC Skill Course**: Hands-on tooling, code, or laboratory skills | **AEC Communication**: Technical report writing & presentation prep | **Peer Recall**: Concept explanation drill |
| **Friday** | **Integrated Revision**: Cross-topic connections & past paper analysis | **CIA Submission Audit**: Assignment citations & rubric checks | **Summary Notes Consolidation**: Create 1-page cheat sheets |
| **Saturday** | **Full 2-Hour Mock Test**: Timed exam conditions simulation | **Detailed Test Review**: Score grading and gap identification | **Light Leisure & Reading**: Cultural or departmental society work |
| **Sunday** | **Rest & Cognitive Recovery**: Non-screen mental rejuvenation | **Ruia Library Prep**: 1-hour planning of upcoming week's milestones | **Sleep Hygiene & Early Rest**: Memory consolidation protocol |

#### 🎓 Three Golden Ruia Autonomous Study Principles:
1. **The 50/10 Focus Protocol**: Study with complete phone isolation for 50 minutes, followed by a mandatory 10-minute non-screen recovery.
2. **Active Retrieval Over Passive Reading**: Close the textbook and write the core mechanisms from memory before verifying accuracy.
3. **Continuous Assessment Alignment**: Dedicate 45 minutes daily to internal tests (CIA) to secure the 40-mark internal component."""

    elif "reminder" in prompt_lower or "deadline" in prompt_lower:
        return prefix + """### ⏳ Ruia AI Milestone Reminder Schedule
*Continuous Internal Assessment (CIA) Preparation Roadmap*

- **📍 Milestone 1 (T - 7 Days): Research & Outline Validation**
  * Finalize scope, gather certified academic sources from the Ruia library / digital portal, and draft the thesis framework.
- **📍 Milestone 2 (T - 4 Days): Full Working Draft**
  * Complete body paragraphs, implement technical arguments, and integrate citations according to Ruia faculty rubrics.
- **📍 Milestone 3 (T - 2 Days): Rubric Audit & Peer Review**
  * Check against professor guidelines, run spell/syntax verification, and verify bibliography.
- **📍 Milestone 4 (T - 12 Hours): Final Submission Readiness**
  * Convert to PDF, verify formatting integrity, and submit cleanly to the department portal before the cutoff hour.

*“Success is the sum of small efforts, repeated day in and day out.” — Ramnarain Ruia Autonomous College*"""

    elif "resume" in prompt_lower:
        return prefix + """### 📑 Ruia Placement Cell — Resume Diagnostic

**Overall Placement Readiness Score**: `91 / 100`  
*Outstanding autonomous academic credentials with strong project leadership; high potential for top-tier corporate placement.*

---

#### 🌟 Key Strengths:
- **Autonomous Rigor**: Degree coursework at Ramnarain Ruia Autonomous College is prominently showcased.
- **Relevant Technical Arsenal**: Strong alignment with modern industry tooling and NEP 2020 curriculum standards.
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
Bachelor of Science / Arts (Autonomous · NEP 2020) · CGPA: 9.1 / 10.0
Relevant Coursework: Advanced Algorithms, Artificial Intelligence, Database Engineering

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
Active Core Member, Ruia College Technical Association (RCTA)
- Organized annual inter-collegiate technical symposia engaging 300+ student participants.
```"""

    elif "quiz" in prompt_lower:
        return prefix + """### 🎯 Ruia College Academic Practice Set
*Active Recall & Autonomous Syllabus Mastery*

#### Question 1
**What is the primary advantage of utilizing Spaced Repetition in long-term academic retention?**
- A) It eliminates the need for conceptual understanding
- B) It exploits the psychological spacing effect to flatten the forgetting curve
- C) It guarantees 100% test accuracy without revision
- D) It reduces the total amount of study time to zero

<details>
<summary><b>🔍 Reveal Answer & Detailed Rationale</b></summary>
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
<summary><b>🔍 Reveal Answer & Detailed Rationale</b></summary>
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
<summary><b>🔍 Reveal Answer & Detailed Rationale</b></summary>
<b>Correct Answer: B</b><br>
<i>Rationale: Richard Feynman emphasized that complexity often masks gaps in understanding. If you cannot explain a concept using simple analogies, you have identified your exact knowledge deficit.</i>
</details>"""

    elif "revision" in prompt_lower or "exam" in prompt_lower:
        return prefix + """### 📅 Ruia Autonomous Examination Revision Master Schedule
*Semester End Examination (SEE) Reverse-Engineered Strategy*

| Date / Phase | Strategic Focus | Method & Target | Recovery Protocol |
| :--- | :--- | :--- | :--- |
| **T - 10 to 7 Days** | Core Concepts Consolidation | High-yield syllabus units & formula derivations | 15-min campus walk |
| **T - 6 to 4 Days** | Past 5-Year Question Papers | Timed paper solving with answer key review | Hydration & screen detox |
| **T - 3 to 2 Days** | Weak Areas Targeted Drill | Flashcard recall & professor doubt sessions | Light stretching & healthy diet |
| **T - 1 Day** | High-Level Synopsis & Rest | Concept map review (No late-night cramming) | 8-hour sleep requirement |
| **Exam Morning** | Calm Warm-up | 20-min formula sheet scan & mental readiness | Deep breathing & early arrival |

*“Confidence comes from discipline and training.” — Ramnarain Ruia Autonomous College*"""

    return prefix + "Ruia AI Companion is ready to assist your academic journey."
