import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.db import (
    connection, fetch_all, fetch_one, execute,
    get_all_students, get_student_by_id, get_or_create_student,
    get_all_courses, get_or_create_course,
    dashboard as get_dashboard_data,
    update_assignment_status as db_update_assignment_status,
    delete_assignment as db_delete_assignment,
    delete_exam as db_delete_exam,
    seed_default_data
)
from backend.ai import (
    get_active_api_key, is_gemini_configured, save_api_key_to_env,
    test_gemini_connection
)
from backend.planner_logic import create_plan, get_latest_plan
from backend.reminder_logic import create_reminders, get_all_student_reminders
from backend.resume_logic import review_resume
from backend.quiz_logic import create_quiz, get_student_quizzes
from backend.exam_logic import create_revision_schedule

# Initialize FastAPI application
app = FastAPI(
    title="RUI — Ruia Student Buddy API",
    description="Official REST API for Ramnarain Ruia Autonomous College Academic Companion",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent

# Ensure static & templates directories exist
(BASE_DIR / "static" / "css").mkdir(parents=True, exist_ok=True)
(BASE_DIR / "static" / "js").mkdir(parents=True, exist_ok=True)
(BASE_DIR / "templates").mkdir(parents=True, exist_ok=True)

# Mount static and assets directories
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
if (BASE_DIR / "assets").exists():
    app.mount("/assets", StaticFiles(directory=str(BASE_DIR / "assets")), name="assets")


# ==============================================================================
# PYDANTIC SCHEMAS (Flexible for frontend compatibility)
# ==============================================================================
class StudentCreate(BaseModel):
    name: str
    email: Optional[str] = ""
    program: Optional[str] = "Computer Science"
    department: Optional[str] = None
    year: Optional[Any] = 3

class PlanCreate(BaseModel):
    student_id: int
    subjects: Optional[str] = ""
    hours_per_day: Optional[float] = 3.5
    daily_hours: Optional[float] = None
    exam_date: Optional[str] = ""
    difficulty: Optional[str] = "Balanced"
    context: Optional[str] = ""
    focus_topics: Optional[str] = None

class AssignmentCreate(BaseModel):
    student_id: int
    title: str
    due_date: str
    course_name: Optional[str] = None
    course_id: Optional[int] = None
    priority: Optional[str] = "Normal"
    auto_remind: bool = True

class AssignmentStatusUpdate(BaseModel):
    status: str

class ResumeReviewRequest(BaseModel):
    student_id: Optional[int] = None
    resume_text: str
    target_role: Optional[str] = "General Placement"
    target_company: Optional[str] = ""

class QuizGenerateRequest(BaseModel):
    student_id: Optional[int] = 1
    subject: Optional[str] = "Computer Science"
    topic: str
    kind: Optional[str] = "multiple-choice questions with 4 options and detailed rationale"
    count: Optional[int] = 5
    question_count: Optional[int] = None
    difficulty: Optional[str] = "Intermediate"

class ExamCreate(BaseModel):
    student_id: int
    name: Optional[str] = None
    course_name: Optional[str] = None
    course_id: Optional[int] = None
    date: Optional[str] = None
    exam_date: Optional[str] = None
    exam_time: Optional[str] = "10:30 AM – 01:00 PM"
    venue: Optional[str] = "Main Academic Block"

class ExamRevisionRequest(BaseModel):
    student_id: int

class GeminiKeyConfig(BaseModel):
    api_key: Optional[str] = None
    key: Optional[str] = None


# ==============================================================================
# CORE HTML ROUTE
# ==============================================================================
@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_file = BASE_DIR / "templates" / "index.html"
    if not index_file.exists():
        return HTMLResponse("<h1>RUI Companion is initializing frontend...</h1>", status_code=200)
    return HTMLResponse(content=index_file.read_text(encoding="utf-8"))


# ==============================================================================
# ==============================================================================
# SYSTEM & STATUS APIS
# ==============================================================================
@app.get("/api/status")
async def get_system_status():
    api_key = get_active_api_key()
    active_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    
    # Pre-seed default data if not done
    try:
        seed_default_data()
        db_connected = True
    except Exception:
        db_connected = False

    is_configured = bool(api_key)
    return {
        "status": "online",
        "app_name": "RUI — The Ruia Student Buddy",
        "college": "Ramnarain Ruia Autonomous College",
        "campus": "Matunga East, Mumbai (Estd. 1937)",
        "accreditation": "NAAC 'A+' (CGPA 3.70 / 4.0)",
        "db_connected": db_connected,
        "database_name": "Ruia-Buddy (MySQL)",
        "ai_active": is_configured,
        "gemini_configured": is_configured,
        "ai_model": active_model if is_configured else "Curriculum Mode"
    }


@app.post("/api/config/gemini-key")
async def configure_gemini_key(config: GeminiKeyConfig):
    key = (config.api_key or config.key or "").strip()
    if not key:
        raise HTTPException(status_code=400, detail="API key cannot be empty")
    
    res = test_gemini_connection(key)
    if isinstance(res, tuple) and len(res) == 3:
        is_valid, model_name, msg = res
    elif isinstance(res, tuple) and len(res) == 2:
        is_valid, msg = res
        model_name = "gemini-2.5-flash"
    else:
        is_valid, model_name, msg = False, None, str(res)

    if not is_valid:
        raise HTTPException(status_code=400, detail=f"Verification failed: {msg}")

    chosen_model = model_name or "gemini-2.5-flash"
    save_api_key_to_env(key, chosen_model)
    return {
        "success": True,
        "message": f"Connected to Google Gemini ({chosen_model}) successfully!",
        "model": chosen_model
    }


# ==============================================================================
# SCHOLARS & PROFILES APIS
# ==============================================================================
@app.get("/api/students")
async def list_students():
    try:
        students = get_all_students()
        return {"success": True, "students": students or []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/students")
async def create_student(data: StudentCreate):
    try:
        program = data.department or data.program or "Computer Science"
        student = get_or_create_student(
            name=data.name.strip(),
            email=(data.email or "").strip(),
            program=program.strip(),
            year=int(data.year) if str(data.year).isdigit() else 1
        )
        return {"success": True, "student": student}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/students/{student_id}")
async def get_student(student_id: int):
    stu = get_student_by_id(student_id)
    if not stu:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"success": True, "student": stu}


@app.get("/api/courses")
async def list_courses():
    try:
        courses = get_all_courses()
        return {"success": True, "courses": courses or []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==============================================================================
# DASHBOARD API
# ==============================================================================
@app.get("/api/dashboard")
async def get_dashboard(student_id: int):
    try:
        assignments, exams, plan, reminders_count = get_dashboard_data(student_id)
        
        assign_list = assignments or []
        exam_list = exams or []
        
        total_assignments = len(assign_list)
        pending_assignments = sum(1 for a in assign_list if a.get("status") != "Completed")
        upcoming_exams_count = len(exam_list)
        
        return {
            "success": True,
            "assignments": assign_list,
            "upcoming_assignments": assign_list[:5],
            "exams": exam_list,
            "upcoming_exams": exam_list[:5],
            "plan": plan,
            "reminders_count": reminders_count,
            "metrics": {
                "gpa": 3.85,
                "total_assignments": total_assignments,
                "pending_assignments": pending_assignments,
                "upcoming_exams": upcoming_exams_count
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==============================================================================
# STUDY PLANNER APIS
# ==============================================================================
@app.post("/api/planner")
async def generate_study_plan(data: PlanCreate):
    try:
        subjects = data.subjects or data.focus_topics or "All Autonomous Disciplines"
        hours = data.daily_hours or data.hours_per_day or 3.5
        ctx_parts = []
        if data.exam_date:
            ctx_parts.append(f"Target Exam Date: {data.exam_date}")
        if data.difficulty:
            ctx_parts.append(f"Intensity Level: {data.difficulty}")
        if data.focus_topics:
            ctx_parts.append(f"Focus Topics: {data.focus_topics}")
        if data.context:
            ctx_parts.append(data.context)
            
        full_ctx = " | ".join(ctx_parts)

        plan_markdown = create_plan(
            student_id=data.student_id,
            subjects=str(subjects).strip(),
            hours_per_day=int(round(float(hours))),
            context=full_ctx.strip()
        )
        return {
            "success": True,
            "plan": plan_markdown,
            "plan_markdown": plan_markdown
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/planner/latest")
async def get_latest_study_plan(student_id: int):
    try:
        plan = get_latest_plan(student_id)
        if plan and isinstance(plan, dict):
            return {
                "success": True,
                "plan": plan.get("plan_content", ""),
                "plan_markdown": plan.get("plan_content", "")
            }
        return {"success": False, "plan": None}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==============================================================================
# ASSIGNMENT DESK APIS
# ==============================================================================
@app.get("/api/assignments")
async def get_assignments(student_id: int, status: Optional[str] = None):
    try:
        if status:
            rows = fetch_all(
                """SELECT a.*, c.course_name, DATEDIFF(a.due_date, CURDATE()) AS days_left 
                   FROM assignments a 
                   LEFT JOIN courses c ON a.course_id = c.course_id 
                   WHERE a.student_id = %s AND a.status = %s 
                   ORDER BY a.due_date ASC""",
                (student_id, status)
            )
        else:
            rows = fetch_all(
                """SELECT a.*, c.course_name, DATEDIFF(a.due_date, CURDATE()) AS days_left 
                   FROM assignments a 
                   LEFT JOIN courses c ON a.course_id = c.course_id 
                   WHERE a.student_id = %s 
                   ORDER BY a.due_date ASC""",
                (student_id,)
            )
        return {"success": True, "assignments": rows or []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/assignments")
async def create_assignment(data: AssignmentCreate):
    try:
        course_id = data.course_id
        if not course_id and data.course_name and data.course_name.strip():
            course_id = get_or_create_course(data.course_name.strip())

        assignment_id = execute(
            "INSERT INTO assignments (student_id, course_id, title, due_date, status) VALUES (%s, %s, %s, %s, 'Pending')",
            (data.student_id, course_id, data.title.strip(), data.due_date)
        )

        reminders_text = ""
        if data.auto_remind:
            try:
                reminders_text = create_reminders(
                    data.student_id, assignment_id, data.title.strip(), data.due_date
                )
            except Exception:
                pass

        return {
            "success": True,
            "assignment_id": assignment_id,
            "reminders": reminders_text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/api/assignments/{assignment_id}/status")
async def update_assignment_status(assignment_id: int, data: AssignmentStatusUpdate):
    try:
        db_update_assignment_status(assignment_id, data.status)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/assignments/{assignment_id}")
async def delete_assignment_endpoint(assignment_id: int):
    try:
        db_delete_assignment(assignment_id)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/assignments/reminders")
async def get_reminders(student_id: int):
    try:
        rems = get_all_student_reminders(student_id)
        return {"success": True, "reminders": rems or []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==============================================================================
# RESUME LAB APIS
# ==============================================================================
@app.post("/api/resume/analyze")
async def analyze_resume_endpoint(data: ResumeReviewRequest):
    try:
        target_role = data.target_role or "Software Engineer"
        if data.target_company:
            target_role += f" ({data.target_company})"

        review = review_resume(
            student_id=data.student_id,
            resume_text=data.resume_text.strip(),
            target_role=target_role
        )
        return {
            "success": True,
            "analysis": review,
            "review_markdown": review
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==============================================================================
# QUIZ STUDIO APIS
# ==============================================================================
@app.post("/api/quiz/generate")
async def generate_quiz_endpoint(data: QuizGenerateRequest):
    try:
        count = data.question_count or data.count or 5
        kind_desc = f"{data.kind} (Level: {data.difficulty})"

        quiz_md = create_quiz(
            student_id=data.student_id or 1,
            subject=(data.subject or "Autonomous Sciences").strip(),
            topic=data.topic.strip(),
            kind=kind_desc,
            count=count
        )
        return {
            "success": True,
            "quiz_markdown": quiz_md,
            "analysis": quiz_md
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/quiz/vault")
async def get_quiz_vault(student_id: int):
    try:
        quizzes = get_student_quizzes(student_id)
        return {"success": True, "quizzes": quizzes or []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==============================================================================
# EXAM MAP APIS
# ==============================================================================
@app.get("/api/exams")
async def get_exams(student_id: int):
    try:
        exams = fetch_all(
            """SELECT e.*, c.course_name, DATEDIFF(e.exam_date, CURDATE()) AS days_left 
               FROM exams e 
               LEFT JOIN courses c ON e.course_id = c.course_id 
               WHERE e.student_id = %s 
               ORDER BY e.exam_date ASC""",
            (student_id,)
        )
        return {"success": True, "exams": exams or []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/exams")
async def create_exam(data: ExamCreate):
    try:
        course_name = data.course_name or data.name or "Semester Examination"
        course_id = data.course_id
        if not course_id and course_name:
            course_id = get_or_create_course(course_name.strip())

        exam_date = data.exam_date or data.date
        exam_id = execute(
            "INSERT INTO exams (student_id, course_id, exam_date, exam_time, venue) VALUES (%s, %s, %s, %s, %s)",
            (data.student_id, course_id, exam_date, (data.exam_time or "10:30 AM").strip(), (data.venue or "Main Academic Block").strip())
        )
        return {
            "success": True,
            "exam_id": exam_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/exams/{exam_id}")
async def delete_exam_endpoint(exam_id: int):
    try:
        db_delete_exam(exam_id)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/exams/revision-schedule")
async def generate_exam_revision(data: ExamRevisionRequest):
    try:
        upcoming = fetch_all(
            """SELECT e.*, c.course_name 
               FROM exams e 
               LEFT JOIN courses c ON e.course_id = c.course_id 
               WHERE e.student_id = %s AND e.exam_date >= CURDATE() 
               ORDER BY e.exam_date ASC""",
            (data.student_id,)
        )
        if not upcoming:
            raise HTTPException(status_code=400, detail="No upcoming exams registered. Please add an exam target first.")
        
        schedule = create_revision_schedule(upcoming)
        return {
            "success": True,
            "schedule": schedule,
            "schedule_markdown": schedule
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=5000, reload=True)
