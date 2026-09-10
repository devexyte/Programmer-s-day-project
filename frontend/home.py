import base64
from pathlib import Path
import streamlit as st

def _navigate(target):
    st.session_state["nav_goto"] = target
    st.rerun()

def render():
    logo_path = Path("assets/logo.png")
    if not logo_path.exists():
        logo_path = Path("assets/logo.jpg")

    logo_b64 = ""
    if logo_path.exists():
        logo_b64 = f"data:image/png;base64,{base64.b64encode(logo_path.read_bytes()).decode()}"

    # Hero Banner
    hero_col, img_col = st.columns([2.3, 1], gap="large")
    
    with hero_col:
        st.html("""<div class="hero">
<div class="hero-content">
<div class="hero-pill">
<span>⭐</span>
<span>Official Companion · Ramnarain Ruia Autonomous College</span>
</div>
<h1>Meet <em>RUI</em> — Your Ruia Student Buddy.</h1>
<p class="lead">
An intelligent academic companion crafted specifically for Ruia College scholars. RUI synthesizes syllabus-aligned 7-day study timetables, milestone assignment roadmaps, placement cell resume audits, and examination strategies.
</p>
</div>
</div>""")

    with img_col:
        logo_img_tag = f'<img src="{logo_b64}" style="max-width:120px; height:auto; border-radius:8px; filter:drop-shadow(0 4px 8px rgba(0,0,0,0.08));">' if logo_b64 else ''
        st.html(f"""<div class="hero-emblem-card">
{logo_img_tag}
<div style="font-family:'Playfair Display', serif; font-size:1.1rem; font-weight:700; color:#701A24; margin-top:10px;">Ramnarain Ruia College</div>
<div style="font-size:0.75rem; font-weight:800; color:#C5A059; letter-spacing:0.08em; text-transform:uppercase;">Autonomous · Estd. 1937</div>
<div style="font-size:0.75rem; color:#475569; margin-top:4px; font-style:italic;">Explore · Experience · Excel</div>
<div style="margin-top:10px; background:#F8FAFC; border:1px solid #E2E8F0; padding:4px 10px; border-radius:999px; font-size:0.72rem; font-weight:700; color:#0F172A;">
NAAC 'A+' · CGPA 3.70/4.0
</div>
</div>""")

    st.html("<div style='margin-bottom: 20px;'></div>")

    # Hero Quick-Action Row
    c_act1, c_act2, c_act3 = st.columns(3)
    with c_act1:
        if st.button("📊 Open Academic Dashboard", use_container_width=True, type="primary"):
            _navigate("📊 Academic Dashboard")
    with c_act2:
        if st.button("📅 Build 7-Day Study Plan with RUI", use_container_width=True):
            _navigate("📅 Study Planner")
    with c_act3:
        if st.button("🎯 Practice in Quiz Studio", use_container_width=True):
            _navigate("🎯 Quiz Studio")

    st.html("<div style='margin-bottom: 28px;'></div>")

    # Academic Prestige Stats Strip
    st.html("""<div class="ruia-stats-strip">
<div class="stat-pill">
<div class="stat-pill-num">Autonomous</div>
<div class="stat-pill-label">Affiliated with University of Mumbai</div>
</div>
<div class="stat-pill">
<div class="stat-pill-num">NAAC 'A+'</div>
<div class="stat-pill-label">CGPA 3.70 / 4.0 · Star College Status</div>
</div>
<div class="stat-pill">
<div class="stat-pill-num">Estd. 1937</div>
<div class="stat-pill-label">87+ Years of Academic Heritage</div>
</div>
<div class="stat-pill">
<div class="stat-pill-num">NEP 2020</div>
<div class="stat-pill-label">DSC · DSE · SEC · AEC Curriculum</div>
</div>
</div>""")

    # Five Horizons Section with RUI branding & navigation
    st.html('<div class="section-kicker">MEET RUI · FIVE ACADEMIC PILLARS</div>')
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.html("""<div class="feature-card">
<div class="feature-icon-box">📅</div>
<h3>Study Planner</h3>
<p>7-day timetables aligned with official Ruia Autonomous departments, difficult courses, and focus blocks.</p>
</div>""")
        if st.button("Launch Planner →", key="home_btn_planner", use_container_width=True):
            _navigate("📅 Study Planner")

    with col2:
        st.html("""<div class="feature-card">
<div class="feature-icon-box">⏳</div>
<h3>Reminders</h3>
<p>Staged milestone roadmaps from research to final submission, preventing deadline emergencies.</p>
</div>""")
        if st.button("Open Desk →", key="home_btn_assignments", use_container_width=True):
            _navigate("📝 Assignment Desk")

    with col3:
        st.html("""<div class="feature-card">
<div class="feature-icon-box">📑</div>
<h3>Resume Lab</h3>
<p>Placement cell diagnostics, STAR-method quantification, and ATS-optimized markdown export.</p>
</div>""")
        if st.button("Review Resume →", key="home_btn_resume", use_container_width=True):
            _navigate("📑 Resume Lab")

    with col4:
        st.html("""<div class="feature-card">
<div class="feature-icon-box">🎯</div>
<h3>Quiz Studio</h3>
<p>Curated practice sets from syllabus lecture units with interactive answer reveals and rationale.</p>
</div>""")
        if st.button("Start Quiz →", key="home_btn_quiz", use_container_width=True):
            _navigate("🎯 Quiz Studio")

    with col5:
        st.html("""<div class="feature-card">
<div class="feature-icon-box">⏱️</div>
<h3>Exam Map</h3>
<p>Paper venues, countdown clocks, and reverse-engineered spaced repetition revision master schedules.</p>
</div>""")
        if st.button("Open Exam Map →", key="home_btn_exams", use_container_width=True):
            _navigate("⏱️ Exam Map")

    st.html("<div style='margin-bottom: 24px;'></div>")

    # Collegiate Values Card
    st.html("""<div class="ruia-quote-box">
“Education is not preparation for life; education is life itself.”
<div class="ruia-quote-author">— John Dewey · Honoured in the Halls of Ramnarain Ruia Autonomous College</div>
</div>""")
