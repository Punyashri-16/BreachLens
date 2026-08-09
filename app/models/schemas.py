from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class Asset(BaseModel):
    id: str                          
    name: str                        
    type: str                        
    criticality: int = Field(ge=1, le=5)
    business_unit: str               
    record_count: int = 0            


class Edge(BaseModel):
    source: str                     
    target: str                                   
    weight: float = Field(gt=0, le=1)
    reason: str                      
    mitre_technique: str             


class Scenario(BaseModel):
    id: str
    name: str
    description: str
    start_asset: str                 
    attack_type: str                 


class MitreTechnique(BaseModel):
    technique_id: str                
    name: str                        
    tactic: str                      
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