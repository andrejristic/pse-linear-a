"""Boundary Organ. In this app it registers CANDIDATE READINGS (worker units) or
SOURCES (harvest / Guardian). A reading is a transient boundary entity until it
earns absorption into the Organelle Registry. (THETA_MODES.md ENTITY MODEL)
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import numpy as np

from .. import constants as K
from .llr import single_llr, llr_step, absorption_ok, AbsorptionGate


@dataclass
class BoundaryEntity:
    entity_id: str
    representation: dict                      # the reading payload (target, value, scope...)
    theta_e: float = 0.0                      # per-reading commitment (percent)
    residency_resample: int = 0               # resample clock
    real_evidence: set = field(default_factory=set)   # ids of INDEPENDENT real tablets
    stable_count: int = 0
    mi: float = 0.0
    origin: str = "machine"                   # "machine" | "human" | source-id
    source_type: str = "internal"             # "internal" | "human-conversation" | "scraped"
    signal: str = "internal"                  # "cheap" | "costly" | "internal"
    series: list[float] = field(default_factory=list)  # theta_e over resamples
    llr_accum: float = 0.0

    @property
    def real_evidence_count(self) -> int:
        return len(self.real_evidence)

    def resample_sigma(self, window: int = K.ABSORB_STABLE_STEPS) -> float:
        s = self.series[-window:]
        return float(np.std(s)) if len(s) > 1 else 0.0


class BoundaryOrgan:
    def __init__(self):
        self.entities: dict[str, BoundaryEntity] = {}
        self.gate = AbsorptionGate()

    # cap on total boundary spend depends on the unit's current mode setpoint
    def total_theta(self) -> float:
        return sum(e.theta_e for e in self.entities.values())

    def register(self, entity_id: str, representation: dict, origin: str = "machine",
                 source_type: str = "internal", signal: str = "internal") -> BoundaryEntity:
        if entity_id in self.entities:
            return self.entities[entity_id]
        e = BoundaryEntity(entity_id, representation, origin=origin,
                           source_type=source_type, signal=signal)
        # cheap signals (bare assertions / motivated claims) enter capped low
        if signal == "cheap":
            e.theta_e = min(e.theta_e, K.CHEAP_SIGNAL_WEIGHT * 100)
        self.entities[entity_id] = e
        return e

    def observe(self, entity_id: str, p_reading: float, p_null: float,
                mi: float, real_tablet_id: Optional[str] = None,
                budget_cap: float = K.THETA_CEILING) -> BoundaryEntity:
        """One interaction = one resample test of a reading. Applies the LLR update."""
        e = self.entities[entity_id]
        lr = single_llr(p_reading, p_null)
        e.llr_accum += lr
        new = llr_step(e.theta_e, lr)
        # respect the mode budget: total boundary theta cannot exceed the setpoint budget
        headroom = max(budget_cap - (self.total_theta() - e.theta_e), 0.0)
        e.theta_e = min(new, headroom)
        e.residency_resample += 1
        e.series.append(e.theta_e)
        e.mi = mi
        if e.theta_e >= K.ABSORB_WEIGHT_MIN:
            e.stable_count += 1
        else:
            e.stable_count = 0
        if real_tablet_id is not None:
            e.real_evidence.add(real_tablet_id)
        return e

    def absorption_status(self, entity_id: str) -> tuple[bool, dict]:
        e = self.entities[entity_id]
        return absorption_ok(e.residency_resample, e.real_evidence_count, e.theta_e,
                             e.stable_count, e.mi, e.resample_sigma(), self.gate)

    def eligible(self) -> list[str]:
        return [eid for eid in self.entities if self.absorption_status(eid)[0]]

    def cap_weight(self, entity_id: str, cap: float) -> None:
        if entity_id in self.entities:
            self.entities[entity_id].theta_e = min(self.entities[entity_id].theta_e, cap)

    def expel(self, entity_id: str) -> None:
        self.entities.pop(entity_id, None)
