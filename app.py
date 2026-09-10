import os
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv
from frontend import home, dashboard, planner, assignments, resume, quiz, exams
from backend.db import get_or_create_student

load_dotenv()
st.set_page_config(page_title="Ruia AI Student Companion", page_icon="✦", layout="wide", initial_sidebar_state="expanded")
st.markdown(f"<style>{Path('assets/styles.css').read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

if 'student' not in st.session_state: st.session_state.student = None
with st.sidebar:
    st.markdown("## RUIA <span style='color:#c9a86a'>AI</span>", unsafe_allow_html=True)
    st.caption("STUDENT COMPANION")
    page = st.radio("Navigate", ["Welcome", "Dashboard", "Study Planner", "Assignments", "Resume Lab", "Quiz Studio", "Exam Map"], label_visibility="collapsed")
    st.divider()
    if st.session_state.student:
        st.markdown(f"**{st.session_state.student['name']}**")
        if st.button("Switch profile"): st.session_state.student = None; st.rerun()

if st.session_state.student is None and page != "Welcome":
    st.info("Set up your student profile to use your companion.")
    with st.form("profile"):
        name = st.text_input("Full name")
        email = st.text_input("College email")
        program, year = st.columns(2)
        program = program.text_input("Programme")
        year = year.selectbox("Year", [1, 2, 3, 4, 5])
        create = st.form_submit_button("Enter companion")
    if create:
        if not all([name, email, program]): st.warning("Please complete every profile field.")
        else:
            try: st.session_state.student = get_or_create_student(name, email, program, year); st.rerun()
            except Exception as exc: st.error(f"We could not connect to MySQL. Check your .env and run schema.sql. Details: {exc}")
elif page == "Welcome": home.render()
elif page == "Dashboard": dashboard.render(st.session_state.student)
elif page == "Study Planner": planner.render(st.session_state.student)
elif page == "Assignments": assignments.render(st.session_state.student)
elif page == "Resume Lab": resume.render(st.session_state.student)
elif page == "Quiz Studio": quiz.render(st.session_state.student)
elif page == "Exam Map": exams.render(st.session_state.student)

