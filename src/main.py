import os
import json
import sqlite3
import uuid
from datetime import datetime

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse

from fastapi.middleware.cors import CORSMiddleware
from src.workflow import graph
from src.utils import extract_pdf_text ,calculate_days_remaining


DB = "src/rfp.db"

app = FastAPI(title="RFP Intelligence MVP")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <html><body>
    <h2>RFP Intelligence - Full Document Analysis</h2>
    <form action="/upload" method="post" enctype="multipart/form-data">
    <input type="file" name="file" accept=".pdf"/>
    <button type="submit">Upload & Analyze RFP</button>
    </form>
    </body></html>
    """


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    """Upload and analyze complete RFP document"""
    os.makedirs("uploads", exist_ok=True)
    path = f"uploads/{uuid.uuid4()}_{file.filename}"

    with open(path, "wb") as f:
        f.write(await file.read())

    # Extract FULL document text - no truncation
    text = extract_pdf_text(path)
    print(f"Extracted {len(text)} characters from RFP")

    initial_state = {
        "text": text,  # FULL document text
        "metadata": {},
        "total_requirements": 0,
        "technical_requirements": 0,
        "functional_requirements": 0,
        "security_requirements": 0,
        "compliance_requirements": 0,
        "compliance_score": 0,
        "risk_level": "MEDIUM",
        "risk_reasons": [],
        "win_probability": 0,
    }

    # Run complete analysis on full document
    result = graph.invoke(initial_state)
    rfp_id = str(uuid.uuid4())

    # Ensure proper data types for SQLite
    contract_value = result["metadata"].get("contract_value")
    if contract_value:
        try:
            contract_value = float(contract_value)
        except:
            contract_value = None

    # Serialize risk_reasons list to JSON string
    risk_reasons_json = json.dumps(result.get("risk_reasons", []))

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute(
        """
    INSERT INTO rfps (
        id, customer_name, rfp_title, issue_date, submission_deadline,
        contract_value, currency, stage, status, risk_level,
        risk_reasons, win_probability, total_requirements, technical_requirements,
        functional_requirements, security_requirements, compliance_requirements,
        compliance_score, days_remaining, created_at
    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """,
        (
            rfp_id,
            result["metadata"].get("customer_name"),
            result["metadata"].get("rfp_title"),
            result["metadata"].get("issue_date"),
            result["metadata"].get("submission_deadline"),
            contract_value,
            result["metadata"].get("currency", "USD"),
            "Analysis",
            "Processed",
            result.get("risk_level"),
            risk_reasons_json,
            result.get("win_probability"),
            result.get("total_requirements"),
            result.get("technical_requirements"),
            result.get("functional_requirements"),
            result.get("security_requirements"),
            result.get("compliance_requirements"),
            result.get("compliance_score"),
            calculate_days_remaining(result["metadata"].get("submission_deadline", "")),
            datetime.utcnow().isoformat(),
        ),
    )
    conn.commit()
    conn.close()

    return {
        "rfp_id": rfp_id,
        "document_size": f"{len(text)} characters",
        "metadata": result.get("metadata", {}),
        "requirements": {
            "total": result.get("total_requirements", 0),
            "technical": result.get("technical_requirements", 0),
            "functional": result.get("functional_requirements", 0),
            "security": result.get("security_requirements", 0),
            "compliance": result.get("compliance_requirements", 0),
        },
        "risk_level": result.get("risk_level", "MEDIUM"),
        "risk_reasons": result.get("risk_reasons", []),
        "compliance_score": result.get("compliance_score", 0),
        "win_probability": result.get("win_probability", 0),
    }


@app.get("/api/rfps")
def get_rfps():
    """Get all analyzed RFPs"""
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    rows = [dict(x) for x in conn.execute("select * from rfps")]
    conn.close()

    # Parse risk_reasons back from JSON
    for row in rows:
        try:
            row["risk_reasons"] = json.loads(row.get("risk_reasons", "[]"))
        except:
            row["risk_reasons"] = []

    return rows


@app.get("/api/rfps/{rfp_id}")
def get_rfp_detail(rfp_id: str):
    """Get detailed RFP analysis"""
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    row = conn.execute("select * from rfps where id = ?", (rfp_id,)).fetchone()
    conn.close()

    if row:
        result = dict(row)
        try:
            result["risk_reasons"] = json.loads(result.get("risk_reasons", "[]"))
        except:
            result["risk_reasons"] = []
        return result
    return {"error": "RFP not found"}


@app.get("/api/dashboard/kpis")
def dashboard():
    """Dashboard KPIs for all RFPs"""
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    total = cur.execute("select count(*) from rfps").fetchone()[0]
    high_risk = cur.execute(
        "select count(*) from rfps where risk_level = 'HIGH'"
    ).fetchone()[0]
    avg_compliance = cur.execute("select avg(compliance_score) from rfps").fetchone()[0]

    conn.close()

    return {
        "active_rfps": total,
        "high_risk_rfps": high_risk,
        "avg_compliance_score": round(avg_compliance, 2) if avg_compliance else 0,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
