from backend.ai import generate
from backend.db import execute

def create_plan(student_id, subjects, hours, exam_context):
    prompt = f'''You are Ruia AI, an encouraging academic planner for Ruia College, Mumbai. Create a precise 7-day study plan in Markdown.
Subjects and difficulty: {subjects}\nAvailable study hours per day: {hours}\nUpcoming exams: {exam_context or 'None supplied'}.
Balance difficult courses, active recall, revision and breaks. Use a day-by-day table, then give three concise study habits.'''
    plan = generate(prompt)
    execute("INSERT INTO study_plans (student_id,generated_plan) VALUES (%s,%s)", (student_id, plan))
    return plan

