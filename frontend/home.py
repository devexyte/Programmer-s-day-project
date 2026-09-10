import base64
from pathlib import Path
import streamlit as st

def _get_logo_uri():
    for name in ["logo.png", "logo.jpg"]:
        p = Path("assets") / name
        if p.exists():
            return f"data:image/png;base64,{base64.b64encode(p.read_bytes()).decode()}"
    return None

def render():
    logo_uri = _get_logo_uri()

    # Hero Banner with Official Logo
    st.markdown(f"""
    <div class="hero">
        <div class="hero-content">
            <div class="hero-pill">Ramnarain Ruia Autonomous College · Mumbai</div>
            <h1>Your academic life,<br><em>beautifully in rhythm.</em></h1>
            <p class="lead">
                An intelligent companion designed for Ruia students. Harmonizing weekly study plans, assignment milestones, resume critique, interactive quizzes, and examination strategy.
            </p>
        </div>
        {f'''
        <div class="hero-logo-box">
            <img src="{logo_uri}" alt="Ruia College Emblem">
            <div class="hero-motto">Explore · Experience · Excel</div>
        </div>
        ''' if logo_uri else ''}
    </div>
    """, unsafe_allow_html=True)

    # Prestige Academic Stats Strip
    st.markdown("""
    <div class="ruia-stats-strip">
        <div class="stat-pill">
            <div class="stat-pill-num">Autonomous</div>
            <div class="stat-pill-label">Affiliated with University of Mumbai</div>
        </div>
        <div class="stat-pill">
            <div class="stat-pill-num">NAAC A+</div>
            <div class="stat-pill-label">Grade with 3.70 CGPA</div>
        </div>
        <div class="stat-pill">
            <div class="stat-pill-num">Estd. 1937</div>
            <div class="stat-pill-label">87+ Years of Academic Heritage</div>
        </div>
        <div class="stat-pill">
            <div class="stat-pill-num">Ruia AI</div>
            <div class="stat-pill-label">Powered by Gemini & MySQL</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Five Horizons Section
    st.markdown('<div class="section-kicker">ONE COMPANION · FIVE ACADEMIC PILLARS</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon-box">📅</div>
            <h3>Study Planner</h3>
            <p>Reverse-engineered 7-day schedules factoring in difficulty, study hours, and Pomodoro rest intervals.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon-box">⏳</div>
            <h3>Reminders</h3>
            <p>Staged milestone roadmaps from research to final submission, keeping stress entirely at bay.</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon-box">📑</div>
            <h3>Resume Lab</h3>
            <p>Placement cell diagnostics, STAR-method quantification, and ATS-optimized markdown export.</p>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon-box">🎯</div>
            <h3>Quiz Studio</h3>
            <p>Transform lecture topics into rigorous practice sets with interactive explanations and instant self-tests.</p>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon-box">⏱️</div>
            <h3>Exam Map</h3>
            <p>Countdown clocks, paper venues, and spaced repetition revision calendars tailored to your dates.</p>
        </div>
        """, unsafe_allow_html=True)

    # Collegiate Values Card
    st.markdown("""
    <div class="ruia-quote-box">
        “Education is not preparation for life; education is life itself.”
        <div class="ruia-quote-author">— John Dewey · Honoured in the Halls of Ruia College</div>
    </div>
    """, unsafe_allow_html=True)

    # Footer
    st.markdown("""
    <div class="ruia-footer">
        <div class="ruia-footer-creds">
            <span>🏛️</span>
            <span>Ramnarain Ruia Autonomous College, Matunga East, Mumbai 400019</span>
        </div>
        <div>
            <span>Official Student AI Companion · Version 2.0</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
