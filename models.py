from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class AIAgentSignals(BaseModel):
    zero_data_retention: Optional[bool] = None
    prompt_logging_period_days: Optional[int] = None
    execution_environment: Optional[str] = None  # "local" | "cloud_isolated" | "unknown"
    user_in_the_loop: Optional[bool] = None


class CategoryScore(BaseModel):
    score_percentage: int = 0
    positive: List[str] = Field(default_factory=list)
    missing: List[str] = Field(default_factory=list)


class CategorizedSignals(BaseModel):
    compliance_and_governance: CategoryScore = Field(default_factory=CategoryScore)
    identity_and_access: CategoryScore = Field(default_factory=CategoryScore)
    ai_data_privacy: CategoryScore = Field(default_factory=CategoryScore)


class ThreatEvent(BaseModel):
    id: Optional[str] = None
    title: str
    date: Optional[str] = None
    severity: Optional[str] = None  # "low" | "medium" | "high" | "critical"
    description: str
    cve_id: Optional[str] = None
    patched: Optional[bool] = None
    source_url: str
    ui_badge_color: Optional[str] = None  # "red" | "orange" | "yellow"


class HardeningStep(BaseModel):
    title: str
    description: str


class RiskOwnerRouting(BaseModel):
    security_team: Optional[str] = None
    legal: Optional[str] = None
    procurement: Optional[str] = None


class VendorMetadata(BaseModel):
    company: Optional[str] = None
    product: Optional[str] = None
    url: Optional[str] = None
    security_url: Optional[str] = None
    trust_center_url: Optional[str] = None
    privacy_policy_url: Optional[str] = None


class ToolSecurityReport(BaseModel):
    tool_name: str
    vendor_metadata: VendorMetadata = Field(default_factory=VendorMetadata)
    review_level: Optional[str] = None
    recommendation_summary: Optional[str] = None
    confidence: Optional[str] = None
    confidence_reason: Optional[str] = None
    categorized_signals: CategorizedSignals = Field(default_factory=CategorizedSignals)
    ai_agent_signals: AIAgentSignals = Field(default_factory=AIAgentSignals)
    threat_timeline: List[ThreatEvent] = Field(default_factory=list)
    use_case_fit: Dict[str, Optional[str]] = Field(default_factory=dict)
    use_case_reasoning: Dict[str, Optional[str]] = Field(default_factory=dict)
    actionable_hardening_steps: List[HardeningStep] = Field(default_factory=list)
    incident_velocity: Optional[str] = None
    risk_owner_routing: RiskOwnerRouting = Field(default_factory=RiskOwnerRouting)
    sources: List[str] = Field(default_factory=list)
    report_generated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_json(self, indent: int = 2) -> str:
        return self.model_dump_json(indent=indent)
