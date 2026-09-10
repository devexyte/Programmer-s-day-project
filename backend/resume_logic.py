from backend.ai import generate

def review_resume(resume):
    prompt = f'''You are a career adviser for Ruia College students. Review this resume for grammar, clarity, structure and impact. Return these sections: Strengths, Priority improvements, and Polished resume. Preserve facts; never invent achievements.\n\nRESUME:\n{resume}'''
    return generate(prompt)

