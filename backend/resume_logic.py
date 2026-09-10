from backend.ai import generate_resume_review


def review_resume(resume_text, target_role="General Academic & Corporate Placement"):
    return generate_resume_review(resume_text, target_role)
