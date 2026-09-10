import os
import base64
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv
from frontend import home, dashboard, planner, assignments, resume, quiz, exams
from frontend.footer import render_footer
from backend.db import get_or_create_student, get_all_students, seed_default_data
from backend.ai import is_gemini_configured, get_active_api_key, save_api_key_to_env, test_gemini_connection

load_dotenv()

st.set_page_config(
    page_title="RUI — The Ruia Student Buddy | Ramnarain Ruia Autonomous College",
    page_icon="assets/logo.png" if Path("assets/logo.png").exists() else "🏛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load CSS
css_path = Path("assets/styles.css")
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

# Pre-seed default Ruia courses & students in MySQL (cached per session)
if "db_seeded" not in st.session_state:
    try:
        seed_default_data()
        st.session_state["db_seeded"] = True
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

# Encode Logo for Top Navigation
logo_file = Path("assets/logo.png")
if not logo_file.exists():
    logo_file = Path("assets/logo.jpg")

logo_b64 = ""
if logo_file.exists():
    logo_b64 = f"data:image/png;base64,{base64.b64encode(logo_file.read_bytes()).decode()}"

# Active Intelligence Data
active_key = get_active_api_key()
active_model = st.session_state.get("active_gemini_model") or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# ==============================================================================
# STYLISH RED TOP BRAND NAVBAR
# ==============================================================================
logo_tag = f'<img src="{logo_b64}" class="rui-brand-logo" alt="Ruia Emblem">' if logo_b64 else '<span style="font-size:1.8rem;">🏛️</span>'

if st.session_state.student:
    student = st.session_state.student
    initials = "".join([p[0] for p in student['name'].split()][:2]).upper() or "RC"
    short_name = student['name'].split()[0]
    student_chip_html = f'<div class="rui-student-chip" title="{student["name"]} ({student["program"]})"><div class="rui-student-avatar">{initials}</div><div class="rui-student-name">{short_name} · Yr {student["year"]}</div></div>'
else:
    student_chip_html = '<div class="rui-student-chip" style="background:rgba(255,255,255,0.18); border:1px solid rgba(255,255,255,0.35);"><span style="font-size:0.8rem; font-weight:700; color:#FFFFFF;">Scholars Portal</span></div>'

if active_key:
    ai_badge_html = f'<div class="rui-ai-badge" title="RUI Generative AI active ({active_model})"><span class="rui-ai-pulse"></span><span>RUI AI Active</span></div>'
else:
    ai_badge_html = '<div style="display:inline-flex; align-items:center; gap:6px; background:rgba(245,158,11,0.28); border:1px solid rgba(251,191,36,0.6); color:#FDE68A; font-size:0.75rem; font-weight:700; padding:5px 12px; border-radius:9999px;"><span>●</span><span>Curriculum Mode</span></div>'

navbar_html = f"""<div class="rui-top-navbar">
<div class="rui-brand-box">
{logo_tag}
<div class="rui-brand-text">
<div class="rui-brand-title">RUI <span class="rui-brand-tag">Student Buddy</span></div>
<div class="rui-brand-subtitle">Ramnarain Ruia Autonomous College · Matunga East, Mumbai (Estd. 1937)</div>
</div>
</div>
<div style="display:flex; align-items:center; gap:12px; flex-wrap:wrap;">
{student_chip_html}
{ai_badge_html}
</div>
</div>"""

st.html(navbar_html)

def navigate_to(target):
    st.session_state["nav_selection"] = target
    st.rerun()

if "nav_selection" not in st.session_state:
    st.session_state["nav_selection"] = "🏛️ Welcome"

# Extract current page identifier
raw_nav = st.session_state["nav_selection"]
page = raw_nav.split(" ", 1)[1] if " " in raw_nav else raw_nav

# ==============================================================================
# UNIFIED HORIZONTAL TOP NAVIGATION MENU (ZERO BLACK BOX, HIGH-CONTRAST)
# ==============================================================================
nav_items = [
    ("🏛️ Welcome", "Welcome"),
    ("📊 Dashboard", "Academic Dashboard"),
    ("📅 Study Planner", "Study Planner"),
    ("📝 Assignments", "Assignment Desk"),
    ("📑 Resume Lab", "Resume Lab"),
    ("🎯 Quiz Studio", "Quiz Studio"),
    ("⏱️ Exam Map", "Exam Map"),
]

nav_cols = st.columns(7, gap="small")
for col, (label, target_page) in zip(nav_cols, nav_items):
    is_active = (page == target_page)
    with col:
        if st.button(
            label,
            key=f"topnav_{target_page.replace(' ', '_')}",
            type="primary" if is_active else "secondary",
            use_container_width=True
        ):
            if page != target_page:
                navigate_to(f"📌 {target_page}" if target_page != "Welcome" else "🏛️ Welcome")


# Subtle Context & Account Bar
c_bar_l, c_bar_r = st.columns([3.8, 1.2], vertical_alignment="center")
with c_bar_l:
    if st.session_state.student:
        stu = st.session_state.student
        st.html(f'<div style="font-size:0.84rem; color:#475569; padding:4px 2px;">🎓 Ruia Scholar: <b style="color:#701A24;">{stu["name"]}</b> · <i>{stu["program"]}</i> (Year {stu["year"]}) · MySQL <code>Ruia-Buddy</code> Synced</div>')
    else:
        st.html('<div style="font-size:0.84rem; color:#64748B; padding:4px 2px;">👋 Welcome, Ruia Scholar! Sign in to sync your study timetables, assignment reminders, and exam schedules.</div>')

with c_bar_r:
    if st.session_state.student:
        if st.button("↻ Switch Student", key="top_switch_student_btn", use_container_width=True):
            st.session_state.student = None
            navigate_to("🏛️ Welcome")
    else:
        if st.button("🔑 Student Sign-In", key="top_btn_signin_fast", use_container_width=True):
            navigate_to("📊 Academic Dashboard")


# Optional AI & System Configuration Panel
with st.expander("⚙️ RUI AI Companion Configuration & Gemini Key", expanded=False):
    col_ai_info, col_ai_form = st.columns([1.2, 1.8], gap="large")
    with col_ai_info:
        st.html(f'<h4 style="margin:0 0 6px 0; color:#701A24;">RUI Intelligence System</h4><p style="font-size:0.88rem; color:#475569; margin:0 0 10px 0;">RUI is the official AI academic buddy for <b>Ramnarain Ruia Autonomous College</b>. Powered by <b>Google Gemini ({active_model})</b>, RUI designs bespoke 7-day study plans, audits resumes against placement cell standards, and generates topic quizzes.</p><div style="font-size:0.82rem; color:#0F172A; font-weight:600;">Database: <span style="color:#059669;">● MySQL Connected (Ruia-Buddy)</span></div>')
        if active_key:
            masked = f"{active_key[:6]}...{active_key[-4:]}"
            st.html(f'<div style="font-size:0.78rem; color:#64748B; margin-top:6px;">Active API Key: <code>{masked}</code></div>')
    with col_ai_form:
        new_key_input = st.text_input(
            "Enter / Update Gemini API Key",
            type="password",
            placeholder="AIzaSy...",
            key="input_gemini_key_header",
            help="Get a free key directly from https://aistudio.google.com/app/apikey"
        )
        if st.button("Connect & Test API Key", key="btn_save_gemini_header", use_container_width=True):
            if not new_key_input.strip():
                st.warning("Please enter an API key.")
            else:
                with st.spinner("Verifying with Google Gemini..."):
                    res = test_gemini_connection(new_key_input)
                    if isinstance(res, tuple) and len(res) == 3:
                        is_valid, model_name, msg = res
                    elif isinstance(res, tuple) and len(res) == 2:
                        is_valid, msg = res
                        model_name = "gemini-2.5-flash"
                    else:
                        is_valid, model_name, msg = False, None, str(res)

                    if is_valid:
                        chosen_model = model_name or "gemini-2.5-flash"
                        save_api_key_to_env(new_key_input, chosen_model)
                        st.session_state["custom_gemini_api_key"] = new_key_input.strip()
                        st.session_state["active_gemini_model"] = chosen_model
                        st.toast(f"RUI AI connected with {chosen_model}! 🎉")
                        st.rerun()
                    else:
                        st.error(f"Verification failed: {msg}")

st.html("<div style='margin-bottom: 22px;'></div>")

# ==============================================================================
# SIDEBAR DRAWER (OPTIONAL DIAGNOSTIC DRAWER)
# ==============================================================================
with st.sidebar:
    st.markdown("### 🏛️ RUI Diagnostics & Portal Info")
    if logo_file.exists():
        st.image(str(logo_file), use_container_width=True)
    st.html("""<div style="font-size:0.82rem; color:#475569; line-height:1.5; margin:10px 0;">
<b>Ramnarain Ruia Autonomous College</b><br>
<i>Matunga East, Mumbai · Estd. 1937</i><br>
NAAC 'A+' Grade (CGPA 3.70 / 4.0)<br>
Affiliated with University of Mumbai
</div>
<hr style="margin:12px 0;">
<div style="font-size:0.78rem; color:#0F172A;">
<b>System Status:</b><br>
● MySQL (Ruia-Buddy): <span style="color:#059669; font-weight:700;">Online</span><br>
● Top Navigation: <span style="color:#059669; font-weight:700;">Active</span><br>
● Academic Engine: <span style="color:#059669; font-weight:700;">Autonomous NEP 2020</span>
</div>""")

# ==============================================================================
# MAIN PAGE ROUTING & STUDENT AUTHENTICATION
# ==============================================================================
if st.session_state.student is None and page != "Welcome":
    st.html("""<div class="admission-card">
<div class="admission-card-header">
<div class="hero-pill" style="margin-bottom: 8px;">Official Ruia Student Portal</div>
<h2 style="margin: 6px 0 8px 0; color: #701A24 !important;">Meet RUI — Student Sign-In & Verification</h2>
<p style="color: #475569; font-size: 0.98rem; margin:0;">
Connect your academic profile to unlock personalized AI planning, assignment deadlines, and exam schedules stored in your <b>Ruia-Buddy</b> database.
</p>
</div>
</div>""")

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
                        st.toast(f"Welcome back, {st.session_state.student['name']}!")
                        navigate_to("📊 Academic Dashboard")
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
                
                reg_submit = st.form_submit_button("Save to MySQL & Enter RUI Companion", use_container_width=True)
                
                if reg_submit:
                    if not new_name.strip() or not new_email.strip():
                        st.warning("Please provide both name and college email.")
                    else:
                        try:
                            saved_student = get_or_create_student(new_name.strip(), new_email.strip(), new_program, new_year)
                            st.session_state.student = saved_student
                            st.success(f"Registered successfully as {new_name}!")
                            navigate_to("📊 Academic Dashboard")
                        except Exception as exc:
                            st.error(f"Failed to record student: {exc}")

        with login_tab3:
            st.markdown("#### Instant Access for Testing")
            d1, d2 = st.columns(2)
            with d1:
                if st.button("👤 Aarav Sharma (TY B.Sc. CS)", use_container_width=True):
                    st.session_state.student = get_or_create_student("Aarav Sharma", "aarav.sharma@ruiacollege.edu", "B.Sc. Computer Science (Autonomous)", 3)
                    navigate_to("📊 Academic Dashboard")
            with d2:
                if st.button("👤 Ananya Deshmukh (SY B.A. Economics)", use_container_width=True):
                    st.session_state.student = get_or_create_student("Ananya Deshmukh", "ananya.deshmukh@ruiacollege.edu", "B.A. Economics (Autonomous)", 2)
                    navigate_to("📊 Academic Dashboard")


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

# ==============================================================================
# MASTER DEDICATED RUI FOOTER (ON ALL PAGES)
# ==============================================================================
render_footer()
