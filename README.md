# RFP Intelligence MVP

An AI-powered RFP (Request for Proposal) analysis platform that extracts metadata, classifies requirements, assesses risks, and calculates win probability using LangGraph workflows and local Ollama LLM inference.

## 🎯 Overview

This project automates the analysis of RFP documents by:
- **Extracting Metadata**: Customer name, RFP title, dates, contract value
- **Classifying Requirements**: Technical, functional, security, and compliance requirements
- **Risk Assessment**: Evaluates risk factors and assigns risk levels (LOW/MEDIUM/HIGH)
- **Compliance Scoring**: Calculates compliance coverage percentage
- **Win Probability**: Predicts win probability based on compliance and risk metrics

## 🏗️ Architecture

### Tech Stack
- **Backend**: FastAPI with Uvicorn
- **LLM**: Local Ollama model (`llama3.2:latest`)
- **Workflow Orchestration**: LangGraph StateGraph
- **Database**: SQLite
- **PDF Processing**: PyMuPDF (fitz)
- **Package Manager**: uv (Python)
- **Frontend**: HTML5 + Bootstrap + Chart.js

### Processing Workflow

```
PDF Upload
    ↓
[metadata_node] → Extract customer, title, dates, contract value
    ↓
[requirement_classification_node] → Count all requirements by type
    ↓
[risk_node] → Assess risk factors (HIGH/MEDIUM/LOW)
    ↓
[compliance_node] → Calculate compliance score
    ↓
[win_probability_node] → Compute final win probability
    ↓
SQLite Database Storage
    ↓
Dashboard Display & API Response
```

### Data Flow (State Management)

```
State TypedDict:
├── text: str (full PDF text)
├── metadata: dict
│   ├── customer_name
│   ├── rfp_title
│   ├── issue_date (YYYY-MM-DD)
│   ├── submission_deadline (YYYY-MM-DD)
│   ├── contract_value
│   └── currency
├── total_requirements: int
├── technical_requirements: int
├── functional_requirements: int
├── security_requirements: int
├── compliance_requirements: int
├── compliance_score: int (0-100)
├── risk_level: str (LOW/MEDIUM/HIGH)
├── risk_reasons: list[str]
└── win_probability: int (0-100)
```

## 📋 Requirements

- Python 3.12+
- uv (Python package manager)
- Ollama with llama3.2:latest model
- ~4GB RAM (for Ollama model inference)

## 🚀 Setup Instructions

### 1. Install Ollama and Download Model

**Download Ollama**: https://ollama.ai

**Install and run Ollama with llama3.2:latest**:
```bash
ollama pull llama3.2:latest
ollama serve
```

This will start Ollama on `http://localhost:11434` (default port).

### 2. Clone and Setup Project

```bash
cd e:\project\rfp-project
```

### 3. Install Dependencies with uv

```bash
# Install all dependencies
uv sync

# Or if using a virtual environment:
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv sync
```

### 4. Initialize Database

```bash
python -m src.table
```

This creates `src/rfp.db` with the RFPs table.

## 🎮 Running the Application

### Option 1: Terminal Commands

**Terminal 1 - Start Backend (FastAPI)**:
```bash
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

Backend API runs at: `http://localhost:8000`

**Terminal 2 - Start Frontend**:
```bash
# Using Five Server (VS Code extension)
# Or any local HTTP server from project root:
python -m http.server 8001
```

Then open dashboard: `http://localhost:8001/dashboard.html`

### Option 2: Using Existing VS Code Tasks

1. Open Command Palette: `Ctrl+Shift+P`
2. Select "Tasks: Run Task"
3. Choose "uvicorn" (backend) or "Five Server" (frontend)

## 📡 API Endpoints

### Upload & Analyze RFP
```
POST /upload
Content-Type: multipart/form-data

Body: file (PDF)

Response:
{
  "rfp_id": "uuid",
  "document_size": "X characters",
  "metadata": {...},
  "requirements": {
    "total": int,
    "technical": int,
    "functional": int,
    "security": int,
    "compliance": int
  },
  "risk_level": "LOW|MEDIUM|HIGH",
  "risk_reasons": [...],
  "compliance_score": 0-100,
  "win_probability": 0-100
}
```

### List All RFPs
```
GET /api/rfps

Response: [
  {
    "id": "uuid",
    "customer_name": "string",
    "rfp_title": "string",
    "risk_level": "LOW|MEDIUM|HIGH",
    "win_probability": 0-100,
    ...
  }
]
```

### Get RFP Details
```
GET /api/rfps/{rfp_id}

Response: {detailed RFP analysis}
```

### Dashboard KPIs
```
GET /api/dashboard/kpis

Response: {
  "active_rfps": int,
  "high_risk_rfps": int,
  "avg_compliance_score": float
}
```

## 📊 Dashboard Features

The `dashboard.html` frontend displays:

- **KPI Cards**
  - Active RFPs Count
  - High Risk RFPs Count
  - Average Compliance Score

- **RFP Table**
  - Customer Name
  - RFP Title
  - Risk Level (color-coded)
  - Win Probability
  - Compliance Score
  - Days Remaining to Deadline

- **Charts** (if multiple RFPs)
  - Requirements Distribution (pie chart)
  - Compliance vs Risk Analysis (bar chart)
  - Win Probability Trend (line chart)

- **File Upload**
  - Drag-and-drop PDF upload
  - Real-time analysis feedback

## 💡 Usage Example

### 1. Prepare an RFP Document

Example: `uploads/high_risk_rfp.pdf`
- Contains customer name, dates, requirements
- Minimum 1-2 pages recommended

### 2. Upload via Dashboard

1. Open `http://localhost:8001/dashboard.html`
2. Click "Choose File" or drag-drop PDF
3. Click "Upload & Analyze"
4. Wait for LLM analysis (~10-30s depending on document size)

### 3. View Results

- Results appear in the RFP table immediately
- View detailed analysis: Click RFP row
- Check risk factors in Risk Reasons column
- Monitor win probability score

### 4. API Usage (curl example)

```bash
# Upload RFP
curl -X POST http://localhost:8000/upload \
  -F "file=@uploads/high_risk_rfp.pdf"

# Get all RFPs
curl http://localhost:8000/api/rfps

# Get dashboard KPIs
curl http://localhost:8000/api/dashboard/kpis
```

## 🔧 Configuration

### Ollama Model

To use a different Ollama model, edit `src/workflow.py`:

```python
llm = ChatOllama(
    model="llama3.2:latest",  # Change this
    temperature=0  # 0 = deterministic, 1 = creative
)
```

Available models:
- `llama3.2:latest` (recommended - 3.2B parameters)
- `llama2:latest` (7B parameters)
- `mistral:latest` (7B parameters)

### Database Location

Edit database path in `src/table.py` and `src/main.py`:

```python
DB = "src/rfp.db"  # Change path as needed
```

## 📁 Project Structure

```
rfp-project/
├── src/
│   ├── main.py           # FastAPI backend
│   ├── workflow.py       # LangGraph workflow & LLM nodes
│   ├── state.py          # State TypedDict definition
│   ├── table.py          # Database initialization
│   ├── utils.py          # PDF extraction & date calculations
│   └── rfp.db            # SQLite database (auto-created)
├── uploads/              # Uploaded RFP PDFs
│   └── high_risk_rfp.pdf # Example document
├── dashboard.html        # Frontend UI
├── pyproject.toml        # uv dependencies
└── README.md             # This file
```

## 🧠 LLM Prompt Strategy

### Metadata Extraction
- Looks for: "TO:", "Issued to:", company names, letterheads
- Extracts dates in YYYY-MM-DD format
- Attempts to parse contract values

### Requirement Classification
- Counts requirements with "must", "should", "will", "require"
- Separates by category: technical, functional, security, compliance
- Processes full document without truncation

### Risk Assessment
- **HIGH RISK**: Aggressive deadlines (<30 days), complex tech, certifications required, high penalties, DR needed
- **MEDIUM RISK**: Moderate complexity, some certifications, reasonable timeline
- **LOW RISK**: Straightforward requirements, ample timeline (>60 days), minimal compliance

### Compliance Scoring
Formula: `(covered_requirements / total_requirements) * 100`
- Covered = technical + functional + security requirements
- Score affects win probability

### Win Probability Calculation
Base = compliance_score
- If HIGH risk: -20 points
- If MEDIUM risk: -10 points
- Final range: 0-100

## 🐛 Troubleshooting

### Issue: "Connection refused" on localhost:11434
**Solution**: Ensure Ollama is running
```bash
ollama serve
```

### Issue: "Model not found: llama3.2:latest"
**Solution**: Download the model
```bash
ollama pull llama3.2:latest
```

### Issue: Slow LLM responses
**Solution**: 
- Check system RAM (minimum 4GB needed)
- Reduce document size
- Try lighter model: `ollama pull llama3.2:1b`

### Issue: Database locked error
**Solution**: Delete `src/rfp.db` and reinitialize
```bash
python -m src.table
```

### Issue: Frontend not loading
**Solution**: Verify server running on port 8001
```bash
python -m http.server 8001
```

## 📈 Performance Notes

- **Small RFP** (1-2 pages): ~10-15 seconds analysis
- **Medium RFP** (5-10 pages): ~20-30 seconds analysis
- **Large RFP** (20+ pages): ~1-2 minutes analysis
- Bottleneck is LLM inference on local Ollama

## 🔐 Security & Privacy

- ✅ All processing runs locally (no cloud APIs)
- ✅ Ollama runs on localhost by default
- ✅ SQLite database stored locally
- ✅ No external API calls
- ⚠️ CORS enabled in FastAPI (use firewall in production)

## 📝 Sample RFP Analysis

Using `uploads/high_risk_rfp.pdf`:

```json
{
  "rfp_id": "28a9a8c0-fc7a-4039-b13f-8167e91f3269",
  "metadata": {
    "customer_name": "Acme Corporation",
    "rfp_title": "Cloud Infrastructure Solutions",
    "issue_date": "2024-12-01",
    "submission_deadline": "2024-12-20",
    "contract_value": 500000,
    "currency": "USD"
  },
  "requirements": {
    "total": 45,
    "technical": 18,
    "functional": 15,
    "security": 8,
    "compliance": 4
  },
  "risk_level": "HIGH",
  "risk_reasons": [
    "Aggressive deadline (19 days remaining)",
    "Requires SOC2 certification",
    "Complex multi-cloud architecture"
  ],
  "compliance_score": 85,
  "win_probability": 65
}
```

## 📚 Dependencies

Installed via `uv sync`:

```toml
fastapi>=0.136.3          # Web framework
langchain>=1.3.9          # LLM framework
langchain-ollama>=1.1.0   # Ollama integration
langgraph>=1.2.5          # Workflow orchestration
pydantic>=2.13.4          # Data validation
pymupdf>=1.27.2.3         # PDF extraction
python-multipart>=0.0.32  # Form data handling
uvicorn>=0.49.0           # ASGI server
```

## 🎓 Next Steps

1. **Experiment with different models**: Try `llama2`, `mistral`, `neural-chat`
2. **Add document upload history**: Track uploaded files and versions
3. **Export analysis reports**: PDF/Excel export functionality
4. **Multi-language support**: Process RFPs in different languages
5. **Enhanced UI**: Real-time progress updates, requirement details view
6. **Advanced filtering**: Filter RFPs by risk, compliance score, deadline

## 📝 License

Open source - use and modify as needed.

## 👤 Author

RFP Intelligence MVP - GenAI for RFP Analysis

---

**Last Updated**: 2026-06-13  
**Project Status**: Active Development
