import streamlit as st

def render():
    st.markdown('<div class="hero"><div class="crest">RC</div><div><p class="eyebrow">RUIA COLLEGE · MUMBAI</p><h1>Your academic life,<br><em>beautifully in rhythm.</em></h1><p class="lead">An intelligent companion for planning, practice and purposeful progress.</p></div></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-kicker">ONE COMPANION · FIVE WAYS FORWARD</div>', unsafe_allow_html=True)
    cols = st.columns(5)
    cards = [("✦", "Study plan", "Shape each week around your pace."), ("◷", "Reminders", "Meet every deadline calmly."), ("⌁", "Resume lab", "Present your strongest self."), ("?", "Quiz studio", "Turn topics into mastery."), ("◉", "Exam map", "Revise with confidence.")]
    for col, (icon, title, copy) in zip(cols, cards):
        with col: st.markdown(f'<div class="feature-card"><span>{icon}</span><h3>{title}</h3><p>{copy}</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="home-note">“Education is not preparation for life; education is life itself.” <b>— Ruia AI Student Companion</b></div>', unsafe_allow_html=True)

