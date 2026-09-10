import streamlit as st
from backend.planner_logic import create_plan

def render(student):
    st.title("Study Planner")
    st.caption("A week that works with your commitments, not against them.")
    with st.form("plan"):
        subjects = st.text_area("Subjects & difficulty", placeholder="Economics — High\nPython — Medium\nStatistics — High")
        hours = st.slider("Focused hours available each day", 1, 10, 3)
        exams = st.text_input("Upcoming exams (optional)", placeholder="Statistics — 22 Sep")
        submit = st.form_submit_button("Create my weekly plan")
    if submit:
        if not subjects.strip(): st.warning("Add at least one subject."); return
        with st.spinner("Ruia AI is composing your plan..."):
            try: st.markdown(create_plan(student['student_id'], subjects, hours, exams))
            except Exception as exc: st.error(str(exc))

