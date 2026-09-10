CREATE DATABASE IF NOT EXISTS ruia_companion;
USE ruia_companion;

CREATE TABLE students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL, email VARCHAR(100) NOT NULL UNIQUE,
    program VARCHAR(100) NOT NULL, year INT NOT NULL
);
CREATE TABLE courses (
    course_id INT AUTO_INCREMENT PRIMARY KEY,
    course_name VARCHAR(100) NOT NULL, course_code VARCHAR(50) NOT NULL UNIQUE, year INT NOT NULL
);
CREATE TABLE assignments (
    assignment_id INT AUTO_INCREMENT PRIMARY KEY, student_id INT NOT NULL, course_id INT NULL,
    title VARCHAR(200) NOT NULL, due_date DATE NOT NULL, status VARCHAR(50) NOT NULL DEFAULT 'Pending',
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE SET NULL
);
CREATE TABLE exams (
    exam_id INT AUTO_INCREMENT PRIMARY KEY, student_id INT NOT NULL, course_id INT NULL,
    exam_date DATE NOT NULL, exam_time VARCHAR(20), venue VARCHAR(100),
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE SET NULL
);
CREATE TABLE study_plans (
    plan_id INT AUTO_INCREMENT PRIMARY KEY, student_id INT NOT NULL, generated_plan TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
);
CREATE TABLE reminders (
    reminder_id INT AUTO_INCREMENT PRIMARY KEY, student_id INT NOT NULL, assignment_id INT NOT NULL,
    reminder_text TEXT NOT NULL, reminder_date DATE NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (assignment_id) REFERENCES assignments(assignment_id) ON DELETE CASCADE
);
CREATE TABLE quizzes (
    quiz_id INT AUTO_INCREMENT PRIMARY KEY, student_id INT NOT NULL, subject VARCHAR(100) NOT NULL,
    topic VARCHAR(100) NOT NULL, generated_quiz TEXT NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
);

