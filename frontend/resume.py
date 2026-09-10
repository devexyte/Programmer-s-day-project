import streamlit as st
from backend.resume_logic import review_resume

def render(student):
    st.title("Resume Lab")
    st.caption("Thoughtful feedback that preserves your voice and your facts.")
    resume = st.text_area("Paste your resume", height=330, placeholder="Your education, experience, projects and skills...")
    if st.button("Review with Ruia AI", type="primary"):
        if not resume.strip(): st.warning("Paste your resume first.")
        else:
            with st.spinner("Reviewing clarity, structure and impact..."):
                try:
                    review = review_resume(resume)
                    st.markdown(review)
                    st.download_button("Download reviewed resume", review, "ruia_resume_review.md", "text/markdown")
                except Exception as exc: st.error(str(exc))

