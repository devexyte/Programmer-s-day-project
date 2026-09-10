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


def get_or_create_student(name, email, program, year):
    student = fetch_one("SELECT * FROM students WHERE email=%s", (email,))
    if student:
        return student
    student_id = execute(
        "INSERT INTO students (name, email, program, year) VALUES (%s, %s, %s, %s)",
        (name, email, program, year)
    )
    return fetch_one("SELECT * FROM students WHERE student_id=%s", (student_id,))


def get_all_courses():
    return fetch_all("SELECT * FROM courses ORDER BY course_name ASC")


def get_or_create_course(course_name, course_code=None, year=1):
    if not course_name:
        return None
    course = fetch_one("SELECT * FROM courses WHERE LOWER(course_name)=LOWER(%s)", (course_name.strip(),))
    if course:
        return course['course_id']
    code = course_code or course_name.strip().upper()[:6].replace(" ", "")
    existing_code = fetch_one("SELECT * FROM courses WHERE course_code=%s", (code,))
    if existing_code:
        import random
        code = f"{code[:4]}{random.randint(10, 99)}"
    return execute(
        "INSERT INTO courses (course_name, course_code, year) VALUES (%s, %s, %s)",
        (course_name.strip(), code, year)
    )


def seed_default_courses():
    try:
        with connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT COUNT(*) AS cnt FROM courses")
            row = cursor.fetchone()
            if row and row['cnt'] == 0:
                defaults = [
                    ("Artificial Intelligence & Machine Learning", "CS-AIML", 3),
                    ("Data Science & Big Data Analytics", "CS-DS301", 3),
                    ("Object-Oriented Programming (Python/Java)", "CS-OOP101", 2),
                    ("Database Management Systems & SQL", "IT-DBMS", 2),
                    ("Econometrics & Macroeconomic Theory", "ECO-201", 2),
                    ("Organic & Inorganic Chemistry", "CHEM-102", 1),
                    ("Biotechnology & Molecular Genetics", "BIO-301", 3),
                    ("English Literature & Business Communication", "ENG-101", 1),
                ]
                cursor.executemany(
                    "INSERT IGNORE INTO courses (course_name, course_code, year) VALUES (%s, %s, %s)",
                    defaults
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
