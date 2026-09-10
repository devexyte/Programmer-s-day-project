import os
import google.generativeai as genai


def generate(prompt):
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("Gemini is not configured. Add GEMINI_API_KEY to your .env file.")
    try:
        genai.configure(api_key=key)
        model = genai.GenerativeModel(os.getenv("GEMINI_MODEL", "gemini-1.5-flash"))
        response = model.generate_content(prompt)
        return response.text
    except Exception as exc:
        raise RuntimeError(f"Gemini could not complete this request: {exc}") from exc

