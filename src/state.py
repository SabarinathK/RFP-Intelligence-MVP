

from typing import TypedDict


class State(TypedDict):
    text: str
    metadata: dict
    total_requirements: int
    technical_requirements: int
    functional_requirements: int
    security_requirements: int
    compliance_requirements: int
    compliance_score: int
    risk_level: str
    risk_reasons: list
    win_probability: int
