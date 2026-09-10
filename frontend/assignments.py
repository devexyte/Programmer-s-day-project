import streamlit as st
from backend.db import execute, fetch_all
from backend.reminder_logic import create_reminders

def render(student):
    st.title("Assignment Desk")
    with st.form("assignment"):
        title = st.text_input("Assignment title")
        due = st.date_input("Submission deadline")
        auto = st.checkbox("Ask Ruia AI to create reminders", value=True)
        submit = st.form_submit_button("Add assignment")
    if submit:
        if not title: st.warning("Add an assignment title.")
        else:
            assignment_id = execute("INSERT INTO assignments (student_id,title,due_date,status) VALUES (%s,%s,%s,'Pending')", (student['student_id'], title, due))
            st.success("Assignment saved.")
            if auto:
                with st.spinner("Creating your reminder rhythm..."):
                    try: st.markdown(create_reminders(student['student_id'], assignment_id, title, due))
                    except Exception as exc: st.error(str(exc))
    st.subheader("Your assignments")
    try:
        for item in fetch_all("SELECT * FROM assignments WHERE student_id=%s ORDER BY due_date", (student['student_id'],)):
            st.markdown(f"<div class='list-item'><b>{item['title']}</b><br><small>{item['due_date']} · {item['status']}</small></div>", unsafe_allow_html=True)
    except Exception as exc: st.error(str(exc))

