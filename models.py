from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from pydantic import BaseModel, Field


class SecuritySignals(BaseModel):
    soc2: Optional[bool] = None
    iso27001: Optional[bool] = None
    sso: Optional[bool] = None
    mfa: Optional[bool] = None
    rbac: Optional[bool] = None
    audit_logs: Optional[bool] = None
    encryption: Optional[bool] = None
    vulnerability_disclosure: Optional[bool] = None
    bug_bounty: Optional[bool] = None

    def merge(self, other: "SecuritySignals") -> "SecuritySignals":
        merged: dict[str, Optional[bool]] = {}
        for field in self.model_fields:
            a = getattr(self, field)
            b = getattr(other, field)
            # True wins over None; None is unknown (not False)
            if a is True or b is True:
                merged[field] = True
            elif a is False or b is False:
                merged[field] = False
            else:
                merged[field] = None
        return SecuritySignals(**merged)


class PublicIncident(BaseModel):
    date: Optional[str] = None
    title: str
    description: str
    severity: Optional[str] = None
    source_url: str


class ToolSecurityReport(BaseModel):
    tool_name: str
    company: Optional[str] = None
    product_name: Optional[str] = None
    vendor_url: Optional[str] = None
    security_page_url: Optional[str] = None
    trust_center_url: Optional[str] = None
    privacy_policy_url: Optional[str] = None
    security_signals: SecuritySignals = Field(default_factory=SecuritySignals)
    public_incidents: List[PublicIncident] = Field(default_factory=list)
    sources: List[str] = Field(default_factory=list)
    report_generated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_json(self, indent: int = 2) -> str:
        return self.model_dump_json(indent=indent)
