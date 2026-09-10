import os
import base64
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv
from frontend import home, dashboard, planner, assignments, resume, quiz, exams
from backend.db import get_or_create_student, seed_default_courses

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

# Helper for logo data URI
def get_logo_data_uri():
    logo_path = Path("assets/logo.png")
    if not logo_path.exists():
        logo_path = Path("assets/logo.jpg")
    if logo_path.exists():
        data = logo_path.read_bytes()
        return f"data:image/png;base64,{base64.b64encode(data).decode()}"
    return None

logo_uri = get_logo_data_uri()

# Initialize session state
if "student" not in st.session_state:
    st.session_state.student = None

# Pre-seed default Ruia courses
try:
    seed_default_courses()
except Exception:
    pass

# Sidebar Rendering
with st.sidebar:
    if logo_uri:
        st.markdown(f"""
        <div class="sidebar-brand-card">
            <img src="{logo_uri}" alt="Ruia College Logo">
            <div class="sidebar-brand-sub">Autonomous · Mumbai</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align:center; padding: 12px 0 20px 0;">
            <h2 style="color:#FFF !important; margin:0; font-family:'Playfair Display', serif;">RUIA <span style="color:#C9A86A;">AI</span></h2>
            <div style="color:#E5C383; font-size:0.75rem; letter-spacing:0.15em; font-weight:700;">STUDENT COMPANION</div>
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
        if st.button("↻ Switch Profile", use_container_width=True):
            st.session_state.student = None
            st.rerun()
        st.markdown("<div style='margin-bottom:12px;'></div>", unsafe_allow_html=True)

    # Navigation menu
    nav_options = [
        "🏛️ Welcome",
        "📊 Academic Dashboard",
        "📅 Study Planner",
        "📝 Assignment Desk",
        "📑 Resume Lab",
        "🎯 Quiz Studio",
        "⏱️ Exam Map"
    ]
    
    selected_nav = st.radio(
        "Navigation",
        nav_options,
        index=0,
        label_visibility="collapsed"
    )
    
    page = selected_nav.split(" ", 1)[1]

    st.markdown("---")
    st.markdown("""
    <div style="padding: 10px 4px; text-align: center; color: rgba(255,255,255,0.7); font-size: 0.72rem; line-height: 1.5;">
        <b style="color:#F3E5C8;">Ramnarain Ruia Autonomous College</b><br>
        <i>Matunga East, Mumbai · Estd. 1937</i><br>
        <span style="display:inline-block; margin-top:6px; color:#4ADE80;">● MySQL & AI Active</span>
    </div>
    """, unsafe_allow_html=True)

# Main Screen Routing
if st.session_state.student is None and page != "Welcome":
    # Collegiate Student Onboarding Card
    st.markdown(f"""
    <div class="admission-card">
        <div class="admission-card-header">
            {f'<img src="{logo_uri}" class="admission-logo-img" alt="Ruia Logo">' if logo_uri else ''}
            <div class="hero-pill" style="margin-bottom: 8px;">Official Student Portal</div>
            <h2 style="margin: 6px 0 8px 0; color: #6B0F1A !important;">Student Identification</h2>
            <p style="color: #52525B; font-size: 0.95rem; margin:0;">
                Connect your academic profile to unlock personalized AI planning, deadline reminders, and exam schedules.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    demo_col1, demo_col2, demo_col3 = st.columns([1, 1.8, 1])
    with demo_col2:
        if st.button("⚡ Quick Test with Demo Student Profile", use_container_width=True):
            try:
                demo_student = get_or_create_student(
                    name="Aarav Sharma",
                    email="aarav.sharma@ruiacollege.edu",
                    program="B.Sc. Computer Science (Autonomous)",
                    year=3
                )
                st.session_state.student = demo_student
                st.success("Welcome, Aarav! Profile established.")
                st.rerun()
            except Exception as exc:
                st.error(f"Could not initialize demo profile: {exc}")

        st.markdown("<div style='text-align:center; color:#A1A1AA; font-size:0.85rem; margin:14px 0;'>— or create / log into your profile below —</div>", unsafe_allow_html=True)

        with st.form("student_profile_form"):
            name = st.text_input("Full Name", placeholder="e.g. Ananya Deshmukh")
            email = st.text_input("College Email", placeholder="e.g. ananya.deshmukh@ruiacollege.edu")
            
            programs = [
                "B.Sc. Computer Science (Autonomous)",
                "B.Sc. Information Technology",
                "B.Sc. Data Science & Analytics",
                "B.Sc. Biotechnology",
                "B.Sc. Chemistry (Analytical / Organic)",
                "B.A. Economics",
                "B.A. English Literature & Communication",
                "B.Com. Financial Markets & Accounting",
                "M.Sc. Computer Science / AI"
            ]
            program = st.selectbox("Academic Programme", programs)
            year = st.selectbox("Academic Year", [1, 2, 3, 4, 5], format_func=lambda y: f"Year {y} (FY/SY/TY/Postgrad)")
            
            submit = st.form_submit_button("Enter Ruia Companion", use_container_width=True)
            
            if submit:
                if not name.strip() or not email.strip():
                    st.warning("Please provide your full name and valid college email.")
                else:
                    try:
                        student = get_or_create_student(name.strip(), email.strip(), program, year)
                        st.session_state.student = student
                        st.success(f"Welcome to Ruia AI Companion, {name.split()[0]}!")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Database connection issue: {exc}. Please verify MySQL settings in .env.")

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
