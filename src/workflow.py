from datetime import datetime
from typing import TypedDict
from src.state import State
import fitz
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, END
import json

llm = ChatOllama(model="llama3.2:latest", temperature=0)

def metadata_node(state: State):
    """Extract metadata from FULL RFP document with better customer name detection"""
    prompt = f"""
Extract key metadata from this RFP document.

Customer name can appear as:
- "TO:" or "TO ALL:" 
- "Issued to:"
- Company name in letterhead
- Organization name mentioned in opening
- Contact company name

Return ONLY valid JSON (leave empty string if not found):

{{
  "customer_name": "company name if found, or empty string",
  "rfp_title": "title of the RFP",
  "issue_date": "YYYY-MM-DD format or empty",
  "submission_deadline": "YYYY-MM-DD format or empty",
  "contract_value": 0,
  "currency": "USD or other currency code"
}}

DOCUMENT:
{state['text']}
"""
    try:
        response = llm.invoke(prompt).content
        print(f"Metadata Response:\n{response}\n")  # Debug

        start = response.find("{")
        end = response.rfind("}") + 1
        state["metadata"] = json.loads(response[start:end])
    except Exception as e:
        print(f"Metadata extraction error: {e}")
        state["metadata"] = {}
    return state


def requirement_classification_node(state: State):
    """Classify ALL requirements from complete RFP document with improved extraction"""
    prompt = f"""
You are analyzing an RFP document. Extract and COUNT all requirements by type.

For each category, count EVERY requirement found, including:
- Requirements stated with "must", "should", "will", "require"
- Technical specs, integrations, APIs, databases, frameworks
- Functional behaviors, features, workflows
- Security, encryption, compliance, certifications
- Regulatory, legal, audit requirements

Be STRICT and count EVERY SINGLE requirement you find.

Return ONLY valid JSON with integer counts:

{{
    "total_requirements": <count all requirements>,
    "technical_requirements": <count technical/infrastructure requirements>,
    "functional_requirements": <count functional/feature requirements>,
    "security_requirements": <count security/encryption/access requirements>,
    "compliance_requirements": <count regulatory/compliance/audit requirements>
}}

DOCUMENT TEXT:
{state['text']}
"""
    try:
        response = llm.invoke(prompt).content
        print(f"LLM Response:\n{response}\n")  # Debug: see raw response

        start = response.find("{")
        end = response.rfind("}") + 1
        data = json.loads(response[start:end])

        # Helper function to safely convert to int
        def to_int(val):
            if isinstance(val, list):
                return int(val[0]) if val else 0
            elif isinstance(val, str):
                try:
                    return int(val)
                except:
                    return 0
            else:
                return int(val) if val else 0

        state["total_requirements"] = to_int(data.get("total_requirements", 0))
        state["technical_requirements"] = to_int(data.get("technical_requirements", 0))
        state["functional_requirements"] = to_int(
            data.get("functional_requirements", 0)
        )
        state["security_requirements"] = to_int(data.get("security_requirements", 0))
        state["compliance_requirements"] = to_int(
            data.get("compliance_requirements", 0)
        )

        # Ensure total_requirements is sum of others if it's 0
        if state["total_requirements"] == 0:
            state["total_requirements"] = (
                state["technical_requirements"]
                + state["functional_requirements"]
                + state["security_requirements"]
                + state["compliance_requirements"]
            )

    except Exception as e:
        print(f"Requirement classification error: {e}")
        # Set defaults if parsing fails
        state["total_requirements"] = 0
        state["technical_requirements"] = 0
        state["functional_requirements"] = 0
        state["security_requirements"] = 0
        state["compliance_requirements"] = 0
    return state


def compliance_node(state: State):
    """Calculate compliance score from classified requirements"""
    total = state.get("total_requirements", 0)
    if total == 0:
        state["compliance_score"] = 0
        return state

    covered = (
        state.get("technical_requirements", 0)
        + state.get("functional_requirements", 0)
        + state.get("security_requirements", 0)
    )
    state["compliance_score"] = int((covered / total) * 100)
    return state


def risk_node(state: State):
    """Analyze COMPLETE RFP for risk factors with structured scoring"""
    prompt = f"""
Analyze this RFP and assign a risk level (LOW/MEDIUM/HIGH) based on:

SCORING RULES:
- HIGH RISK if: aggressive deadline (<30 days), complex tech stack, mandatory certifications, high SLA penalties, disaster recovery required, or heavy compliance/security
- MEDIUM RISK if: moderate complexity, some certifications required, reasonable timeline
- LOW RISK if: straightforward requirements, ample timeline (>60 days), minimal compliance needs

List SPECIFIC risk factors found in the document.

Return ONLY JSON:

{{
    "risk_level": "LOW|MEDIUM|HIGH",
    "risk_reasons": [
        "specific reason 1",
        "specific reason 2",
        "specific reason 3"
    ]
}}

DOCUMENT:
{state['text']}
"""
    try:
        response = llm.invoke(prompt).content
        print(f"Risk Analysis Response:\n{response}\n")  # Debug

        start = response.find("{")
        end = response.rfind("}") + 1
        data = json.loads(response[start:end])
        state["risk_level"] = data.get("risk_level", "MEDIUM")
        state["risk_reasons"] = data.get("risk_reasons", [])
    except Exception as e:
        print(f"Risk assessment error: {e}")
        state["risk_level"] = "MEDIUM"
        state["risk_reasons"] = []
    return state


def win_probability_node(state: State):
    """Calculate win probability based on compliance and risk"""
    score = state.get("compliance_score", 0)
    risk = state.get("risk_level", "MEDIUM")
    probability = score

    if risk == "HIGH":
        probability -= 20
    elif risk == "MEDIUM":
        probability -= 10

    probability = max(0, min(probability, 100))
    state["win_probability"] = int(probability)
    return state


builder = StateGraph(State)
builder.add_node("metadata", metadata_node)
builder.add_node("requirements", requirement_classification_node)
builder.add_node("risk", risk_node)
builder.add_node("compliance", compliance_node)
builder.add_node("win_probability", win_probability_node)

builder.set_entry_point("metadata")
builder.add_edge("metadata", "requirements")
builder.add_edge("requirements", "risk")
builder.add_edge("risk", "compliance")
builder.add_edge("compliance", "win_probability")
builder.add_edge("win_probability", END)

graph = builder.compile()
