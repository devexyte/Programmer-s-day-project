import streamlit as st
from backend.db import (
    execute, fetch_all, get_all_courses, get_or_create_course,
    update_assignment_status, delete_assignment
)
from backend.reminder_logic import create_reminders, get_all_student_reminders

def render(student):
    if not student:
        st.info("Please set up or select your student profile.")
        return

    st.markdown("""
    <div style="margin-bottom: 20px;">
        <div class="section-kicker">RAMNARAIN RUIA AUTONOMOUS COLLEGE · RUI ASSIGNMENT DESK</div>
        <h1 style="margin: 0 0 6px 0;">Assignment Desk & Milestone Reminders</h1>
        <p style="color: #475569; font-size: 1.05rem; margin: 0;">
            Track collegiate coursework, submissions, and let <b>RUI</b> automatically synthesize multi-stage preparation checkpoints.
        </p>
    </div>
    """, unsafe_allow_html=True)

    tab_create, tab_active, tab_completed, tab_reminders = st.tabs([
        "➕ Register New Assignment",
        "📌 Active Submissions",
        "✅ Completed Archive",
        "🔔 AI Milestone Reminders"
    ])

    with tab_create:
        st.markdown("### 📝 Assignment Details")
        
        courses = get_all_courses()
        course_names = [c['course_name'] for c in courses]
        course_names.insert(0, "— Select or create below —")

        with st.form("new_assignment_form"):
            selected_course = st.selectbox("Associated Course / Paper", course_names)
            custom_course = st.text_input("Or enter custom paper name (if not in list above)", placeholder="e.g. Modern Web Engineering Lab")
            
            title = st.text_input("Assignment Title / Deliverable", placeholder="e.g. Research Paper on Transformer Attention Mechanisms")
            due_date = st.date_input("Official Due Date")
            
            auto_remind = st.checkbox("✦ Automatically construct AI milestone preparation checkpoints", value=True)
            
            submit = st.form_submit_button("Save Assignment to Profile", use_container_width=True)

        if submit:
            if not title.strip():
                st.warning("Please provide an assignment title.")
            else:
                # Determine course_id
                course_id = None
                course_to_use = custom_course.strip() if custom_course.strip() else (selected_course if selected_course != "— Select or create below —" else None)
                if course_to_use:
                    course_id = get_or_create_course(course_to_use)

                try:
                    assignment_id = execute(
                        "INSERT INTO assignments (student_id, course_id, title, due_date, status) VALUES (%s, %s, %s, %s, 'Pending')",
                        (student['student_id'], course_id, title.strip(), due_date)
                    )
                    st.success(f"Assignment '{title}' saved successfully!")

                    if auto_remind:
                        with st.spinner("Synthesizing strategic milestone checkpoints..."):
                            reminders = create_reminders(student['student_id'], assignment_id, title.strip(), str(due_date))
                            st.markdown("#### 🔔 Generated Milestone Roadmap")
                            st.markdown(reminders, unsafe_allow_html=True)
                    st.rerun()
                except Exception as exc:
                    st.error(f"Failed to record assignment: {exc}")

    with tab_active:
        st.markdown("### 📋 Active Deadlines")
        try:
            active_items = fetch_all(
                """SELECT a.*, c.course_name, DATEDIFF(a.due_date, CURDATE()) AS days_left 
                   FROM assignments a 
                   LEFT JOIN courses c ON a.course_id = c.course_id 
                   WHERE a.student_id = %s AND a.status != 'Completed' 
                   ORDER BY a.due_date ASC""",
                (student['student_id'],)
            )
            if active_items:
                for item in active_items:
                    days = item.get('days_left', 0)
                    due_badge = "🚨 Due Today" if days == 0 else (f"⚠️ Due Tomorrow" if days == 1 else f"⏳ {days} days remaining")
                    status_class = "status-urgent" if days <= 2 else "status-pending"

                    col_main, col_btn1, col_btn2 = st.columns([5, 1.2, 1])
                    with col_main:
                        st.markdown(f"""
                        <div class="list-item" style="margin-bottom:6px;">
                            <div class="list-item-content">
                                <div class="list-item-title">{item['title']}</div>
                                <div class="list-item-meta">
                                    <span>📚 {item.get('course_name') or 'Autonomous Paper'}</span>
                                    <span>·</span>
                                    <span>📅 Due {item['due_date']}</span>
                                    <span class="status-pill {status_class}">{due_badge}</span>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col_btn1:
                        if st.button("Mark Done", key=f"mark_active_{item['assignment_id']}", use_container_width=True):
                            update_assignment_status(item['assignment_id'], "Completed")
                            st.toast("Assignment completed!")
                            st.rerun()
                    with col_btn2:
                        if st.button("Delete", key=f"del_active_{item['assignment_id']}", use_container_width=True):
                            delete_assignment(item['assignment_id'])
                            st.toast("Assignment removed.")
                            st.rerun()
            else:
                st.info("No active assignments pending. Great work staying on top of your deliverables!")
        except Exception as exc:
            st.error(f"Error reading assignments: {exc}")

    with tab_completed:
        st.markdown("### 🏆 Completed Coursework Archive")
        try:
            completed_items = fetch_all(
                """SELECT a.*, c.course_name 
                   FROM assignments a 
                   LEFT JOIN courses c ON a.course_id = c.course_id 
                   WHERE a.student_id = %s AND a.status = 'Completed' 
                   ORDER BY a.due_date DESC""",
                (student['student_id'],)
            )
            if completed_items:
                for item in completed_items:
                    st.markdown(f"""
                    <div class="list-item">
                        <div class="list-item-content">
                            <div class="list-item-title" style="text-decoration: line-through; color:#71717A;">{item['title']}</div>
                            <div class="list-item-meta">
                                <span>📚 {item.get('course_name') or 'Autonomous Paper'}</span>
                                <span>·</span>
                                <span>Completed on schedule</span>
                                <span class="status-pill status-completed">Completed</span>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("<p style='color:#71717A;'>Completed assignments will be archived here.</p>", unsafe_allow_html=True)
        except Exception as exc:
            st.error(str(exc))

    with tab_reminders:
        st.markdown("### 🔔 Active Milestone Roadmaps")
        try:
            reminders = get_all_student_reminders(student['student_id'])
            if reminders:
                for r in reminders:
                    with st.expander(f"📌 {r.get('assignment_title', 'Assignment')} (Due: {r.get('reminder_date')})", expanded=True):
                        st.markdown(r['reminder_text'], unsafe_allow_html=True)
            else:
                st.info("No active milestone roadmaps. Check the 'Automatically construct AI milestone preparation checkpoints' box when creating an assignment.")
        except Exception as exc:
            st.error(str(exc))
