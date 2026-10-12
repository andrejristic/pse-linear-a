"""Shared Guardian machinery. A Guardian is a PSE unit whose Boundary registers
SOURCES/SESSIONS. It keeps its OWN theta in [25,35] (not enmeshed, not asleep)."""
from __future__ import annotations
from dataclasses import dataclass, field

from .. import constants as K


@dataclass
class RiskFinding:
    source: str
    surface: str                 # "epistemic" | "cyber"
    level: int                   # BENIGN/ELEVATED/CRITICAL
    reason: str
    detail: dict = field(default_factory=dict)
    tier: str = "observe_report" # or "isolate_quarantine"

    @property
    def level_name(self) -> str:
        return {K.BENIGN: "BENIGN", K.ELEVATED: "ELEVATED", K.CRITICAL: "CRITICAL"}[self.level]


class GuardianBase:
    surface = "base"

    def __init__(self, shared_lib, guardian_id: str):
        self.sl = shared_lib
        self.guardian_id = guardian_id
        self.theta = 30.0                     # its own theta discipline
        self.findings: list[RiskFinding] = []

    def _report(self, finding: RiskFinding) -> RiskFinding:
        # NEVER talks to the other Guardian; reports only to SharedLib
        self.sl.write_threat_intel(finding.source, {
            "surface": finding.surface, "level": finding.level_name,
            "reason": finding.reason, "tier": finding.tier, "by": self.guardian_id})
        if finding.level >= K.CRITICAL and finding.tier == "isolate_quarantine":
            self.sl.queue_human_review(source=finding.source, reason=finding.reason,
                                       guardian=self.guardian_id)
        self.findings.append(finding)
        # theta discipline: engaging a threat nudges theta; keep it in band
        self.theta = min(max(self.theta, K.GUARDIAN_THETA_MIN), K.GUARDIAN_THETA_MAX)
        return finding

    def self_check(self) -> str | None:
        if self.theta > K.GUARDIAN_THETA_MAX:
            return "guardian_enmeshed"
        if self.theta < K.GUARDIAN_THETA_MIN:
            return "guardian_asleep_schizoid"
        return None
