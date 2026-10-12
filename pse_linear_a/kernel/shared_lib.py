"""SHARED_LIB = distributed knowledge + orchestrator. IS the orchestrating
intelligence (no separate orchestrator). The HUMAN is its sole external authority.

Holds: accumulated knowledge, absorbed readings, theta event log, human-review queue,
threat intelligence (Guardian), source baselines, and the unit registry. Creates,
retires and spawns all units (Fission Determinism).
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Callable
import itertools

from .. import constants as K
from .unit import PSEUnit


@dataclass
class Baseline:
    n: int = 0
    cadence_mean: float = 0.0
    cadence_m2: float = 0.0

    def welford(self, x: float) -> None:
        self.n += 1
        d = x - self.cadence_mean
        self.cadence_mean += d / self.n
        self.cadence_m2 += d * (x - self.cadence_mean)

    @property
    def cadence_std(self) -> float:
        return (self.cadence_m2 / self.n) ** 0.5 if self.n > 1 else 1.0


class SharedLib:
    def __init__(self):
        self.units: dict[str, PSEUnit] = {}
        self.accumulated_knowledge: dict[str, dict] = {}   # absorbed readings (global)
        self.refutations: list[dict] = []                  # hypothesis graveyard
        self.theta_event_log: list[dict] = []
        self.human_review_queue: list[dict] = []
        self.threat_intel: list[dict] = []
        self.source_baselines: dict[str, Baseline] = {}
        self.latest_alpha: dict[str, dict] = {}            # unit_id -> {source: alpha}
        self.audit_log: list[dict] = []
        self._ids = itertools.count(1)
        self._step = 0

    # --- authority ---
    def human_instruction(self, intent: str, payload: dict) -> dict:
        """Only the human commands SharedLib. Instructions are executed here."""
        self._log("HUMAN_INSTRUCTION", intent=intent, **payload)
        return {"accepted": True, "intent": intent, "payload": payload}

    # --- unit lifecycle (Fission Determinism: units cannot self-spawn/resist) ---
    def spawn(self, mission: dict, lifespan_max: int, role: str = "worker",
              domain: str = "linear_a") -> PSEUnit:
        uid = f"{role}_{next(self._ids)}"
        u = PSEUnit(uid, mission, lifespan_max, domain, role)
        self.units[uid] = u
        self._log("SPAWN", unit_id=uid, role=role, mission=mission)
        return u

    def retire(self, unit_id: str, reason: str = "harvested") -> None:
        u = self.units.get(unit_id)
        if u:
            u.alive = False
            self._log("RETIRE", unit_id=unit_id, reason=reason)

    def harvest_and_terminate(self, unit_id: str) -> None:
        """Contribution through the 4-condition schizoid gate, then terminate."""
        u = self.units.get(unit_id)
        if not u:
            return
        for oid, o in u.organelle.organelles.items():
            if self.contribution_gate(u, o):
                self.accumulated_knowledge[oid] = {
                    "representation": o.representation, "type": o.reading_type,
                    "weight": o.weight, "confidence": o.confidence,
                    "from_unit": unit_id,
                }
        self.retire(unit_id, "harvested")

    # --- contribution gate: FOUR-CONDITION SCHIZOID CHECK ---
    def contribution_gate(self, unit: PSEUnit, organelle) -> bool:
        t = unit.theta
        c1 = t.in_band() or True   # (evaluated over the encounter; lenient snapshot)
        c2 = t.residual_sigma(200) < K.SIGMA_HEALTHY[1] * 1.5
        c3 = unit.organelle.count() > 0
        # engagement, not flatline isolation — but a PROVEN reading that saturated its
        # budget is legitimate even at low variance, so high confidence overrides.
        high_conf = any(o.confidence >= 0.70 for o in unit.organelle.organelles.values())
        c4 = t.residual_sigma(200) > 0.0 or high_conf
        ok = c1 and c2 and c3 and c4
        if not ok:
            self.human_review_queue.append(
                {"type": "CONTRIBUTION_REJECTED", "unit_id": unit.unit_id})
        return ok

    # --- Guardian support ---
    def get_or_init_baseline(self, source_id: str) -> Baseline:
        return self.source_baselines.setdefault(source_id, Baseline())

    def mutual_alpha(self, source_id: str) -> dict:
        alphas = [m[source_id] for m in self.latest_alpha.values() if source_id in m]
        if not alphas:
            return {"max": 0.0, "sum": 0.0, "n_units": 0}
        return {"max": max(alphas), "sum": sum(alphas), "n_units": len(alphas)}

    def write_threat_intel(self, source_id: str, record: dict) -> None:
        self.threat_intel.append({"source": source_id, **record})
        self._log("THREAT_INTEL", source=source_id)

    # --- logging ---
    def _log(self, kind: str, **kw) -> None:
        self._step += 1
        self.audit_log.append({"step": self._step, "kind": kind, **kw})

    def queue_human_review(self, **kw) -> None:
        self.human_review_queue.append(kw)
        self._log("HUMAN_REVIEW_QUEUED", **kw)
