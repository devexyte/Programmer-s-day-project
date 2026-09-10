import streamlit as st
from backend.planner_logic import create_plan, get_latest_plan

def render(student):
    if not student:
        st.info("Please set up or select your student profile.")
        return

    st.markdown("""
    <div style="margin-bottom: 20px;">
        <div class="section-kicker">RAMNARAIN RUIA AUTONOMOUS COLLEGE · ACADEMIC CURRICULUM</div>
        <h1 style="margin: 0 0 6px 0;">Official Syllabus Study Planner</h1>
        <p style="color: #64748B; font-size: 1.05rem; margin: 0;">
            Reverse-engineered 7-day study timetables tailored to official Ruia College autonomous departments, NEP 2020 course units (DSC/DSE/SEC), and Continuous Internal Assessments (CIA).
        </p>
    </div>
    """, unsafe_allow_html=True)

    col_form, col_output = st.columns([1, 1.25], gap="large")

    with col_form:
        st.markdown("### 🏛️ Department & Course Selection")

        dept_options = [
            "Department of Computer Science (Autonomous · NEP 2020)",
            "Department of Bioanalytical Sciences & Instrumentation",
            "Department of Biotechnology & Molecular Genetics",
            "Department of Economics (Autonomous · NEP 2020)",
            "Department of Chemistry (Analytical & Organic)",
            "Department of Information Technology & Cloud Systems",
            "Custom Autonomous Department / Programme"
        ]

        selected_dept = st.selectbox("Select Ruia College Department", dept_options)

        # Department-specific official syllabus templates
        dept_presets = {
            "Department of Computer Science (Autonomous · NEP 2020)": (
                "DSC 1: Advanced Data Structures & Algorithm Design — High (Core)\n"
                "DSC 2: Artificial Intelligence & Machine Learning — High (Core)\n"
                "DSE: Cloud Computing & Distributed Systems — Medium (Elective)\n"
                "SEC: Full-Stack Web Development & Streamlit — Medium (Skill)\n"
                "AEC: Academic Research Methodology — Low"
            ),
            "Department of Bioanalytical Sciences & Instrumentation": (
                "DSC 1: Bioanalytical Chromatography & HPLC Techniques — High (Core)\n"
                "DSC 2: Molecular Diagnostics & Mass Spectrometry — High (Core)\n"
                "DSE: Pharmaceutical Quality Assurance & GMP — Medium (Elective)\n"
                "SEC: Computational Bio-Modeling & ChemDraw — Medium (Skill)\n"
                "AEC: Technical Report Writing & Laboratory Safety — Low"
            ),
            "Department of Biotechnology & Molecular Genetics": (
                "DSC 1: Molecular Genetics, Recombinant DNA & CRISPR — High (Core)\n"
                "DSC 2: Immunology & Cell Culture Technology — High (Core)\n"
                "DSE: Environmental Biotechnology & Bioprocess — Medium (Elective)\n"
                "SEC: Python for Biological Data Analysis — Medium (Skill)\n"
                "AEC: Research Ethics & Seminar Presentation — Low"
            ),
            "Department of Economics (Autonomous · NEP 2020)": (
                "DSC 1: Advanced Macroeconomic Policy & Central Banking — High (Core)\n"
                "DSC 2: Econometrics & Time-Series Modeling with R — High (Core)\n"
                "DSE: International Financial Markets & Trade Policy — Medium (Elective)\n"
                "SEC: Data Analytics for Public Economics — Medium (Skill)\n"
                "AEC: Economic Journalism & Policy Debates — Low"
            ),
            "Department of Chemistry (Analytical & Organic)": (
                "DSC 1: Organic Reaction Mechanisms & Stereochemistry — High (Core)\n"
                "DSC 2: Physical Thermodynamics & Quantum Chemistry — High (Core)\n"
                "DSE: Instrumental Methods of Chemical Analysis — Medium (Elective)\n"
                "SEC: Green Chemistry & Waste Minimization — Medium (Skill)\n"
                "AEC: Scientific Documentation & Laboratory Safety — Low"
            ),
            "Department of Information Technology & Cloud Systems": (
                "DSC 1: Database Management Systems & SQL Architecture — High (Core)\n"
                "DSC 2: Cyber Security, Cryptography & Network Defense — High (Core)\n"
                "DSE: Microservices & DevOps Engineering — Medium (Elective)\n"
                "SEC: Mobile Application Development with Flutter — Medium (Skill)\n"
                "AEC: Professional Communication Skills — Low"
            ),
            "Custom Autonomous Department / Programme": (
                "Subject 1 (Core Paper) — High Difficulty\n"
                "Subject 2 (Core Paper) — High Difficulty\n"
                "Subject 3 (Department Elective) — Medium Difficulty\n"
                "Subject 4 (Skill Course) — Low Difficulty"
            )
        }

        auto_subjects = dept_presets.get(selected_dept, dept_presets["Custom Autonomous Department / Programme"])

        with st.form("study_plan_form"):
            subjects = st.text_area(
                "Coursework Modules & Assessment Units",
                value=auto_subjects,
                height=160,
                help="Syllabus units fetched from official Ruia College autonomous curriculum"
            )

            c_hrs, c_cia = st.columns(2)
            with c_hrs:
                hours = st.slider("Focused Study Hours Per Day", min_value=1, max_value=10, value=4, step=1)
            with c_cia:
                assessment_focus = st.selectbox(
                    "Primary Assessment Focus",
                    [
                        "Balanced (CIA 40 Marks + Semester End Exam 60 Marks)",
                        "Continuous Internal Assessment (CIA Test & Lab Submissions)",
                        "Semester End Examination (SEE Theory Papers Preparation)",
                        "Foundation Concept Building & Practical Lab Prep"
                    ]
                )

            exams = st.text_input("Upcoming Exam Horizons / CIA Test Dates (optional)", placeholder="e.g. CIA Internal Assessment on Oct 10; Sem End Exam Nov 15")

            submit = st.form_submit_button("✦ Synthesize Ruia 7-Day Timetable", use_container_width=True)

        if submit:
            if not subjects.strip():
                st.warning("Please specify your subjects and coursework modules.")
            else:
                context_str = f"Assessment Strategy: {assessment_focus}. Exam Context: {exams.strip() or 'Regular Semester Pace'}"
                with st.spinner("Ruia AI is synthesizing your official autonomous curriculum timetable..."):
                    try:
                        plan = create_plan(student['student_id'], subjects.strip(), hours, context_str)
                        st.session_state["current_plan"] = plan
                        st.success("7-Day Academic Timetable crafted and saved to MySQL database!")
                    except Exception as exc:
                        st.error(f"Error generating study plan: {exc}")

    with col_output:
        st.markdown("### 🏛️ Official 7-Day Timetable")

        current_plan = st.session_state.get("current_plan")
        if not current_plan:
            db_plan = get_latest_plan(student['student_id'])
            if db_plan:
                current_plan = db_plan['generated_plan']

        if current_plan:
            st.markdown(current_plan, unsafe_allow_html=True)
            st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)
            st.download_button(
                "📥 Download Official Study Timetable (.md)",
                data=current_plan,
                file_name="ruia_autonomous_study_plan.md",
                mime="text/markdown",
                use_container_width=True
            )
        else:
            st.markdown("""
            <div style="background:#FFF; border:1px dashed #DACDBB; border-radius:14px; padding:48px 24px; text-align:center; color:#71717A;">
                <div style="font-size:2.4rem; margin-bottom:12px;">🏛️</div>
                <h4 style="margin:0 0 6px 0; color:#6B0F1A !important;">Awaiting Timetable Synthesis</h4>
                <p style="font-size:0.92rem; max-width:380px; margin:0 auto;">
                    Select your official Ruia College department on the left and click <b>Synthesize Ruia 7-Day Timetable</b>.
                </p>
            </div>
            """, unsafe_allow_html=True)
