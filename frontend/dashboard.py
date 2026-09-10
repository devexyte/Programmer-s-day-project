from datetime import datetime
import streamlit as st
from backend.db import dashboard, update_assignment_status

def _navigate(target):
    st.session_state["nav_goto"] = target
    st.rerun()

def render(student):
    if not student:
        st.info("Please set up or select your student profile.")
        return

    # Dynamic time greeting
    hour = datetime.now().hour
    if hour < 12:
        greeting = "Good morning"
    elif hour < 17:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"

    first_name = student['name'].split()[0]
    
    st.html(f"""<div style="margin-bottom: 24px;">
<div class="section-kicker">RAMNARAIN RUIA AUTONOMOUS COLLEGE · RUI COMMAND CENTER</div>
<h1 style="margin: 0 0 6px 0;">{greeting}, {first_name}.</h1>
<p style="color: #475569; font-size: 1.05rem; margin: 0;">
Enrolled in <b>{student['program']}</b> · Year {student['year']} · Connected to MySQL Database (<b>Ruia-Buddy</b>).
</p>
</div>""")

    try:
        assignments, exams, plan, reminders_count = dashboard(student['student_id'])
    except Exception as exc:
        st.error(f"Error fetching dashboard metrics: {exc}")
        return

    # Metric Cards Strip
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Active Assignments", len(assignments))
    with m2:
        st.metric("Upcoming Exams", len(exams))
    with m3:
        next_exam_days = f"{exams[0]['days_left']}d" if exams else "None"
        st.metric("Closest Exam", next_exam_days)
    with m4:
        st.metric("RUI Study Plan", "Active" if plan else "Not Created")

    st.html("<div style='margin-bottom: 20px;'></div>")

    # Quick Action Bar
    q1, q2, q3, q4 = st.columns(4)
    with q1:
        if st.button("➕ Add Assignment", use_container_width=True):
            _navigate("📝 Assignment Desk")
    with q2:
        if st.button("⏱️ Schedule Exam", use_container_width=True):
            _navigate("⏱️ Exam Map")
    with q3:
        if st.button("📅 Update Study Plan", use_container_width=True):
            _navigate("📅 Study Planner")
    with q4:
        if st.button("🎯 Practice Quiz", use_container_width=True):
            _navigate("🎯 Quiz Studio")

    st.html("<div style='margin-bottom: 24px;'></div>")

    # Split View: Deadlines & Exam Horizon
    left_col, right_col = st.columns([1.15, 0.85], gap="large")

    with left_col:
        st.markdown("### 📝 Upcoming Coursework & Deadlines")
        if assignments:
            for item in assignments:
                days_left = item.get('days_left', 0)
                status_class = "status-urgent" if days_left <= 2 else "status-pending"
                due_text = "Today!" if days_left == 0 else (f"Tomorrow" if days_left == 1 else f"in {days_left} days")
                
                c1, c2 = st.columns([4.2, 1])
                with c1:
                    st.html(f"""<div class="list-item" style="margin-bottom: 8px;">
<div class="list-item-content">
<div class="list-item-title">{item['title']}</div>
<div class="list-item-meta">
<span>📚 {item.get('course_name') or 'Autonomous Course'}</span>
<span>·</span>
<span>📅 Due {item['due_date']} ({due_text})</span>
<span class="status-pill {status_class}">{item['status']}</span>
</div>
</div>
</div>""")

                with c2:
                    if st.button("✓ Done", key=f"done_dash_{item['assignment_id']}", help="Mark as completed", use_container_width=True):
                        try:
                            update_assignment_status(item['assignment_id'], "Completed")
                            st.toast(f"Marked '{item['title']}' as completed! 🎉")
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))
        else:
            st.html("""<div style="background:#FFF; border:1px dashed #DACDBB; border-radius:12px; padding:24px; text-align:center; color:#0F172A;">
<p style="margin:0; font-weight:600; color:#0F172A;">No pending assignment deadlines!</p>
<small style="color:#64748B;">Head to the Assignment Desk to add coursework and generate AI milestone reminders.</small>
</div>""")


    with right_col:
        st.markdown("### ⏱️ Examination Horizon")
        if exams:
            for exam in exams:
                days = exam.get('days_left', 0)
                badge_class = "urgent" if days <= 3 else ("warning" if days <= 7 else "")
                
                st.html(f"""<div class="countdown-card">
<div>
<div style="font-weight:700; color:#701A24; font-size:1.05rem;">{exam.get('course_name') or 'Degree Examination'}</div>
<div style="font-size:0.82rem; color:#64748B; margin-top:4px;">
📍 {exam.get('venue') or 'Main Academic Heritage Block'} · 🕒 {exam.get('exam_time') or '10:00 AM'}
</div>
<div style="font-size:0.78rem; color:#64748B; margin-top:2px;">
Date: <b>{exam['exam_date']}</b>
</div>
</div>
<div class="countdown-badge {badge_class}">
<div class="countdown-days">{days}</div>
<div class="countdown-sub">Days Left</div>
</div>
</div>""")

        else:
            st.html("""<div style="background:#FFF; border:1px dashed #DACDBB; border-radius:12px; padding:24px; text-align:center; color:#0F172A;">
<p style="margin:0; font-weight:600; color:#0F172A;">No exams scheduled currently.</p>
<small style="color:#64748B;">Register your paper dates in Exam Map to start countdowns and revision schedules.</small>
</div>""")


    st.html("<div style='margin-bottom: 32px;'></div>")

    # Study Plan Preview Section
    if plan:
        st.markdown("### 🏛️ Current 7-Day Academic Plan")
        with st.expander("📖 View Full Weekly Study Timetable", expanded=False):
            st.markdown(plan['generated_plan'], unsafe_allow_html=True)
    else:
        st.html("""<div class="ruia-quote-box" style="margin: 16px 0;">
<b>No weekly study plan created yet.</b> Visit the <b>Study Planner</b> to generate an AI-optimized schedule balanced around your autonomous coursework.
</div>""")

