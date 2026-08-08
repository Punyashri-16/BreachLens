from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


# ---------- DOCUMENT MODELS ----------
# These describe the shape of what lives in MongoDB.

class Asset(BaseModel):
    id: str                          # e.g. "customer_db"
    name: str                        # e.g. "Customer Database"
    type: str                        # e.g. "database", "cloud", "identity"
    criticality: int = Field(ge=1, le=5)
    business_unit: str               # e.g. "Sales", "Engineering"
    record_count: int = 0            # 0 for systems that hold no records


class Edge(BaseModel):
    source: str                      # asset id the attacker starts from
    target: str                      # asset id they can reach
    relationship_type: str           # e.g. "credential_theft", "trust"
    weight: float = Field(gt=0, le=1)
    reason: str                      # the real-world mechanism
    mitre_technique: str             # e.g. "T1078"


class Scenario(BaseModel):
    id: str
    name: str
    description: str
    start_asset: str                 # asset id where the attack begins
    attack_type: str                 # e.g. "phishing"


class MitreTechnique(BaseModel):
    technique_id: str                # e.g. "T1078"
    name: str                        # e.g. "Valid Accounts"
    tactic: str                      # e.g. "Initial Access"
    description: str


class Incident(BaseModel):
    scenario_id: str
    start_asset: str
    attack_path: List[str] = []
    reachable_assets: List[Dict[str, Any]] = []
    risk_score: float
    blast_radius: Dict[str, Any]
    critical_assets: List[Dict[str, Any]] = []
    business_impact: Dict[str, Any]
    mitre_techniques: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Report(BaseModel):
    incident_id: str
    story: Optional[str] = None
    recommendations: Optional[List[str]] = None
    executive_summary: Optional[str] = None
    soc_summary: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ---------- REQUEST MODELS ----------
# These describe what arrives in the body of a POST request.
# FastAPI rejects anything that does not match, before your code runs.

class SimulateRequest(BaseModel):
    scenario_id: Optional[str] = None
    start_asset: Optional[str] = None


class StoryRequest(BaseModel):
    incident: Dict[str, Any]


class RecommendationsRequest(BaseModel):
    incident: Dict[str, Any]


class BobRequest(BaseModel):
    question: str
    incident: Dict[str, Any]


class CounterfactualRequest(BaseModel):
    scenario_id: Optional[str] = None
    start_asset: Optional[str] = None
    limit: int = Field(default=10, ge=1, le=50)