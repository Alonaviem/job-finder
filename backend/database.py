import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "jobs.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id            TEXT PRIMARY KEY,
            source        TEXT,
            title         TEXT,
            company       TEXT,
            location_text TEXT,
            city          TEXT,
            lat           REAL,
            lng           REAL,
            work_model    TEXT,
            experience    TEXT,
            category      TEXT,
            salary_min    INTEGER,
            salary_max    INTEGER,
            description   TEXT,
            url           TEXT,
            posted_at     TEXT,
            scraped_at    TEXT,
            search_query  TEXT
        )
    """)
    # Migration: add category column if table existed before
    try:
        cursor.execute("ALTER TABLE jobs ADD COLUMN category TEXT")
    except Exception:
        pass
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_title    ON jobs(title)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_city     ON jobs(city)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_source   ON jobs(source)")
    conn.commit()
    conn.close()


def insert_jobs(jobs: list) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()
    inserted = 0
    for job in jobs:
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO jobs
                (id, source, title, company, location_text, city, lat, lng,
                 work_model, experience, category, salary_min, salary_max,
                 description, url, posted_at, scraped_at, search_query)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job.get("id"), job.get("source"), job.get("title"),
                job.get("company"), job.get("location_text"), job.get("city"),
                job.get("lat"), job.get("lng"), job.get("work_model"),
                job.get("experience"), job.get("category"),
                job.get("salary_min"), job.get("salary_max"),
                job.get("description"), job.get("url"), job.get("posted_at"),
                now, job.get("search_query"),
            ))
            inserted += 1
        except Exception as e:
            print(f"[DB] Insert error: {e}")
    conn.commit()
    conn.close()
    return inserted


def get_jobs(
    title: str = None,
    city: str = None,
    cities: list = None,
    experience: str = None,
    work_model: str = None,
    source: str = None,
    days: int = None,
    salary_min: int = None,
    limit: int = 200,
    offset: int = 0,
) -> list:
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM jobs WHERE 1=1"
    params = []

    if title:
        query += " AND LOWER(title) LIKE ?"
        params.append(f"%{title.lower()}%")
    # Multi-city takes priority; fall back to single city
    if cities:
        clauses = []
        for c in cities:
            clauses.append("(LOWER(city) LIKE ? OR LOWER(location_text) LIKE ?)")
            params.extend([f"%{c.lower()}%", f"%{c.lower()}%"])
        query += " AND (" + " OR ".join(clauses) + ")"
    elif city and city.lower() != "all":
        query += " AND (LOWER(city) LIKE ? OR LOWER(location_text) LIKE ?)"
        params.extend([f"%{city.lower()}%", f"%{city.lower()}%"])
    if experience:
        query += " AND experience = ?"
        params.append(experience)
    if work_model:
        query += " AND work_model = ?"
        params.append(work_model)
    if source:
        query += " AND source = ?"
        params.append(source)
    if days:
        query += " AND scraped_at >= datetime('now', ?)"
        params.append(f"-{days} days")
    if salary_min:
        query += " AND (salary_min >= ? OR salary_max >= ?)"
        params.extend([salary_min, salary_min])

    query += " ORDER BY scraped_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_cities() -> list:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT city, lat, lng, COUNT(*) as job_count
        FROM jobs
        WHERE city IS NOT NULL AND lat IS NOT NULL
        GROUP BY city
        ORDER BY job_count DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_stats() -> dict:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as total FROM jobs")
    total = cursor.fetchone()["total"]
    cursor.execute("SELECT source, COUNT(*) as count FROM jobs GROUP BY source")
    by_source = {r["source"]: r["count"] for r in cursor.fetchall()}
    cursor.execute("SELECT MAX(scraped_at) as last_updated FROM jobs")
    last_updated = cursor.fetchone()["last_updated"]
    conn.close()
    return {"total": total, "by_source": by_source, "last_updated": last_updated}
