import os
from contextlib import contextmanager
from datetime import date
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

load_dotenv()


def _config():
    return {
        "host": os.getenv("MYSQL_HOST", "localhost"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER", "root"),
        "password": os.getenv("MYSQL_PASSWORD", ""),
        "database": os.getenv("MYSQL_DATABASE", "ruia_companion"),
        "connection_timeout": 20,
        "autocommit": True
    }


@contextmanager
def connection():
    conn = None
    last_err = None
    for attempt in range(2):
        try:
            conn = mysql.connector.connect(**_config())
            break
        except Exception as e:
            last_err = e
            if attempt == 1:
                raise last_err
    try:
        yield conn
        if conn and not conn.autocommit:
            conn.commit()
    except Exception:
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass
        raise
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


def fetch_all(query, params=()):
    with connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params)
        return cursor.fetchall()


def fetch_one(query, params=()):
    rows = fetch_all(query, params)
    return rows[0] if rows else None


def execute(query, params=()):
    with connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.lastrowid


def get_all_students():
    seed_default_data()
    return fetch_all("SELECT * FROM students ORDER BY student_id DESC")


def get_student_by_id(student_id):
    return fetch_one("SELECT * FROM students WHERE student_id = %s", (student_id,))


def get_or_create_student(name, email, program, year):
    student = fetch_one("SELECT * FROM students WHERE email = %s", (email.strip(),))
    if student:
        return student
    student_id = execute(
        "INSERT INTO students (name, email, program, year) VALUES (%s, %s, %s, %s)",
        (name.strip(), email.strip(), program.strip(), int(year))
    )
    return fetch_one("SELECT * FROM students WHERE student_id = %s", (student_id,))


def get_all_courses():
    seed_default_data()
    return fetch_all("SELECT * FROM courses ORDER BY course_name ASC")


def get_or_create_course(course_name, course_code=None, year=1):
    if not course_name:
        return None
    course = fetch_one("SELECT * FROM courses WHERE LOWER(course_name) = LOWER(%s)", (course_name.strip(),))
    if course:
        return course['course_id']
    code = course_code or course_name.strip().upper()[:6].replace(" ", "")
    existing_code = fetch_one("SELECT * FROM courses WHERE course_code = %s", (code,))
    if existing_code:
        import random
        code = f"{code[:4]}{random.randint(10, 99)}"
    return execute(
        "INSERT INTO courses (course_name, course_code, year) VALUES (%s, %s, %s)",
        (course_name.strip(), code, year)
    )


def seed_default_data():
    try:
        with connection() as conn:
            cursor = conn.cursor(dictionary=True)
            # 1. Seed courses if empty
            cursor.execute("SELECT COUNT(*) AS cnt FROM courses")
            row = cursor.fetchone()
            if row and row['cnt'] == 0:
                defaults = [
                    ("Computer Science (Core AI & Data Structures)", "CS-AIML", 3),
                    ("Information Technology & Cloud Systems", "IT-CLOUD", 2),
                    ("Bioanalytical Sciences & Instrumentation", "BIO-ANAL", 3),
                    ("Biotechnology & Molecular Genetics", "BIO-GEN", 2),
                    ("Autonomous Economics & Econometrics", "ECO-AUT", 2),
                    ("Organic & Analytical Chemistry", "CHEM-AUT", 1),
                    ("English Literature & Academic Discourse", "ENG-COMM", 1),
                    ("Physics & Applied Electronics", "PHY-ELEC", 2),
                ]
                cursor.executemany(
                    "INSERT IGNORE INTO courses (course_name, course_code, year) VALUES (%s, %s, %s)",
                    defaults
                )

            # 2. Seed demo students if empty
            cursor.execute("SELECT COUNT(*) AS cnt FROM students")
            s_row = cursor.fetchone()
            if s_row and s_row['cnt'] == 0:
                demo_students = [
                    ("Aarav Sharma", "aarav.sharma@ruiacollege.edu", "B.Sc. Computer Science (Autonomous)", 3),
                    ("Ananya Deshmukh", "ananya.deshmukh@ruiacollege.edu", "B.A. Economics (Autonomous)", 2),
                    ("Tanvi Kulkarni", "tanvi.kulkarni@ruiacollege.edu", "B.Sc. Bioanalytical Sciences", 3),
                ]
                cursor.executemany(
                    "INSERT IGNORE INTO students (name, email, program, year) VALUES (%s, %s, %s, %s)",
                    demo_students
                )
    except Exception:
        pass


def dashboard(student_id):
    with connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """SELECT a.*, c.course_name, DATEDIFF(a.due_date, CURDATE()) AS days_left 
               FROM assignments a 
               LEFT JOIN courses c ON a.course_id = c.course_id 
               WHERE a.student_id = %s AND a.status != 'Completed' AND a.due_date >= CURDATE() 
               ORDER BY a.due_date ASC LIMIT 6""",
            (student_id,)
        )
        assignments = cursor.fetchall()

        cursor.execute(
            """SELECT e.*, c.course_name, DATEDIFF(e.exam_date, CURDATE()) AS days_left 
               FROM exams e 
               LEFT JOIN courses c ON e.course_id = c.course_id 
               WHERE e.student_id = %s AND e.exam_date >= CURDATE() 
               ORDER BY e.exam_date ASC LIMIT 5""",
            (student_id,)
        )
        exams = cursor.fetchall()

        cursor.execute(
            "SELECT * FROM study_plans WHERE student_id = %s ORDER BY created_at DESC LIMIT 1",
            (student_id,)
        )
        plans = cursor.fetchall()
        plan = plans[0] if plans else None

        cursor.execute(
            "SELECT COUNT(*) AS total FROM reminders WHERE student_id = %s",
            (student_id,)
        )
        reminders_count = cursor.fetchone()
        
        return assignments, exams, plan, (reminders_count['total'] if reminders_count else 0)


def update_assignment_status(assignment_id, new_status):
    execute("UPDATE assignments SET status = %s WHERE assignment_id = %s", (new_status, assignment_id))


def delete_assignment(assignment_id):
    execute("DELETE FROM assignments WHERE assignment_id = %s", (assignment_id,))


def delete_exam(exam_id):
    execute("DELETE FROM exams WHERE exam_id = %s", (exam_id,))
