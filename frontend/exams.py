import streamlit as st
from backend.db import execute, fetch_all
from backend.exam_logic import create_revision_schedule

def render(student):
    st.title("Exam Map")
    with st.form("exam"):
        course, date, time, venue = st.columns(4)
        course = course.text_input("Course / paper")
        date = date.date_input("Exam date")
        time = time.text_input("Time", placeholder="10:00 AM")
        venue = venue.text_input("Venue", placeholder="Main Building")
        submit = st.form_submit_button("Save exam")
    if submit:
        if not course: st.warning("Add your course or paper name.")
        else: execute("INSERT INTO exams (student_id,exam_date,exam_time,venue) VALUES (%s,%s,%s,%s)", (student['student_id'], date, time, venue)); st.success("Exam saved.")
    try:
        exams = fetch_all("SELECT *, DATEDIFF(exam_date,CURDATE()) AS days_left FROM exams WHERE student_id=%s ORDER BY exam_date", (student['student_id'],))
        if exams:
            st.subheader("Your exam calendar")
            for item in exams: st.markdown(f"<div class='countdown'><b>{item.get('venue') or 'Exam'}</b><strong>{item['days_left']} days</strong><small>{item['exam_date']} · {item.get('exam_time') or 'Time TBC'}</small></div>", unsafe_allow_html=True)
            if st.button("Generate revision schedule"):
                with st.spinner("Planning your revision..."):
                    try: st.markdown(create_revision_schedule([{k: str(v) for k,v in e.items()} for e in exams]))
                    except Exception as exc: st.error(str(exc))
        else: st.info("Your saved exam dates will appear here.")
    except Exception as exc: st.error(str(exc))

