import streamlit as st
from backend.db import (
    execute, fetch_all, get_all_courses, get_or_create_course, delete_exam
)
from backend.exam_logic import create_revision_schedule

def render(student):
    if not student:
        st.info("Please set up or select your student profile.")
        return

    st.markdown("""
    <div style="margin-bottom: 20px;">
        <div class="section-kicker">RAMNARAIN RUIA AUTONOMOUS COLLEGE · RUI EXAM MAP</div>
        <h1 style="margin: 0 0 6px 0;">Exam Map & Revision Architect</h1>
        <p style="color: #475569; font-size: 1.05rem; margin: 0;">
            Keep track of Mumbai University / Autonomous exam venues, countdown clocks, and let <b>RUI</b> architect your spaced repetition revision master schedules.
        </p>
    </div>
    """, unsafe_allow_html=True)

    tab_calendar, tab_schedule = st.tabs(["📅 Exam Calendar & Registration", "📖 AI Revision Master Schedule"])

    with tab_calendar:
        st.markdown("### ➕ Register Upcoming Examination Paper")
        
        courses = get_all_courses()
        course_names = [c['course_name'] for c in courses]
        course_names.insert(0, "— Select or type below —")

        with st.form("exam_form"):
            c1, c2 = st.columns(2)
            with c1:
                selected_course = st.selectbox("Course / Academic Paper", course_names)
                custom_course = st.text_input("Or custom paper title (if not listed above)", placeholder="e.g. Advanced Computer Networks (Paper III)")
            with c2:
                exam_date = st.date_input("Examination Date")
                time_slot = st.selectbox("Exam Session / Time", ["10:30 AM – 01:00 PM (Morning)", "02:30 PM – 05:00 PM (Afternoon)", "09:00 AM – 12:00 PM (Honors)", "Custom Time"])
                if time_slot == "Custom Time":
                    time_slot = st.text_input("Specify Time", placeholder="e.g. 11:00 AM")
            
            venue = st.text_input("Room / Venue", placeholder="e.g. Main Heritage Building, Room 204")
            
            save_exam = st.form_submit_button("Save Paper to Exam Map", use_container_width=True)

        if save_exam:
            paper_name = custom_course.strip() if custom_course.strip() else (selected_course if selected_course != "— Select or type below —" else None)
            if not paper_name:
                st.warning("Please specify your course or paper name.")
            else:
                try:
                    course_id = get_or_create_course(paper_name)
                    execute(
                        "INSERT INTO exams (student_id, course_id, exam_date, exam_time, venue) VALUES (%s, %s, %s, %s, %s)",
                        (student['student_id'], course_id, exam_date, time_slot, venue.strip() or "Ruia Main Campus")
                    )
                    st.success(f"Examination '{paper_name}' registered successfully!")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Failed to register exam: {exc}")

        st.markdown("---")
        st.markdown("### ⏱️ Registered Examination Schedule")

        try:
            exams = fetch_all(
                """SELECT e.*, c.course_name, DATEDIFF(e.exam_date, CURDATE()) AS days_left 
                   FROM exams e 
                   LEFT JOIN courses c ON e.course_id = c.course_id 
                   WHERE e.student_id = %s 
                   ORDER BY e.exam_date ASC""",
                (student['student_id'],)
            )

            if exams:
                for item in exams:
                    days = item.get('days_left', 0)
                    badge_class = "urgent" if days <= 3 else ("warning" if days <= 7 else "")
                    c_card, c_del = st.columns([5, 1])
                    
                    with c_card:
                        st.markdown(f"""
                        <div class="countdown-card">
                            <div>
                                <div style="font-weight:700; color:#6B0F1A; font-size:1.1rem;">
                                    {item.get('course_name') or 'Autonomous Paper'}
                                </div>
                                <div style="font-size:0.85rem; color:#64748B; margin-top:4px;">
                                    📍 {item.get('venue') or 'Main Academic Block'} · 🕒 {item.get('exam_time') or '10:00 AM'}
                                </div>
                                <div style="font-size:0.8rem; color:#A1A1AA; margin-top:2px;">
                                    Scheduled on: <b>{item['exam_date']}</b>
                                </div>
                            </div>
                            <div class="countdown-badge {badge_class}">
                                <div class="countdown-days">{days}</div>
                                <div class="countdown-sub">Days Left</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with c_del:
                        if st.button("Delete", key=f"del_exam_{item['exam_id']}", use_container_width=True):
                            delete_exam(item['exam_id'])
                            st.toast("Exam removed from schedule.")
                            st.rerun()
            else:
                st.info("No examination dates logged yet. Register your upcoming semester papers above.")
        except Exception as exc:
            st.error(str(exc))

    with tab_schedule:
        st.markdown("### 📖 Spaced Repetition Revision Strategy")
        try:
            upcoming = fetch_all(
                """SELECT e.*, c.course_name 
                   FROM exams e 
                   LEFT JOIN courses c ON e.course_id = c.course_id 
                   WHERE e.student_id = %s AND e.exam_date >= CURDATE() 
                   ORDER BY e.exam_date ASC""",
                (student['student_id'],)
            )

            if upcoming:
                st.write(f"Detected **{len(upcoming)}** upcoming papers on your horizon.")
                if st.button("✦ Generate Reverse-Engineered Revision Schedule", type="primary", use_container_width=True):
                    with st.spinner("Ruia AI is synthesizing your spaced repetition revision timetable..."):
                        try:
                            rev_plan = create_revision_schedule(upcoming)
                            st.session_state["active_revision_plan"] = rev_plan
                        except Exception as exc:
                            st.error(str(exc))

                active_plan = st.session_state.get("active_revision_plan")
                if active_plan:
                    st.markdown("---")
                    st.markdown(active_plan, unsafe_allow_html=True)
                    st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)
                    st.download_button(
                        "📥 Download Revision Timetable (.md)",
                        data=active_plan,
                        file_name="ruia_revision_timetable.md",
                        mime="text/markdown",
                        use_container_width=True
                    )
            else:
                st.info("Log at least one upcoming exam in the 'Exam Calendar' tab to enable revision planning.")
        except Exception as exc:
            st.error(str(exc))
