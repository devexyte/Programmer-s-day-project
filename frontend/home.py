from pathlib import Path
import streamlit as st

def render():
    logo_path = Path("assets/logo.png")
    if not logo_path.exists():
        logo_path = Path("assets/logo.jpg")

    # Hero Banner
    hero_col, img_col = st.columns([2.2, 1], gap="large")
    
    with hero_col:
        st.markdown("""
        <div class="hero" style="margin-bottom:0; min-height: 280px; padding: 36px 36px;">
            <div class="hero-content">
                <div class="hero-pill">Ramnarain Ruia Autonomous College · Mumbai</div>
                <h1 style="font-size: 2.8rem !important;">Your academic life,<br><em>beautifully in rhythm.</em></h1>
                <p class="lead" style="font-size: 1.05rem; margin-bottom: 16px;">
                    An official digital companion designed for Ruia scholars. Synthesize weekly study schedules, multi-stage assignment milestones, placement cell resume audits, and examination strategy.
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with img_col:
        st.markdown("""
        <div class="sidebar-brand-card" style="margin-top:0; padding: 20px 16px; border: 2.5px solid #C9A86A; height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center;">
        """, unsafe_allow_html=True)
        if logo_path.exists():
            st.image(str(logo_path), use_container_width=True)
        st.markdown("""
            <div style="font-family:'Playfair Display', serif; font-size:1.05rem; font-weight:700; color:#6B0F1A; margin-top:10px;">Ramnarain Ruia College</div>
            <div style="font-size:0.75rem; font-weight:800; color:#C9A86A; letter-spacing:0.1em; text-transform:uppercase;">Autonomous · Estd. 1937</div>
            <div style="font-size:0.72rem; color:#52525B; margin-top:4px; font-style:italic;">Explore · Experience · Excel</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

    # Hero Quick-Action Row
    c_act1, c_act2, c_act3 = st.columns(3)
    with c_act1:
        if st.button("📊 Open Academic Dashboard", use_container_width=True, type="primary"):
            st.session_state["nav_selection"] = "📊 Academic Dashboard"
            st.rerun()
    with c_act2:
        if st.button("📅 Build 7-Day Study Plan", use_container_width=True):
            st.session_state["nav_selection"] = "📅 Study Planner"
            st.rerun()
    with c_act3:
        if st.button("🎯 Practice in Quiz Studio", use_container_width=True):
            st.session_state["nav_selection"] = "🎯 Quiz Studio"
            st.rerun()

    st.markdown("<div style='margin-bottom: 28px;'></div>", unsafe_allow_html=True)

    # Academic Prestige Stats Strip
    st.markdown("""
    <div class="ruia-stats-strip">
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
    </div>
    """, unsafe_allow_html=True)

    # Five Horizons Section with INTERACTIVE NAVIGATION BUTTONS
    st.markdown('<div class="section-kicker">ONE COMPANION · FIVE ACADEMIC PILLARS</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon-box">📅</div>
            <h3>Study Planner</h3>
            <p>7-day timetables aligned with official Ruia Autonomous departments, difficult courses, and focus blocks.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Launch Planner →", key="home_btn_planner", use_container_width=True):
            st.session_state["nav_selection"] = "📅 Study Planner"
            st.rerun()

    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon-box">⏳</div>
            <h3>Reminders</h3>
            <p>Staged milestone roadmaps from research to final submission, preventing deadline emergencies.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open Desk →", key="home_btn_assignments", use_container_width=True):
            st.session_state["nav_selection"] = "📝 Assignment Desk"
            st.rerun()

    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon-box">📑</div>
            <h3>Resume Lab</h3>
            <p>Placement cell diagnostics, STAR-method quantification, and ATS-optimized markdown export.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Review Resume →", key="home_btn_resume", use_container_width=True):
            st.session_state["nav_selection"] = "📑 Resume Lab"
            st.rerun()

    with col4:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon-box">🎯</div>
            <h3>Quiz Studio</h3>
            <p>Curated practice sets from syllabus lecture units with interactive answer reveals and rationale.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start Quiz →", key="home_btn_quiz", use_container_width=True):
            st.session_state["nav_selection"] = "🎯 Quiz Studio"
            st.rerun()

    with col5:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon-box">⏱️</div>
            <h3>Exam Map</h3>
            <p>Paper venues, countdown clocks, and reverse-engineered spaced repetition revision master schedules.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open Exam Map →", key="home_btn_exams", use_container_width=True):
            st.session_state["nav_selection"] = "⏱️ Exam Map"
            st.rerun()

    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

    # Collegiate Values Card
    st.markdown("""
    <div class="ruia-quote-box">
        “Education is not preparation for life; education is life itself.”
        <div class="ruia-quote-author">— John Dewey · Honoured in the Halls of Ramnarain Ruia Autonomous College</div>
    </div>
    """, unsafe_allow_html=True)

    # Footer
    st.markdown("""
    <div class="ruia-footer">
        <div class="ruia-footer-creds">
            <span>🏛️</span>
            <span>Ramnarain Ruia Autonomous College · Matunga East, Mumbai 400019</span>
        </div>
        <div>
            <span>Official Student AI Companion · Powered by MySQL & Gemini</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
