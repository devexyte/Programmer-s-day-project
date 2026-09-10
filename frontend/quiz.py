import streamlit as st
from backend.quiz_logic import create_quiz, get_student_quizzes

def render(student):
    if not student:
        st.info("Please set up or select your student profile.")
        return

    st.markdown("""
    <div style="margin-bottom: 20px;">
        <div class="section-kicker">ACTIVE RECALL & RETENTION WORKSHOP</div>
        <h1 style="margin: 0 0 6px 0;">Quiz Studio & Practice Question Generator</h1>
        <p style="color: #64748B; font-size: 1.05rem; margin: 0;">
            Transform syllabus lecture topics into rigorous practice problems, multiple-choice questions, and mastery flashcards.
        </p>
    </div>
    """, unsafe_allow_html=True)

    tab_create, tab_history = st.tabs(["🎯 Practice Studio", "📚 My Practice Vault"])

    with tab_create:
        st.markdown("<small style='color:#71717A; font-weight:600;'>POPULAR RUIA SYLLABUS TOPICS:</small>", unsafe_allow_html=True)
        q1, q2, q3, q4 = st.columns(4)
        if q1.button("💻 Binary Trees & Graphs", use_container_width=True):
            st.session_state["quiz_subj"] = "Data Structures & Algorithms"
            st.session_state["quiz_top"] = "Binary Search Trees, Graph Traversals (BFS/DFS) & Asymptotic Complexity"
        if q2.button("🧪 Organic Mechanisms", use_container_width=True):
            st.session_state["quiz_subj"] = "Organic Chemistry"
            st.session_state["quiz_top"] = "Nucleophilic Substitution (SN1/SN2) & Stereochemical Inversion"
        if q3.button("📊 Macroeconomics", use_container_width=True):
            st.session_state["quiz_subj"] = "Autonomous Economics"
            st.session_state["quiz_top"] = "Monetary Policy Transmission, Inflation Targeting & IS-LM Framework"
        if q4.button("🧬 DNA & Molecular Bio", use_container_width=True):
            st.session_state["quiz_subj"] = "Biotechnology"
            st.session_state["quiz_top"] = "Prokaryotic vs Eukaryotic DNA Replication & Polymerase Enzymes"

        with st.form("quiz_generator_form"):
            c_subj, c_top = st.columns(2)
            with c_subj:
                subject = st.text_input(
                    "Academic Subject / Paper",
                    value=st.session_state.get("quiz_subj", "Computer Science · Operating Systems"),
                    placeholder="e.g. Database Management Systems"
                )
            with c_top:
                topic = st.text_input(
                    "Specific Topic / Chapter Unit",
                    value=st.session_state.get("quiz_top", "Process Synchronization & Deadlock Handling"),
                    placeholder="e.g. ACID Properties & Concurrency Control"
                )

            c_fmt, c_cnt = st.columns(2)
            with c_fmt:
                kind = st.selectbox(
                    "Assessment Format",
                    [
                        "multiple-choice questions with 4 options and detailed rationale",
                        "short-answer conceptual university examination questions",
                        "spaced-repetition study flashcards with key principles"
                    ]
                )
            with c_cnt:
                count = st.slider("Number of Questions", min_value=3, max_value=20, value=5, step=1)

            generate_btn = st.form_submit_button("✦ Build Practice Set with Ruia AI", use_container_width=True)

        if generate_btn:
            if not subject.strip() or not topic.strip():
                st.warning("Please specify both subject and topic.")
            else:
                with st.spinner("Ruia AI professor is curating rigorous examination questions..."):
                    try:
                        quiz_content = create_quiz(student['student_id'], subject.strip(), topic.strip(), kind, count)
                        st.session_state["active_quiz"] = quiz_content
                        st.success("Practice set generated and saved to your vault!")
                    except Exception as exc:
                        st.error(f"Quiz generation failed: {exc}")

        active_quiz = st.session_state.get("active_quiz")
        if active_quiz:
            st.markdown("---")
            st.markdown(active_quiz, unsafe_allow_html=True)
            st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)
            st.download_button(
                "📥 Download Practice Paper (.md)",
                data=active_quiz,
                file_name="ruia_practice_quiz.md",
                mime="text/markdown",
                use_container_width=True
            )

    with tab_history:
        st.markdown("### 📚 Previously Generated Quizzes")
        try:
            vault = get_student_quizzes(student['student_id'])
            if vault:
                for q in vault:
                    created_time = str(q.get('created_at', ''))[:16]
                    with st.expander(f"🎯 {q['subject']} — {q['topic']} ({created_time})"):
                        st.markdown(q['generated_quiz'], unsafe_allow_html=True)
            else:
                st.info("No saved practice sets yet. Generated quizzes will be archived here automatically.")
        except Exception as exc:
            st.error(f"Error reading practice vault: {exc}")
