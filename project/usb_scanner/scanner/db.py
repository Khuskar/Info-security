import sqlite3
from datetime import datetime
from typing import Optional

DB_PATH = "scanner.db"

def _ensure_columns(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(scans)")
    cols = {row[1] for row in cur.fetchall()}

    if 'is_pe' not in cols:
        cur.execute("ALTER TABLE scans ADD COLUMN is_pe INTEGER DEFAULT 0")
    if 'entropy' not in cols:
        cur.execute("ALTER TABLE scans ADD COLUMN entropy REAL")
    if 'pe_timestamp' not in cols:
        cur.execute("ALTER TABLE scans ADD COLUMN pe_timestamp INTEGER")
    if 'pe_imports' not in cols:
        cur.execute("ALTER TABLE scans ADD COLUMN pe_imports INTEGER")
    conn.commit()

def init_db(db_path: Optional[str] = None):
    path = db_path or DB_PATH
    conn = sqlite3.connect(path, timeout=30, check_same_thread=False)
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS scans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        path TEXT NOT NULL,
        filename TEXT NOT NULL,
        sha256 TEXT,
        size INTEGER,
        triggered_rules TEXT,
        action_taken TEXT,
        timestamp TEXT
    )
    ''')
    conn.commit()

    _ensure_columns(conn)
    return conn

def insert_scan(conn: sqlite3.Connection, path: str, filename: str, sha256: str,
                size: int, triggered_rules: str, is_pe: int = 0,
                entropy: float = None, action_taken: str = None,
                pe_timestamp: int = None, pe_imports: int = None):
    cur = conn.cursor()
    cur.execute('''
    INSERT INTO scans
      (path, filename, sha256, size, triggered_rules, is_pe, entropy, action_taken, pe_timestamp, pe_imports, timestamp)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (path, filename, sha256, size, triggered_rules, is_pe, entropy, action_taken, pe_timestamp, pe_imports, datetime.utcnow().isoformat()))
    conn.commit()
    return cur.lastrowid