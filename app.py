import os
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv
from frontend import home, dashboard, planner, assignments, resume, quiz, exams
from backend.db import get_or_create_student, get_all_students, seed_default_data

load_dotenv()

st.set_page_config(
    page_title="Ruia AI Student Companion | Ramnarain Ruia Autonomous College",
    page_icon="assets/logo.png" if Path("assets/logo.png").exists() else "🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS
css_path = Path("assets/styles.css")
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

# Pre-seed default Ruia courses & students in MySQL
try:
    seed_default_data()
except Exception:
    pass

# Initialize session states
if "student" not in st.session_state:
    st.session_state.student = None

nav_options = [
    "🏛️ Welcome",
    "📊 Academic Dashboard",
    "📅 Study Planner",
    "📝 Assignment Desk",
    "📑 Resume Lab",
    "🎯 Quiz Studio",
    "⏱️ Exam Map"
]

if "nav_selection" not in st.session_state:
    st.session_state["nav_selection"] = "🏛️ Welcome"

# Compute index safely
current_index = 0
if st.session_state["nav_selection"] in nav_options:
    current_index = nav_options.index(st.session_state["nav_selection"])

# Sidebar Rendering
with st.sidebar:
    logo_file = Path("assets/logo.png")
    if not logo_file.exists():
        logo_file = Path("assets/logo.jpg")

    st.markdown('<div class="sidebar-brand-card">', unsafe_allow_html=True)
    if logo_file.exists():
        st.image(str(logo_file), use_container_width=True)
    st.markdown("""
        <div class="sidebar-brand-sub">Ramnarain Ruia College</div>
        <div style="font-size:0.72rem; color:#800000; font-weight:700; letter-spacing:0.05em; text-align:center;">Autonomous · Mumbai</div>
    </div>
    """, unsafe_allow_html=True)

    # Student Profile Chip in Sidebar
    if st.session_state.student:
        student = st.session_state.student
        initials = "".join([part[0] for part in student['name'].split()][:2]).upper() or "RC"
        st.markdown(f"""
        <div class="sidebar-profile-card">
            <div class="sidebar-avatar">{initials}</div>
            <div class="sidebar-profile-info">
                <div class="sidebar-profile-name">{student['name']}</div>
                <div class="sidebar-profile-dept">{student['program']} · Year {student['year']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("↻ Switch Student", use_container_width=True):
            st.session_state.student = None
            st.session_state["nav_selection"] = "🏛️ Welcome"
            st.rerun()
        st.markdown("<div style='margin-bottom:10px;'></div>", unsafe_allow_html=True)

    # Connected Radio Navigation
    def _on_nav_change():
        st.session_state["nav_selection"] = st.session_state.sidebar_radio_nav

    selected_nav = st.radio(
        "Navigation Menu",
        nav_options,
        index=current_index,
        key="sidebar_radio_nav",
        on_change=_on_nav_change,
        label_visibility="collapsed"
    )
    
    st.session_state["nav_selection"] = selected_nav
    page = selected_nav.split(" ", 1)[1]

    st.markdown("---")
    st.markdown("""
    <div style="padding: 6px 4px; text-align: center; color: rgba(255,255,255,0.75); font-size: 0.72rem; line-height: 1.5;">
        <b style="color:#F3E5C8;">Ramnarain Ruia Autonomous College</b><br>
        <i>Matunga East, Mumbai · Estd. 1937</i><br>
        <span style="display:inline-block; margin-top:4px; color:#4ADE80; font-weight:700;">● MySQL (Ruia-Buddy) Connected</span>
    </div>
    """, unsafe_allow_html=True)

# Main Screen Routing & Identification
if st.session_state.student is None and page != "Welcome":
    # Collegiate Student Onboarding Portal
    st.markdown("""
    <div class="admission-card">
        <div class="admission-card-header">
            <div class="hero-pill" style="margin-bottom: 8px;">Official Ruia Student Portal</div>
            <h2 style="margin: 6px 0 8px 0; color: #6B0F1A !important;">Student Identification & Database Sign-In</h2>
            <p style="color: #52525B; font-size: 0.95rem; margin:0;">
                Connect your academic profile to unlock personalized AI planning, assignment deadlines, and exam schedules stored in MySQL.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    c_left, c_center, c_right = st.columns([1, 2.6, 1])
    with c_center:
        login_tab1, login_tab2, login_tab3 = st.tabs([
            "🔑 Select Existing Profile",
            "📝 Register New Student",
            "⚡ 1-Click Quick Demo"
        ])

        with login_tab1:
            st.markdown("#### Access Saved Profile from Database")
            try:
                registered_students = get_all_students()
                if registered_students:
                    options_map = {
                        f"{s['name']} — {s['program']} (Yr {s['year']}) · {s['email']}": s 
                        for s in registered_students
                    }
                    selected_label = st.selectbox("Select Student Profile", list(options_map.keys()))
                    if st.button("Log In with Selected Profile", type="primary", use_container_width=True):
                        st.session_state.student = options_map[selected_label]
                        st.session_state["nav_selection"] = "📊 Academic Dashboard"
                        st.toast(f"Welcome back, {st.session_state.student['name']}!")
                        st.rerun()
                else:
                    st.info("No registered students found in database. Please register below or use a quick demo profile.")
            except Exception as exc:
                st.error(f"Error accessing database: {exc}")

        with login_tab2:
            st.markdown("#### Register New Ruia Scholar")
            with st.form("new_student_form"):
                new_name = st.text_input("Full Name", placeholder="e.g. Tanvi Kulkarni")
                new_email = st.text_input("College Email", placeholder="e.g. tanvi.kulkarni@ruiacollege.edu")
                
                ruia_departments = [
                    "B.Sc. Computer Science (Autonomous · NEP 2020)",
                    "B.Sc. Information Technology & Cloud Systems",
                    "B.Sc. Data Science & Big Data Analytics",
                    "B.Sc. Bioanalytical Sciences & Instrumentation",
                    "B.Sc. Biotechnology & Molecular Genetics",
                    "B.Sc. Chemistry (Analytical & Organic)",
                    "B.Sc. Physics & Applied Electronics",
                    "B.A. Economics (Autonomous · NEP 2020)",
                    "B.A. English Literature & Communication",
                    "B.Com. Financial Markets & Accounting",
                    "M.Sc. Computer Science & AI"
                ]
                new_program = st.selectbox("Academic Department / Programme", ruia_departments)
                new_year = st.selectbox("Academic Year", [1, 2, 3, 4, 5], format_func=lambda y: f"Year {y} ({'FY' if y==1 else 'SY' if y==2 else 'TY' if y==3 else 'Postgraduate'})")
                
                reg_submit = st.form_submit_button("Save to MySQL & Enter Companion", use_container_width=True)
                
                if reg_submit:
                    if not new_name.strip() or not new_email.strip():
                        st.warning("Please provide both name and college email.")
                    else:
                        try:
                            saved_student = get_or_create_student(new_name.strip(), new_email.strip(), new_program, new_year)
                            st.session_state.student = saved_student
                            st.session_state["nav_selection"] = "📊 Academic Dashboard"
                            st.success(f"Registered successfully as {new_name}!")
                            st.rerun()
                        except Exception as exc:
                            st.error(f"Failed to record student: {exc}")

        with login_tab3:
            st.markdown("#### Instant Access for Testing")
            d1, d2 = st.columns(2)
            with d1:
                if st.button("👤 Aarav Sharma (TY B.Sc. CS)", use_container_width=True):
                    st.session_state.student = get_or_create_student("Aarav Sharma", "aarav.sharma@ruiacollege.edu", "B.Sc. Computer Science (Autonomous)", 3)
                    st.session_state["nav_selection"] = "📊 Academic Dashboard"
                    st.rerun()
            with d2:
                if st.button("👤 Ananya Deshmukh (SY B.A. Economics)", use_container_width=True):
                    st.session_state.student = get_or_create_student("Ananya Deshmukh", "ananya.deshmukh@ruiacollege.edu", "B.A. Economics (Autonomous)", 2)
                    st.session_state["nav_selection"] = "📊 Academic Dashboard"
                    st.rerun()

elif page == "Welcome":
    home.render()
elif page == "Academic Dashboard":
    dashboard.render(st.session_state.student)
elif page == "Study Planner":
    planner.render(st.session_state.student)
elif page == "Assignment Desk":
    assignments.render(st.session_state.student)
elif page == "Resume Lab":
    resume.render(st.session_state.student)
elif page == "Quiz Studio":
    quiz.render(st.session_state.student)
elif page == "Exam Map":
    exams.render(st.session_state.student)
