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