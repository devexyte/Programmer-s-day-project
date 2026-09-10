import streamlit as st
from backend.db import dashboard

def render(student):
    st.title(f"Good day, {student['name'].split()[0]}.")
    st.caption("Here is the shape of your academic week.")
    try: assignments, exams, plan = dashboard(student['student_id'])
    except Exception as exc: st.error(str(exc)); return
    a, e, p = st.columns(3)
    a.metric("Upcoming assignments", len(assignments))
    e.metric("Exams on your horizon", len(exams))
    p.metric("Latest plan", "Ready" if plan else "Not created")
    left, right = st.columns([1.15, .85])
    with left:
        st.subheader("Coming up")
        if assignments:
            for item in assignments: st.markdown(f"<div class='list-item'><b>{item['title']}</b><br><small>{item.get('course_name') or 'Independent'} · Due {item['due_date']}</small></div>", unsafe_allow_html=True)
        else: st.info("Your upcoming assignments will appear here.")
    with right:
        st.subheader("Exam countdown")
        if exams:
            for exam in exams: st.markdown(f"<div class='countdown'><b>{exam.get('course_name') or 'Exam'}</b><strong>{exam['days_left']} days</strong><small>{exam['exam_date']} · {exam.get('venue') or 'Venue TBC'}</small></div>", unsafe_allow_html=True)
        else: st.info("Add an exam to start your countdown.")
    if plan:
        with st.expander("Read your latest study plan"): st.markdown(plan['generated_plan'])

