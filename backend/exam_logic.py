from backend.ai import generate

def create_revision_schedule(exams):
    prompt = f"You are Ruia AI. Create a focused revision timetable from these upcoming exams: {exams}. Use a date-by-date Markdown table, give priority to the earliest exams, and include revision techniques and recovery breaks."
    return generate(prompt)

