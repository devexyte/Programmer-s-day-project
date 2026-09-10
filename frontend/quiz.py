import streamlit as st
from backend.quiz_logic import create_quiz

def render(student):
    st.title("Quiz Studio")
    with st.form("quiz"):
        subject, topic = st.columns(2)
        subject = subject.text_input("Subject")
        topic = topic.text_input("Topic")
        kind, count = st.columns(2)
        kind = kind.selectbox("Question format", ["multiple-choice questions", "short-answer questions", "flashcards"])
        count = count.slider("Questions", 5, 20, 10)
        submit = st.form_submit_button("Generate practice set")
    if submit:
        if not subject or not topic: st.warning("Add both a subject and topic.")
        else:
            with st.spinner("Building your practice set..."):
                try:
                    quiz = create_quiz(student['student_id'], subject, topic, kind, count)
                    st.markdown(quiz)
                    st.download_button("Download practice set", quiz, "ruia_quiz.md", "text/markdown")
                except Exception as exc: st.error(str(exc))

