import sqlite3

DB = "rfp.db"
def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
CREATE TABLE IF NOT EXISTS rfps(
    id TEXT PRIMARY KEY,
    customer_name TEXT,
    rfp_title TEXT,
    issue_date TEXT,
    submission_deadline TEXT,
    contract_value REAL,
    currency TEXT,
    stage TEXT,
    status TEXT,
    risk_level TEXT,
    risk_reasons TEXT,
    win_probability INTEGER,
    total_requirements INTEGER,
    technical_requirements INTEGER,
    functional_requirements INTEGER,
    security_requirements INTEGER,
    compliance_requirements INTEGER,
    compliance_score INTEGER,
    days_remaining INTEGER,
    created_at TEXT
)
""")
    conn.commit()
    conn.close()


init_db()
