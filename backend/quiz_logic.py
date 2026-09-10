from backend.ai import generate_quiz
from backend.db import execute, fetch_all


def create_quiz(student_id, subject, topic, format_name="multiple-choice questions", count=10):
    quiz_content = generate_quiz(subject, topic, format_name, count)
    execute(
        "INSERT INTO quizzes (student_id, subject, topic, generated_quiz) VALUES (%s, %s, %s, %s)",
        (student_id, subject, topic, quiz_content)
    )
    return quiz_content


def get_student_quizzes(student_id):
    return fetch_all(
        "SELECT * FROM quizzes WHERE student_id = %s ORDER BY created_at DESC LIMIT 10",
        (student_id,)
    )
