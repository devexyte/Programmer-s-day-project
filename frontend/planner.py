import streamlit as st
from backend.planner_logic import create_plan, get_latest_plan

def render(student):
    if not student:
        st.info("Please set up or select your student profile.")
        return

    st.markdown("""
    <div style="margin-bottom: 20px;">
        <div class="section-kicker">PERSONALIZED AI STUDY PLANNER</div>
        <h1 style="margin: 0 0 6px 0;">Design Your Weekly Academic Rhythm</h1>
        <p style="color: #64748B; font-size: 1.05rem; margin: 0;">
            Harmonize challenging autonomous coursework, deep-work focus blocks, and active recall.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col_form, col_output = st.columns([1, 1.3], gap="large")

    with col_form:
        st.markdown("### 📋 Plan Parameters")
        
        # Quick template loaders
        st.markdown("<small style='color:#71717A; font-weight:600;'>QUICK SYLLABUS PRESETS:</small>", unsafe_allow_html=True)
        t1, t2, t3 = st.columns(3)
        preset_text = ""
        if t1.button("💻 Science / CS", use_container_width=True):
            st.session_state["planner_subjects"] = "Data Structures & Algorithms — High\nApplied Statistics & Probability — High\nDatabase Systems — Medium\nTechnical Communication — Low"
        if t2.button("🧬 Biotech / Chem", use_container_width=True):
            st.session_state["planner_subjects"] = "Molecular Genetics & Genomics — High\nOrganic Spectroscopy — High\nCell Biology Fundamentals — Medium\nBioinformatics Lab — Medium"
        if t3.button("📊 Economics / Arts", use_container_width=True):
            st.session_state["planner_subjects"] = "Macroeconomic Policy — High\nEconometrics & R Programming — High\nPublic Finance — Medium\nIndian Economic History — Low"

        default_subjects = st.session_state.get(
            "planner_subjects",
            "Artificial Intelligence & Machine Learning — High\nAdvanced Database Systems — Medium\nOperating Systems & Unix — High"
        )

        with st.form("study_plan_form"):
            subjects = st.text_area(
                "Coursework Modules & Difficulty Level",
                value=default_subjects,
                height=150,
                placeholder="Subject 1 — High\nSubject 2 — Medium\nSubject 3 — Low"
            )
            hours = st.slider("Target Focused Study Hours Per Day", min_value=1, max_value=12, value=4, step=1)
            exams = st.text_input("Upcoming Exam Horizons (optional)", placeholder="e.g. Mid-Term Papers starting Oct 15")
            
            submit = st.form_submit_button("✦ Compose 7-Day Ruia Study Plan", use_container_width=True)

        if submit:
            if not subjects.strip():
                st.warning("Please specify at least one subject with difficulty.")
            else:
                with st.spinner("Ruia AI is synthesizing your optimal timetable..."):
                    try:
                        plan = create_plan(student['student_id'], subjects.strip(), hours, exams.strip())
                        st.session_state["current_plan"] = plan
                        st.success("Study plan crafted and saved to your Ruia profile!")
                    except Exception as exc:
                        st.error(f"Error generating study plan: {exc}")

    with col_output:
        st.markdown("### 🏛️ 7-Day Study Timetable")
        
        current_plan = st.session_state.get("current_plan")
        if not current_plan:
            # Check if there is an existing plan in DB
            db_plan = get_latest_plan(student['student_id'])
            if db_plan:
                current_plan = db_plan['generated_plan']

        if current_plan:
            st.markdown(current_plan, unsafe_allow_html=True)
            st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)
            st.download_button(
                "📥 Download Study Plan (.md)",
                data=current_plan,
                file_name="ruia_weekly_study_plan.md",
                mime="text/markdown",
                use_container_width=True
            )
        else:
            st.markdown("""
            <div style="background:#FFF; border:1px dashed #DACDBB; border-radius:14px; padding:48px 24px; text-align:center; color:#71717A;">
                <div style="font-size:2.4rem; margin-bottom:12px;">📅</div>
                <h4 style="margin:0 0 6px 0; color:#6B0F1A !important;">Your Timetable Canvas is Empty</h4>
                <p style="font-size:0.92rem; max-width:380px; margin:0 auto;">
                    Fill in your subjects on the left or select a quick syllabus preset, then click <b>Compose 7-Day Ruia Study Plan</b>.
                </p>
            </div>
            """, unsafe_allow_html=True)
