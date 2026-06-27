"""
SQLite persistence layer for the Municipal Service (Citizen Grievance) app.

to Handles users, grievances, status history, and upvotes.+
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "grievance_app.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create all tables if they do not already exist."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            mobile TEXT UNIQUE NOT NULL,
            ward TEXT,
            city TEXT,
            language TEXT DEFAULT 'en',
            points INTEGER DEFAULT 0,
            created_at TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS grievances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            grievance_code TEXT UNIQUE NOT NULL,
            mobile TEXT,
            name TEXT,
            category TEXT,
            description TEXT,
            lat REAL,
            lng REAL,
            address TEXT,
            ward TEXT,
            city TEXT,
            photo_path TEXT,
            priority TEXT DEFAULT 'Medium',
            department TEXT,
            status TEXT DEFAULT 'Submitted',
            upvote_count INTEGER DEFAULT 0,
            created_at TEXT,
            updated_at TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS status_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            grievance_code TEXT NOT NULL,
            status TEXT,
            remark TEXT,
            updated_by TEXT,
            timestamp TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS upvotes (
            grievance_code TEXT NOT NULL,
            mobile TEXT NOT NULL,
            PRIMARY KEY (grievance_code, mobile)
        )
    """)

    conn.commit()
    conn.close()


def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Users

def upsert_user(name, mobile, ward="", city="", language="en"):
    conn = get_connection()
    cur = conn.cursor()
    existing = cur.execute("SELECT * FROM users WHERE mobile = ?", (mobile,)).fetchone()
    if existing:
        cur.execute(
            "UPDATE users SET name = ?, ward = ?, city = ?, language = ? WHERE mobile = ?",
            (name, ward, city, language, mobile),
        )
    else:
        cur.execute(
            "INSERT INTO users (name, mobile, ward, city, language, points, created_at) "
            "VALUES (?, ?, ?, ?, ?, 0, ?)",
            (name, mobile, ward, city, language, now_str()),
        )
    conn.commit()
    conn.close()


def get_user(mobile):
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE mobile = ?", (mobile,)).fetchone()
    conn.close()
    return dict(row) if row else None


def add_points(mobile, points):
    conn = get_connection()
    conn.execute("UPDATE users SET points = points + ? WHERE mobile = ?", (points, mobile))
    conn.commit()
    conn.close()


def user_leaderboard(limit=10):
    conn = get_connection()
    rows = conn.execute(
        "SELECT name, mobile, ward, city, points FROM users ORDER BY points DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def ward_leaderboard(limit=10):
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT ward, SUM(points) as total_points, COUNT(*) as citizen_count
        FROM users
        WHERE ward IS NOT NULL AND ward != ''
        GROUP BY ward
        ORDER BY total_points DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# Grievances

def _next_grievance_code():
    """Generate a government-file-style code, e.g. MCG-2026-000123."""
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) as c FROM grievances").fetchone()["c"]
    conn.close()
    year = datetime.now().year
    return f"MCG-{year}-{count + 1:06d}"


def create_grievance(mobile, name, category, description, lat, lng, address,
                      ward, city, photo_path, priority, department):
    code = _next_grievance_code()
    conn = get_connection()
    cur = conn.cursor()
    ts = now_str()
    cur.execute(
        """
        INSERT INTO grievances
        (grievance_code, mobile, name, category, description, lat, lng, address,
         ward, city, photo_path, priority, department, status, upvote_count,
         created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Submitted', 0, ?, ?)
        """,
        (code, mobile, name, category, description, lat, lng, address,
         ward, city, photo_path, priority, department, ts, ts),
    )
    cur.execute(
        "INSERT INTO status_history (grievance_code, status, remark, updated_by, timestamp) "
        "VALUES (?, 'Submitted', 'Grievance registered by citizen.', ?, ?)",
        (code, name or mobile, ts),
    )
    conn.commit()
    conn.close()
    return code

def get_grievance_by_code(code):
    conn = get_connection()
    row = conn.execute("SELECT * FROM grievances WHERE grievance_code = ?", (code,)).fetchone()
    conn.close()
    return dict(row) if row else None

def get_grievances_by_mobile(mobile):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM grievances WHERE mobile = ? ORDER BY created_at DESC", (mobile,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def list_grievances(category=None, status=None, ward=None, city=None):
    query = "SELECT * FROM grievances WHERE 1=1"
    params = []
    if category and category != "All":
        query += " AND category = ?"
        params.append(category)
    if status and status != "All":
        query += " AND status = ?"
        params.append(status)
    if ward:
        query += " AND ward LIKE ?"
        params.append(f"%{ward}%")
    if city:
        query += " AND city LIKE ?"
        params.append(f"%{city}%")
    query += " ORDER BY created_at DESC"

    conn = get_connection()
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_status(code, new_status, remark, updated_by):
    conn = get_connection()
    ts = now_str()
    conn.execute(
        "UPDATE grievances SET status = ?, updated_at = ? WHERE grievance_code = ?",
        (new_status, ts, code),
    )
    conn.execute(
        "INSERT INTO status_history (grievance_code, status, remark, updated_by, timestamp) "
        "VALUES (?, ?, ?, ?, ?)",
        (code, new_status, remark, updated_by, ts),
    )
    conn.commit()
    conn.close()

def update_photo_path(code, photo_path):
    conn = get_connection()
    conn.execute(
        "UPDATE grievances SET photo_path = ? WHERE grievance_code = ?", (photo_path, code)
    )
    conn.commit()
    conn.close()

def update_department(code, department):
    conn = get_connection()
    conn.execute(
        "UPDATE grievances SET department = ?, updated_at = ? WHERE grievance_code = ?",
        (department, now_str(), code),
    )
    conn.commit()
    conn.close()

def get_status_history(code):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM status_history WHERE grievance_code = ? ORDER BY timestamp ASC", (code,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def find_nearby(lat, lng, category, radius_km=0.3):
    """Return open grievances of the same category within radius_km."""
    from utils import haversine

    if lat is None or lng is None:
        return []
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM grievances WHERE category = ? AND status NOT IN ('Resolved', 'Closed', 'Rejected') "
        "AND lat IS NOT NULL AND lng IS NOT NULL",
        (category,),
    ).fetchall()
    conn.close()
    nearby = []
    for r in rows:
        d = haversine(lat, lng, r["lat"], r["lng"])
        if d <= radius_km:
            item = dict(r)
            item["distance_km"] = round(d, 3)
            nearby.append(item)
    nearby.sort(key=lambda x: x["distance_km"])
    return nearby

def add_upvote(code, mobile):
    """Returns True if upvote was newly added, False if already upvoted."""
    conn = get_connection()
    try:
        conn.execute("INSERT INTO upvotes (grievance_code, mobile) VALUES (?, ?)", (code, mobile))
        conn.execute(
            "UPDATE grievances SET upvote_count = upvote_count + 1 WHERE grievance_code = ?",
            (code,),
        )
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False
    conn.close()
    return success

def has_upvoted(code, mobile):
    conn = get_connection()
    row = conn.execute(
        "SELECT 1 FROM upvotes WHERE grievance_code = ? AND mobile = ?", (code, mobile)
    ).fetchone()
    conn.close()
    return row is not None

def get_stats():
    conn = get_connection()
    total = conn.execute("SELECT COUNT(*) as c FROM grievances").fetchone()["c"]
    resolved = conn.execute(
        "SELECT COUNT(*) as c FROM grievances WHERE status = 'Resolved'"
    ).fetchone()["c"]
    pending = conn.execute(
        "SELECT COUNT(*) as c FROM grievances WHERE status NOT IN ('Resolved', 'Closed', 'Rejected')"
    ).fetchone()["c"]
    by_category = conn.execute(
        "SELECT category, COUNT(*) as c FROM grievances GROUP BY category ORDER BY c DESC"
    ).fetchall()
    by_status = conn.execute(
        "SELECT status, COUNT(*) as c FROM grievances GROUP BY status"
    ).fetchall()
    conn.close()
    return {
        "total": total,
        "resolved": resolved,
        "pending": pending,
        "by_category": [dict(r) for r in by_category],
        "by_status": [dict(r) for r in by_status],
    }
