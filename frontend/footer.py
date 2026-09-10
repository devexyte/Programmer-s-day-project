import streamlit as st

def render_footer():
    html_content = """<div class="rui-master-footer">
<div class="rui-footer-grid">
<div class="rui-footer-col">
<div class="rui-footer-brand">
<span style="font-family:'Playfair Display',serif; font-size:1.4rem; font-weight:800; color:#FFFFFF; letter-spacing:-0.02em;">RUI</span>
<span class="rui-footer-badge">Student Buddy</span>
</div>
<p class="rui-footer-desc">
The official digital extension of <b>Ramnarain Ruia Autonomous College</b>, Matunga East, Mumbai. Designed to orchestrate academic timetables, internal assessment deadlines, and placement readiness.
</p>
<div class="rui-footer-accreditation">
<span>🏛️ Estd. 1937</span>
<span>·</span>
<span>NAAC 'A+' (CGPA 3.70)</span>
<span>·</span>
<span>Autonomous</span>
</div>
</div>
<div class="rui-footer-col">
<h4>🏛️ Academic Portals</h4>
<ul class="rui-footer-links">
<li><a href="https://www.ruiacollege.edu/" target="_blank">Official Ruia College Website ↗</a></li>
<li><a href="#examination-cell">Autonomous Examination Cell (CIA & SEE)</a></li>
<li><a href="#nep-curriculum">NEP 2020 Autonomous Curriculum Units</a></li>
<li><a href="#central-library">Ruia Central Library & OPAC Catalog</a></li>
<li><a href="#attendance-portal">Student Attendance & CIA Records</a></li>
</ul>
</div>
<div class="rui-footer-col">
<h4>⚡ Student Companion</h4>
<ul class="rui-footer-links">
<li><a href="#planner">7-Day Syllabus Revision Planner</a></li>
<li><a href="#assignments">Continuous Assessment & Milestones</a></li>
<li><a href="#resume">Placement Cell ATS Resume Diagnostics</a></li>
<li><a href="#quiz">Active-Recall Quiz Studio & Flashcards</a></li>
<li><a href="#exams">Semester Exam Map & Campus Venues</a></li>
</ul>
</div>
<div class="rui-footer-col">
<h4>📍 Campus & System</h4>
<p class="rui-footer-campus">
<b>Ramnarain Ruia Autonomous College</b><br>
L.N. Road, Matunga East, Mumbai 400019<br>
<span style="color:#F3E5C8;">Opp. Matunga Post Office · Central Line</span>
</p>
<div class="rui-footer-status">
<div>● Database: <b style="color:#34D399;">Ruia-Buddy (MySQL)</b></div>
<div>● AI Engine: <b style="color:#FBBF24;">Google Gemini 2.5 Flash</b></div>
<div>● Architecture: <b style="color:#60A5FA;">Streamlit + Python 3.14</b></div>
</div>
</div>
</div>
<div class="rui-footer-bottom">
<div>
© 2026 <b>Ramnarain Ruia Autonomous College</b> · Mumbai. Crafted with pride for Ruia scholars.
</div>
<div style="font-style:italic; color:#F3E5C8;">
“Explore · Experience · Excel” — Official College Motto
</div>
</div>
</div>"""
    st.html(html_content)
