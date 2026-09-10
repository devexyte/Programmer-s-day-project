from backend.ai import generate_study_plan
from backend.db import execute, fetch_all


def create_plan(student_id, subjects, hours, exam_context=""):
    plan = generate_study_plan(subjects, hours, exam_context)
    execute("INSERT INTO study_plans (student_id, generated_plan) VALUES (%s, %s)", (student_id, plan))
    return plan


def get_latest_plan(student_id):
    plans = fetch_all(
        "SELECT * FROM study_plans WHERE student_id = %s ORDER BY created_at DESC LIMIT 1",
        (student_id,)
    )
    return plans[0] if plans else None
