from backend.ai import generate_assignment_reminders
from backend.db import execute, fetch_all


def create_reminders(student_id, assignment_id, title, due_date):
    text = generate_assignment_reminders(title, due_date)
    execute(
        "INSERT INTO reminders (student_id, assignment_id, reminder_text, reminder_date) VALUES (%s, %s, %s, %s)",
        (student_id, assignment_id, text, due_date)
    )
    return text


def get_assignment_reminders(student_id, assignment_id):
    return fetch_all(
        "SELECT * FROM reminders WHERE student_id = %s AND assignment_id = %s ORDER BY reminder_id DESC",
        (student_id, assignment_id)
    )


def get_all_student_reminders(student_id):
    return fetch_all(
        """SELECT r.*, a.title AS assignment_title 
           FROM reminders r 
           JOIN assignments a ON r.assignment_id = a.assignment_id 
           WHERE r.student_id = %s 
           ORDER BY r.reminder_id DESC LIMIT 10""",
        (student_id,)
    )
