from backend.ai import generate_revision_schedule


def create_revision_schedule(exams):
    formatted_exams = []
    for e in exams:
        cname = e.get('course_name') or 'Paper'
        edate = str(e.get('exam_date'))
        etime = e.get('exam_time') or 'TBC'
        venue = e.get('venue') or 'Campus'
        formatted_exams.append(f"- {cname}: {edate} at {etime} (Venue: {venue})")
    context = "\n".join(formatted_exams) if formatted_exams else str(exams)
    return generate_revision_schedule(context)
