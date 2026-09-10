/**
 * RUI - Ruia Student Buddy Application Logic
 * Ramnarain Ruia Autonomous College
 */

// Global State
let currentStudent = {
  id: 1,
  name: 'Aarav Sharma',
  department: 'Computer Science',
  year: 'TY BSc',
  gpa: 3.85
};

let allStudents = [];
let allCourses = [];
let activeTab = 'welcome';
let examTimers = [];

// Initialize Application
document.addEventListener('DOMContentLoaded', async () => {
  initStudentSession();
  setupNavigation();
  await checkSystemStatus();
  await loadStudentsList();
  await loadCoursesList();
  
  // Handle URL hash routing if present
  const hash = window.location.hash.replace('#', '');
  if (hash && ['welcome', 'dashboard', 'planner', 'assignments', 'resume', 'quiz', 'exams'].includes(hash)) {
    showTab(hash);
  } else {
    showTab('welcome');
  }

  // Bind forms
  setupEventListeners();
});

/* ==========================================================================
   SESSION & STUDENT MANAGEMENT
   ========================================================================== */
function initStudentSession() {
  const saved = localStorage.getItem('ruia_student');
  if (saved) {
    try {
      currentStudent = JSON.parse(saved);
    } catch (e) {
      console.warn('Using default student profile');
    }
  }
  updateScholarDisplay();
}

function updateScholarDisplay() {
  const nameEl = document.getElementById('navbarScholarName');
  const deptEl = document.getElementById('navbarScholarDept');
  const avatarEl = document.getElementById('navbarScholarAvatar');
  
  if (nameEl) nameEl.textContent = currentStudent.name;
  if (deptEl) deptEl.textContent = `${currentStudent.department} • ${currentStudent.year || 'Student'}`;
  if (avatarEl) {
    const initials = currentStudent.name.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase();
    avatarEl.textContent = initials || 'RU';
  }

  // Update quick select chips active state
  document.querySelectorAll('.quick-scholar-chip').forEach(chip => {
    if (chip.getAttribute('data-name') === currentStudent.name) {
      chip.classList.add('active');
    } else {
      chip.classList.remove('active');
    }
  });
}

function selectScholar(studentId, name, dept, year) {
  currentStudent = {
    id: parseInt(studentId, 10),
    name: name,
    department: dept || 'Science',
    year: year || 'FY'
  };
  localStorage.setItem('ruia_student', JSON.stringify(currentStudent));
  updateScholarDisplay();
  showToast(`Switched to scholar: ${currentStudent.name}`, 'success');

  // Refresh current view
  if (activeTab === 'dashboard') loadDashboard();
  if (activeTab === 'assignments') loadAssignments();
  if (activeTab === 'exams') loadExams();
  if (activeTab === 'planner') loadLatestPlan();
}

async function loadStudentsList() {
  try {
    const res = await fetch('/api/students');
    const data = await res.json();
    const list = data.students || (Array.isArray(data) ? data : []);
    if (list.length > 0) {
      allStudents = list.map(s => ({
        id: s.id || s.student_id,
        name: s.name,
        department: s.department || s.program || 'Science',
        year: s.year || 'FY BSc'
      }));
      populateScholarDropdown();
    }
  } catch (err) {
    console.error('Failed to load students:', err);
  }
}

function populateScholarDropdown() {
  const select = document.getElementById('scholarModalSelect');
  if (!select) return;
  select.innerHTML = allStudents.map(s => 
    `<option value="${s.id}" ${s.id === currentStudent.id ? 'selected' : ''}>${s.name} (${s.department} - ${s.year})</option>`
  ).join('');
}

async function loadCoursesList() {
  try {
    const res = await fetch('/api/courses');
    const data = await res.json();
    const list = data.courses || (Array.isArray(data) ? data : []);
    if (list.length > 0) {
      allCourses = list.map(c => ({
        id: c.id || c.course_id,
        name: c.name || c.course_name,
        code: c.code || c.course_code || ''
      }));
      populateCourseDropdowns();
    }
  } catch (err) {
    console.error('Failed to load courses:', err);
  }
}

function populateCourseDropdowns() {
  const dropdownIds = ['assignmentCourse', 'quizCourse', 'examCourse'];
  dropdownIds.forEach(id => {
    const select = document.getElementById(id);
    if (!select) return;
    const placeholder = id === 'quizCourse' ? 'Select Subject / Course' : 'Choose Course';
    select.innerHTML = `<option value="">-- ${placeholder} --</option>` + 
      allCourses.map(c => `<option value="${c.id}">${c.code ? c.code + ' - ' : ''}${c.name}</option>`).join('');
  });
}

/* ==========================================================================
   NAVIGATION
   ========================================================================== */
function setupNavigation() {
  const tabs = document.querySelectorAll('.dock-tab');
  tabs.forEach(tab => {
    tab.addEventListener('click', (e) => {
      const targetTab = tab.getAttribute('data-tab');
      if (targetTab) {
        showTab(targetTab);
      }
    });
  });
}

function showTab(tabId) {
  activeTab = tabId;
  window.location.hash = tabId;

  // Update tabs
  document.querySelectorAll('.dock-tab').forEach(tab => {
    if (tab.getAttribute('data-tab') === tabId) {
      tab.classList.add('active');
    } else {
      tab.classList.remove('active');
    }
  });

  // Update panes
  document.querySelectorAll('.tab-pane').forEach(pane => {
    if (pane.id === `tab-${tabId}`) {
      pane.classList.add('active');
    } else {
      pane.classList.remove('active');
    }
  });

  // Trigger tab-specific loader
  if (tabId === 'dashboard') {
    loadDashboard();
  } else if (tabId === 'assignments') {
    loadAssignments();
  } else if (tabId === 'exams') {
    loadExams();
  } else if (tabId === 'planner') {
    loadLatestPlan();
  }

  window.scrollTo({ top: 0, behavior: 'smooth' });
}

/* ==========================================================================
   SYSTEM STATUS & AI KEY CONFIG
   ========================================================================== */
async function checkSystemStatus() {
  try {
    const res = await fetch('/api/status');
    const data = await res.json();
    const dot = document.getElementById('aiStatusDot');
    const text = document.getElementById('aiStatusText');

    if (data.gemini_configured) {
      if (dot) {
        dot.className = 'status-dot';
        dot.style.backgroundColor = '#10B981';
      }
      if (text) text.textContent = 'Gemini AI Ready';
    } else {
      if (dot) {
        dot.className = 'status-dot warning';
        dot.style.backgroundColor = '#F59E0B';
      }
      if (text) text.textContent = 'Setup API Key';
    }
  } catch (e) {
    console.warn('Status check failed', e);
  }
}

async function saveGeminiKey() {
  const keyInput = document.getElementById('geminiKeyInput');
  const key = keyInput.value.trim();
  if (!key) {
    showToast('Please enter a valid Gemini API key', 'error');
    return;
  }

  try {
    const res = await fetch('/api/config/gemini-key', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ key: key })
    });
    const result = await res.json();
    if (result.success) {
      showToast('Gemini API key configured successfully!', 'success');
      closeModal('apiKeyModal');
      keyInput.value = '';
      checkSystemStatus();
    } else {
      showToast(result.error || 'Failed to save key', 'error');
    }
  } catch (err) {
    showToast('Network error while saving API key', 'error');
  }
}

/* ==========================================================================
   MODULE 2: ACADEMIC DASHBOARD
   ========================================================================== */
async function loadDashboard() {
  const container = document.getElementById('dashboardMetricsContainer');
  const urgentList = document.getElementById('dashboardUrgentList');
  const examList = document.getElementById('dashboardExamList');

  try {
    const res = await fetch(`/api/dashboard?student_id=${currentStudent.id}`);
    const data = await res.json();

    if (!data.success) {
      showToast('Unable to load dashboard data', 'error');
      return;
    }

    const { metrics, upcoming_assignments, upcoming_exams } = data;

    // Populate metric values
    const gpaEl = document.getElementById('metricGPA');
    const totalAssignEl = document.getElementById('metricTotalAssign');
    const pendingAssignEl = document.getElementById('metricPendingAssign');
    const examsCountEl = document.getElementById('metricUpcomingExams');

    if (gpaEl) gpaEl.textContent = metrics.gpa ? parseFloat(metrics.gpa).toFixed(2) : '3.80';
    if (totalAssignEl) totalAssignEl.textContent = metrics.total_assignments || '0';
    if (pendingAssignEl) pendingAssignEl.textContent = metrics.pending_assignments || '0';
    if (examsCountEl) examsCountEl.textContent = metrics.upcoming_exams || '0';

    // Upcoming assignments
    if (urgentList) {
      if (upcoming_assignments && upcoming_assignments.length > 0) {
        urgentList.innerHTML = upcoming_assignments.map(a => `
          <div class="activity-item">
            <div class="activity-meta">
              <span class="activity-title">${escapeHtml(a.title)}</span>
              <span class="activity-detail">${escapeHtml(a.course_name || 'Course')} • Due: ${formatDate(a.due_date)}</span>
            </div>
            <span class="badge-status badge-${(a.status || 'pending').toLowerCase()}">${a.status || 'Pending'}</span>
          </div>
        `).join('');
      } else {
        urgentList.innerHTML = `
          <div class="empty-state" style="padding: 20px;">
            <p class="empty-desc">No urgent assignments pending! You're fully caught up.</p>
          </div>
        `;
      }
    }

    // Upcoming exams
    if (examList) {
      if (upcoming_exams && upcoming_exams.length > 0) {
        examList.innerHTML = upcoming_exams.map(e => `
          <div class="activity-item">
            <div class="activity-meta">
              <span class="activity-title">${escapeHtml(e.name || e.course_name)}</span>
              <span class="activity-detail">Date: ${formatDate(e.date)} • Weightage: ${e.weightage || '30%'}</span>
            </div>
            <span class="badge-status badge-submitted">Exam</span>
          </div>
        `).join('');
      } else {
        examList.innerHTML = `
          <div class="empty-state" style="padding: 20px;">
            <p class="empty-desc">No upcoming examinations scheduled.</p>
          </div>
        `;
      }
    }

  } catch (err) {
    console.error('Dashboard load error:', err);
  }
}

/* ==========================================================================
   MODULE 3: STUDY PLANNER
   ========================================================================== */
async function generateStudyPlan(e) {
  if (e) e.preventDefault();
  
  const dailyHours = document.getElementById('planHours').value;
  const examDate = document.getElementById('planExamDate').value;
  const difficulty = document.getElementById('planDifficulty').value;
  const focus = document.getElementById('planFocus').value;

  const outputContainer = document.getElementById('planMarkdownDisplay');
  const btn = document.getElementById('generatePlanBtn');

  if (btn) {
    btn.disabled = true;
    btn.innerHTML = `<span>Synthesizing 7-Day Curriculum...</span>`;
  }

  if (outputContainer) {
    outputContainer.innerHTML = `
      <div style="text-align: center; padding: 40px;">
        <div style="font-size: 2rem; margin-bottom: 12px; animation: spin 1s infinite linear;">⚙️</div>
        <h4 style="color: #0F172A; font-weight: 700;">Analyzing Ruia Syllabus with Gemini AI...</h4>
        <p style="color: #64748B;">Balancing lecture hours, assignment deadlines, and high-weightage topics...</p>
      </div>
    `;
  }

  try {
    const res = await fetch('/api/planner', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        student_id: currentStudent.id,
        daily_hours: parseFloat(dailyHours) || 3.5,
        exam_date: examDate,
        difficulty: difficulty,
        focus_topics: focus
      })
    });

    const data = await res.json();
    if (data.success && data.plan) {
      renderMarkdown(data.plan, 'planMarkdownDisplay');
      showToast('7-Day Academic Study Plan generated!', 'success');
    } else {
      outputContainer.innerHTML = `
        <div class="empty-state">
          <p class="empty-desc" style="color: #EF4444;">${data.error || 'Failed to generate study plan. Please verify Gemini API key.'}</p>
        </div>
      `;
    }
  } catch (err) {
    showToast('Failed to contact study planner engine', 'error');
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = `<span>Generate 7-Day Schedule</span> ➔`;
    }
  }
}

async function loadLatestPlan() {
  const outputContainer = document.getElementById('planMarkdownDisplay');
  if (!outputContainer) return;

  try {
    const res = await fetch(`/api/planner?student_id=${currentStudent.id}`);
    const data = await res.json();
    if (data.success && data.plan) {
      renderMarkdown(data.plan, 'planMarkdownDisplay');
    }
  } catch (e) {
    console.warn('No cached plan found');
  }
}

/* ==========================================================================
   MODULE 4: ASSIGNMENT DESK
   ========================================================================== */
async function loadAssignments() {
  const tableBody = document.getElementById('assignmentsTableBody');
  const remindersBody = document.getElementById('remindersWidgetBody');

  if (!tableBody) return;

  try {
    const res = await fetch(`/api/assignments?student_id=${currentStudent.id}`);
    const data = await res.json();

    if (data.assignments && data.assignments.length > 0) {
      tableBody.innerHTML = data.assignments.map(a => `
        <tr>
          <td><strong>${escapeHtml(a.title)}</strong></td>
          <td>${escapeHtml(a.course_name || 'Autonomous Course')}</td>
          <td>${formatDate(a.due_date)}</td>
          <td>
            <span class="badge-status" style="background: ${getPriorityBg(a.priority)}; color: ${getPriorityColor(a.priority)}">
              ${a.priority || 'Normal'}
            </span>
          </td>
          <td>
            <span class="badge-status badge-${(a.status || 'pending').toLowerCase()}">${a.status || 'Pending'}</span>
          </td>
          <td>
            <div style="display: flex; gap: 8px;">
              ${a.status !== 'Completed' ? `
                <button class="btn btn-sm btn-outline" onclick="markAssignmentDone(${a.assignment_id || a.id})">✓ Done</button>
              ` : ''}
              <button class="btn btn-sm btn-secondary" onclick="deleteAssignment(${a.assignment_id || a.id})" title="Delete">🗑</button>
            </div>
          </td>
        </tr>
      `).join('');
    } else {
      tableBody.innerHTML = `
        <tr>
          <td colspan="6" style="text-align: center; padding: 32px;">
            <p style="color: #64748B;">No assignments found for ${escapeHtml(currentStudent.name)}. Click "Create Assignment" to add one!</p>
          </td>
        </tr>
      `;
    }

    // Load AI Reminders
    if (remindersBody) {
      const remRes = await fetch(`/api/assignments/reminders?student_id=${currentStudent.id}`);
      const remData = await remRes.json();
      if (remData.reminders && remData.reminders.length > 0) {
        remindersBody.innerHTML = remData.reminders.map(r => `
          <div class="activity-item" style="border-left: 3px solid #800000;">
            <div class="activity-meta">
              <span class="activity-title">${escapeHtml(r.title)}</span>
              <span class="activity-detail">${escapeHtml(r.reminder_text || r.message || 'Due soon')}</span>
            </div>
          </div>
        `).join('');
      } else {
        remindersBody.innerHTML = `<p style="font-size: 0.88rem; color: #64748B; padding: 10px;">All submissions are on track!</p>`;
      }
    }
  } catch (err) {
    console.error('Error loading assignments:', err);
  }
}

async function createAssignment(e) {
  if (e) e.preventDefault();

  const title = document.getElementById('assignTitle').value.trim();
  const courseId = document.getElementById('assignmentCourse').value;
  const dueDate = document.getElementById('assignDueDate').value;
  const priority = document.getElementById('assignPriority').value;

  if (!title || !dueDate) {
    showToast('Please enter both title and due date', 'error');
    return;
  }

  try {
    const res = await fetch('/api/assignments', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        student_id: currentStudent.id,
        title: title,
        course_id: parseInt(courseId, 10) || null,
        due_date: dueDate,
        priority: priority
      })
    });

    const result = await res.json();
    if (result.success) {
      showToast('Assignment logged into registry', 'success');
      document.getElementById('assignTitle').value = '';
      document.getElementById('assignDueDate').value = '';
      closeModal('newAssignmentModal');
      loadAssignments();
    } else {
      showToast(result.error || 'Failed to save assignment', 'error');
    }
  } catch (err) {
    showToast('Network error while adding assignment', 'error');
  }
}

async function markAssignmentDone(assignmentId) {
  try {
    const res = await fetch(`/api/assignments/${assignmentId}/status`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: 'Completed' })
    });
    const result = await res.json();
    if (result.success) {
      showToast('Assignment marked as completed!', 'success');
      loadAssignments();
    }
  } catch (err) {
    showToast('Error updating status', 'error');
  }
}

async function deleteAssignment(assignmentId) {
  if (!confirm('Are you sure you want to delete this assignment?')) return;
  try {
    const res = await fetch(`/api/assignments/${assignmentId}`, {
      method: 'DELETE'
    });
    const result = await res.json();
    if (result.success) {
      showToast('Assignment removed', 'success');
      loadAssignments();
    }
  } catch (err) {
    showToast('Error deleting assignment', 'error');
  }
}

/* ==========================================================================
   MODULE 5: RESUME LAB
   ========================================================================== */
async function analyzeResume(e) {
  if (e) e.preventDefault();

  const resumeText = document.getElementById('resumeRawText').value.trim();
  const targetRole = document.getElementById('resumeTargetRole').value.trim();
  const targetCompany = document.getElementById('resumeTargetCompany').value.trim();

  if (!resumeText) {
    showToast('Please paste your current resume text', 'error');
    return;
  }

  const outputContainer = document.getElementById('resumeAnalysisOutput');
  const btn = document.getElementById('analyzeResumeBtn');

  if (btn) {
    btn.disabled = true;
    btn.innerHTML = `<span>Evaluating ATS Alignment...</span>`;
  }

  if (outputContainer) {
    outputContainer.innerHTML = `
      <div style="text-align: center; padding: 40px;">
        <div style="font-size: 2rem; margin-bottom: 12px; animation: spin 1s infinite linear;">🔍</div>
        <h4 style="color: #0F172A; font-weight: 700;">Running Ruia Career Diagnostics...</h4>
        <p style="color: #64748B;">Cross-referencing industry keywords, STAR impact statements, and formatting...</p>
      </div>
    `;
  }

  try {
    const res = await fetch('/api/resume/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        resume_text: resumeText,
        target_role: targetRole || 'Software Engineer',
        target_company: targetCompany || 'Top Tech Firm'
      })
    });

    const data = await res.json();
    if (data.success && (data.analysis || data.review_markdown)) {
      renderMarkdown(data.analysis || data.review_markdown, 'resumeAnalysisOutput');
      showToast('ATS diagnostic report generated!', 'success');
    } else {
      outputContainer.innerHTML = `
        <div class="empty-state">
          <p class="empty-desc" style="color: #EF4444;">${data.error || 'Failed to analyze resume'}</p>
        </div>
      `;
    }
  } catch (err) {
    showToast('Failed to contact resume lab service', 'error');
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = `<span>Analyze & Optimize Resume</span> ➔`;
    }
  }
}

/* ==========================================================================
   MODULE 6: QUIZ STUDIO
   ========================================================================== */
async function generateQuiz(e) {
  if (e) e.preventDefault();

  const courseSelect = document.getElementById('quizCourse');
  const courseId = courseSelect.value;
  const courseName = courseSelect.options[courseSelect.selectedIndex]?.text || '';
  const topic = document.getElementById('quizTopic').value.trim();
  const count = document.getElementById('quizCount').value;
  const difficulty = document.getElementById('quizDifficulty').value;

  if (!topic) {
    showToast('Please enter a topic for the quiz', 'error');
    return;
  }

  const container = document.getElementById('quizQuestionsContainer');
  const btn = document.getElementById('generateQuizBtn');

  if (btn) {
    btn.disabled = true;
    btn.innerHTML = `<span>Crafting Questions...</span>`;
  }

  if (container) {
    container.innerHTML = `
      <div style="text-align: center; padding: 40px;">
        <div style="font-size: 2rem; margin-bottom: 12px; animation: spin 1s infinite linear;">⚡</div>
        <h4 style="color: #0F172A; font-weight: 700;">Generating Custom Assessment...</h4>
        <p style="color: #64748B;">Curating questions from Ruia autonomous question bank...</p>
      </div>
    `;
  }

  try {
    const res = await fetch('/api/quiz/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        subject: courseName || 'General Science',
        topic: topic,
        question_count: parseInt(count, 10) || 5,
        difficulty: difficulty
      })
    });

    const data = await res.json();
    if (data.success && data.quiz_markdown) {
      renderMarkdown(data.quiz_markdown, 'quizQuestionsContainer');
      showToast('Assessment ready! Test your mastery.', 'success');
    } else if (data.success && data.questions && data.questions.length > 0) {
      renderQuizQuestions(data.questions);
      showToast('Assessment ready! Test your mastery.', 'success');
    } else {
      container.innerHTML = `
        <div class="empty-state">
          <p class="empty-desc" style="color: #EF4444;">${data.error || 'Failed to generate quiz. Please check Gemini API key.'}</p>
        </div>
      `;
    }
  } catch (err) {
    showToast('Quiz Studio engine error', 'error');
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = `<span>Generate AI Assessment</span> ➔`;
    }
  }
}

function renderQuizQuestions(questions) {
  const container = document.getElementById('quizQuestionsContainer');
  if (!container) return;

  container.innerHTML = questions.map((q, idx) => `
    <div class="quiz-question-card" id="questionCard_${idx}">
      <div class="quiz-question-title">
        <span style="color: #800000; margin-right: 6px;">Q${idx + 1}.</span> ${escapeHtml(q.question)}
      </div>
      <div class="quiz-options-list">
        ${(q.options || []).map((opt, optIdx) => `
          <div class="quiz-option-item" onclick="handleQuizAnswer(${idx}, ${optIdx}, '${escapeHtml(q.correct_answer || '')}', '${escapeHtml(q.explanation || '')}')">
            <span style="font-weight: 700; width: 24px;">${String.fromCharCode(65 + optIdx)}.</span>
            <span>${escapeHtml(opt)}</span>
          </div>
        `).join('')}
      </div>
      <div class="quiz-explanation-box" id="explanationBox_${idx}" style="display: none;"></div>
    </div>
  `).join('');
}

function handleQuizAnswer(qIdx, selectedOptIdx, correctAnswer, explanation) {
  const card = document.getElementById(`questionCard_${qIdx}`);
  if (!card) return;

  const options = card.querySelectorAll('.quiz-option-item');
  const expBox = document.getElementById(`explanationBox_${qIdx}`);

  // Disable further clicks
  options.forEach((opt, idx) => {
    opt.style.pointerEvents = 'none';
    const optText = opt.innerText.replace(/^[A-D]\.\s*/, '').trim();
    
    if (optText.toLowerCase() === correctAnswer.toLowerCase() || idx.toString() === correctAnswer) {
      opt.classList.add('correct');
    } else if (idx === selectedOptIdx) {
      opt.classList.add('incorrect');
    }
  });

  if (expBox) {
    expBox.style.display = 'block';
    expBox.innerHTML = `<strong>Explanation:</strong> ${explanation || 'Correct Answer: ' + correctAnswer}`;
  }
}

/* ==========================================================================
   MODULE 7: EXAM MAP
   ========================================================================== */
async function loadExams() {
  const grid = document.getElementById('examCountdownGrid');
  if (!grid) return;

  // Clear existing timer intervals
  examTimers.forEach(t => clearInterval(t));
  examTimers = [];

  try {
    const res = await fetch(`/api/exams?student_id=${currentStudent.id}`);
    const data = await res.json();
    const examsList = data.exams || (Array.isArray(data) ? data : []);

    if (examsList.length > 0) {
      grid.innerHTML = examsList.map((exam, idx) => `
        <div class="countdown-card">
          <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div>
              <div class="countdown-exam-title">${escapeHtml(exam.name || exam.course_name || 'Autonomous Exam')}</div>
              <p style="font-size: 0.82rem; color: #64748B;">Target: ${formatDate(exam.exam_date || exam.date)}</p>
            </div>
            <button class="btn btn-sm btn-secondary" onclick="deleteExam(${exam.exam_id || exam.id})" title="Delete">🗑</button>
          </div>
          <div class="countdown-timer-wrap" id="timerExam_${idx}">
            <div style="display: flex; flex-direction: column; align-items: center;">
              <div class="countdown-digit-box days-box">00</div>
              <span class="countdown-unit-label">Days</span>
            </div>
            <div style="font-weight: 800; font-size: 1.4rem; color: #800000;">:</div>
            <div style="display: flex; flex-direction: column; align-items: center;">
              <div class="countdown-digit-box hours-box">00</div>
              <span class="countdown-unit-label">Hours</span>
            </div>
            <div style="font-weight: 800; font-size: 1.4rem; color: #800000;">:</div>
            <div style="display: flex; flex-direction: column; align-items: center;">
              <div class="countdown-digit-box mins-box">00</div>
              <span class="countdown-unit-label">Mins</span>
            </div>
            <div style="font-weight: 800; font-size: 1.4rem; color: #800000;">:</div>
            <div style="display: flex; flex-direction: column; align-items: center;">
              <div class="countdown-digit-box secs-box">00</div>
              <span class="countdown-unit-label">Secs</span>
            </div>
          </div>
        </div>
      `).join('');

      // Setup countdown loops
      examsList.forEach((exam, idx) => {
        startCountdown(exam.exam_date || exam.date, `timerExam_${idx}`);
      });
    } else {
      grid.innerHTML = `
        <div class="empty-state" style="grid-column: 1 / -1;">
          <p class="empty-desc">No examination milestones recorded. Click "Add Exam Target" to schedule your next milestone.</p>
        </div>
      `;
    }
  } catch (err) {
    console.error('Error loading exams:', err);
  }
}

function startCountdown(targetDateStr, timerElementId) {
  const targetDate = new Date(targetDateStr).getTime();

  function update() {
    const el = document.getElementById(timerElementId);
    if (!el) return;

    const now = new Date().getTime();
    const distance = targetDate - now;

    if (distance < 0) {
      el.innerHTML = `<span style="font-weight: 700; color: #10B981; padding: 8px;">Concluded / In Progress</span>`;
      return;
    }

    const days = Math.floor(distance / (1000 * 60 * 60 * 24));
    const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((distance % (1000 * 60)) / 1000);

    const dBox = el.querySelector('.days-box');
    const hBox = el.querySelector('.hours-box');
    const mBox = el.querySelector('.mins-box');
    const sBox = el.querySelector('.secs-box');

    if (dBox) dBox.textContent = String(days).padStart(2, '0');
    if (hBox) hBox.textContent = String(hours).padStart(2, '0');
    if (mBox) mBox.textContent = String(minutes).padStart(2, '0');
    if (sBox) sBox.textContent = String(seconds).padStart(2, '0');
  }

  update();
  const timer = setInterval(update, 1000);
  examTimers.push(timer);
}

async function createExam(e) {
  if (e) e.preventDefault();

  const name = document.getElementById('examNameInput').value.trim();
  const courseId = document.getElementById('examCourse').value;
  const examDate = document.getElementById('examDateInput').value;

  if (!name || !examDate) {
    showToast('Please enter both exam title and date', 'error');
    return;
  }

  try {
    const res = await fetch('/api/exams', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        student_id: currentStudent.id,
        name: name,
        course_id: parseInt(courseId, 10) || null,
        date: examDate
      })
    });

    const result = await res.json();
    if (result.success) {
      showToast('Exam milestone logged!', 'success');
      document.getElementById('examNameInput').value = '';
      document.getElementById('examDateInput').value = '';
      closeModal('newExamModal');
      loadExams();
    } else {
      showToast(result.error || 'Failed to save exam', 'error');
    }
  } catch (err) {
    showToast('Error registering exam', 'error');
  }
}

async function deleteExam(examId) {
  if (!confirm('Remove this exam target?')) return;
  try {
    const res = await fetch(`/api/exams/${examId}`, { method: 'DELETE' });
    const result = await res.json();
    if (result.success) {
      showToast('Exam target removed', 'success');
      loadExams();
    }
  } catch (err) {
    showToast('Error deleting exam', 'error');
  }
}

async function generateRevisionPlan() {
  const container = document.getElementById('revisionScheduleOutput');
  if (!container) return;

  container.innerHTML = `
    <div style="text-align: center; padding: 30px;">
      <p style="color: #64748B;">Synthesizing AI spaced revision schedule based on your upcoming exams...</p>
    </div>
  `;

  try {
    const res = await fetch('/api/exams/revision-schedule', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ student_id: currentStudent.id })
    });
    const data = await res.json();
    if (data.success && data.schedule) {
      renderMarkdown(data.schedule, 'revisionScheduleOutput');
    } else {
      container.innerHTML = `<p style="color: #EF4444;">${data.error || 'Failed to generate revision schedule.'}</p>`;
    }
  } catch (err) {
    showToast('Error connecting to revision engine', 'error');
  }
}

/* ==========================================================================
   MODAL CONTROLLERS & FORM BINDING
   ========================================================================== */
function openModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.add('open');
  }
}

function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.remove('open');
  }
}

function setupEventListeners() {
  // Modal background clicks
  document.querySelectorAll('.modal-backdrop').forEach(modal => {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        modal.classList.remove('open');
      }
    });
  });

  // Study Planner Form
  const plannerForm = document.getElementById('plannerForm');
  if (plannerForm) plannerForm.addEventListener('submit', generateStudyPlan);

  // Resume Form
  const resumeForm = document.getElementById('resumeForm');
  if (resumeForm) resumeForm.addEventListener('submit', analyzeResume);

  // Quiz Form
  const quizForm = document.getElementById('quizForm');
  if (quizForm) quizForm.addEventListener('submit', generateQuiz);

  // New Assignment Form
  const assignForm = document.getElementById('newAssignmentForm');
  if (assignForm) assignForm.addEventListener('submit', createAssignment);

  // New Exam Form
  const examForm = document.getElementById('newExamForm');
  if (examForm) examForm.addEventListener('submit', createExam);

  // Student Switcher Modal Submit
  const scholarSwitchBtn = document.getElementById('scholarModalSwitchBtn');
  if (scholarSwitchBtn) {
    scholarSwitchBtn.addEventListener('click', () => {
      const select = document.getElementById('scholarModalSelect');
      const selectedId = select.value;
      const found = allStudents.find(s => s.id == selectedId);
      if (found) {
        selectScholar(found.id, found.name, found.department, found.year);
        closeModal('scholarModal');
      }
    });
  }
}

/* ==========================================================================
   UTILITY HELPERS
   ========================================================================== */
function renderMarkdown(mdText, containerId) {
  const container = document.getElementById(containerId);
  if (!container) return;

  if (window.marked) {
    container.innerHTML = `<div class="markdown-output">${window.marked.parse(mdText)}</div>`;
  } else {
    // Basic Markdown fallback
    let html = escapeHtml(mdText)
      .replace(/^### (.*$)/gim, '<h3>$1</h3>')
      .replace(/^## (.*$)/gim, '<h2>$1</h2>')
      .replace(/^# (.*$)/gim, '<h1>$1</h1>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/^\* (.*$)/gim, '<li>$1</li>')
      .replace(/\n/g, '<br/>');
    container.innerHTML = `<div class="markdown-output">${html}</div>`;
  }
}

function showToast(message, type = 'info') {
  const container = document.getElementById('toastContainer');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `<span>${escapeHtml(message)}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';
    toast.style.transition = 'all 300ms ease-out';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

function formatDate(dateStr) {
  if (!dateStr) return 'TBD';
  try {
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
  } catch (e) {
    return dateStr;
  }
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function getPriorityBg(priority) {
  const p = (priority || '').toLowerCase();
  if (p === 'high') return '#FEE2E2';
  if (p === 'medium') return '#FEF3C7';
  return '#E0E7FF';
}

function getPriorityColor(priority) {
  const p = (priority || '').toLowerCase();
  if (p === 'high') return '#991B1B';
  if (p === 'medium') return '#92400E';
  return '#3730A3';
}
