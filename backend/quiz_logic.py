from backend.ai import generate
from backend.db import execute

def create_quiz(student_id, subject, topic, format_name, count):
    prompt = f"You are Ruia AI. Create {count} {format_name} for {subject}, topic: {topic}. Make questions rigorous but appropriate for an undergraduate. For MCQs provide four choices and clearly state an answer after each question. Format in Markdown."
    quiz = generate(prompt)
    execute("INSERT INTO quizzes (student_id,subject,topic,generated_quiz) VALUES (%s,%s,%s,%s)", (student_id, subject, topic, quiz))
    return quiz

