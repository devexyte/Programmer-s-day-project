from backend.ai import generate
from backend.db import execute

def create_reminders(student_id, assignment_id, title, due_date):
    prompt = f"Create a concise reminder schedule for a Ruia College assignment titled '{title}' due on {due_date}. Include preparation checkpoints and a final submission reminder. Return plain bullet points with dates."
    text = generate(prompt)
    execute("INSERT INTO reminders (student_id,assignment_id,reminder_text,reminder_date) VALUES (%s,%s,%s,%s)", (student_id, assignment_id, text, due_date))
    return text

