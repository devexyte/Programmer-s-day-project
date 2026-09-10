import os
from contextlib import contextmanager
from datetime import date
import mysql.connector
from mysql.connector import Error


def _config():
    return {"host": os.getenv("MYSQL_HOST", "localhost"), "port": int(os.getenv("MYSQL_PORT", "3306")),
            "user": os.getenv("MYSQL_USER", "root"), "password": os.getenv("MYSQL_PASSWORD", ""),
            "database": os.getenv("MYSQL_DATABASE", "ruia_companion")}


@contextmanager
def connection():
    conn = mysql.connector.connect(**_config())
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


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
    student_id = execute("INSERT INTO students (name,email,program,year) VALUES (%s,%s,%s,%s)", (name, email, program, year))
    return fetch_one("SELECT * FROM students WHERE student_id=%s", (student_id,))


def dashboard(student_id):
    assignments = fetch_all("SELECT a.*, c.course_name FROM assignments a LEFT JOIN courses c ON a.course_id=c.course_id WHERE a.student_id=%s AND a.status!='Completed' AND a.due_date>=CURDATE() ORDER BY a.due_date LIMIT 5", (student_id,))
    exams = fetch_all("SELECT e.*, c.course_name, DATEDIFF(e.exam_date,CURDATE()) AS days_left FROM exams e LEFT JOIN courses c ON e.course_id=c.course_id WHERE e.student_id=%s AND e.exam_date>=CURDATE() ORDER BY e.exam_date LIMIT 4", (student_id,))
    plan = fetch_one("SELECT * FROM study_plans WHERE student_id=%s ORDER BY created_at DESC LIMIT 1", (student_id,))
    return assignments, exams, plan

