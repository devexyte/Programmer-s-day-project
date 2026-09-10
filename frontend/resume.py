import streamlit as st
from backend.resume_logic import review_resume

def render(student):
    if not student:
        st.info("Please set up or select your student profile.")
        return

    st.markdown("""
    <div style="margin-bottom: 20px;">
        <div class="section-kicker">CAREER ADVISORY & PLACEMENT CELL</div>
        <h1 style="margin: 0 0 6px 0;">Resume Lab & Placement Diagnostics</h1>
        <p style="color: #64748B; font-size: 1.05rem; margin: 0;">
            Elevate your academic credentials, technical projects, and leadership roles into an ATS-optimized, high-impact resume.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 1.25], gap="large")

    with col_left:
        st.markdown("### 📄 Resume Input")
        
        target_role = st.selectbox(
            "Target Industry / Placement Domain",
            [
                "Software Engineering & Full-Stack Development",
                "Data Science & Machine Learning Intern",
                "Quantitative Finance & Market Research",
                "Academic Research & Fellowship Applications",
                "Biotechnology & Pharmaceutical Analysis",
                "Business Analytics & Corporate Consulting"
            ]
        )

        sample_btn = st.button("⚡ Load Ruia Student Sample Resume", use_container_width=True)
        
        sample_resume_content = """Aarav Sharma
Matunga East, Mumbai | aarav.sharma@ruiacollege.edu | +91 98765 43210
LinkedIn: linkedin.com/in/aarav-sharma | GitHub: github.com/aarav-sharma

EDUCATION
Ramnarain Ruia Autonomous College, Mumbai
B.Sc. in Computer Science (Autonomous) | 2023 - 2026
CGPA: 9.1 / 10.0
Coursework: Data Structures & Algorithms, Database Engineering, AI & Machine Learning, Operating Systems

TECHNICAL SKILLS
- Programming Languages: Python, SQL, C++, JavaScript
- Frameworks & Tools: Streamlit, Flask, MySQL, Git, Docker, Pandas, Scikit-Learn
- Core Competencies: Object-Oriented Design, Agile Development, Relational Schema Architecture

ACADEMIC PROJECTS
Ruia AI Student Companion (Lead Developer) | 2026
- Developed an intelligent collegiate productivity platform with Streamlit, MySQL, and Gemini AI.
- Implemented multi-stage assignment milestone generation and spaced-repetition exam revision algorithms.
- Configured secure parameterized SQL database connections supporting student profiles.

Autonomous College Attendance & Timetable Tracker | 2025
- Built a web portal for real-time lecture tracking reducing manual attendance calculation effort.

LEADERSHIP & ACTIVITIES
- Active Core Member, Ruia College Technical Association (RCTA). Organized 2 inter-college tech fests.
- Volunteer, National Service Scheme (NSS) Ruia Unit."""

        if sample_btn:
            st.session_state["resume_input_text"] = sample_resume_content

        resume_text = st.text_area(
            "Paste Your Resume",
            value=st.session_state.get("resume_input_text", ""),
            height=340,
            placeholder="Paste your education, skills, projects, and work experience here..."
        )

        analyze_btn = st.button("✦ Analyze & Polish with Ruia AI", type="primary", use_container_width=True)

    with col_right:
        st.markdown("### 📑 Diagnostic Report & Polished Resume")

        if analyze_btn:
            if not resume_text.strip():
                st.warning("Please paste or load a resume to begin analysis.")
            else:
                with st.spinner("Placement cell AI is auditing impact, metrics, and ATS compatibility..."):
                    try:
                        review_result = review_resume(resume_text.strip(), target_role)
                        st.session_state["current_resume_review"] = review_result
                    except Exception as exc:
                        st.error(f"Analysis failed: {exc}")

        current_review = st.session_state.get("current_resume_review")
        if current_review:
            st.markdown(current_review, unsafe_allow_html=True)
            st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)
            st.download_button(
                "📥 Download Polished Resume (.md)",
                data=current_review,
                file_name="ruia_polished_resume.md",
                mime="text/markdown",
                use_container_width=True
            )
        else:
            st.markdown("""
            <div style="background:#FFF; border:1px dashed #DACDBB; border-radius:14px; padding:48px 24px; text-align:center; color:#71717A;">
                <div style="font-size:2.4rem; margin-bottom:12px;">📑</div>
                <h4 style="margin:0 0 6px 0; color:#6B0F1A !important;">Awaiting Resume Submission</h4>
                <p style="font-size:0.92rem; max-width:380px; margin:0 auto;">
                    Paste your resume on the left or click <b>Load Ruia Student Sample Resume</b> to generate your placement diagnostic and polished revision.
                </p>
            </div>
            """, unsafe_allow_html=True)
