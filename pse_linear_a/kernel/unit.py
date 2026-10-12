"""PSE Unit = (Core, Boundary, Organelle, Theta). Any missing = death."""
from __future__ import annotations
from typing import Optional

from .. import constants as K
from .core import CoreSelf
from .boundary import BoundaryOrgan
from .organelle import OrganelleRegistry
from .theta import ThetaMonitor, Mode, setpoint


class PSEUnit:
    def __init__(self, unit_id: str, mission: dict, lifespan_max: int,
                 domain: str = "linear_a", role: str = "worker"):
        self.unit_id = unit_id
        self.role = role
        self.core = CoreSelf(mission, lifespan_max, community_tag=domain)
        self.boundary = BoundaryOrgan()
        self.organelle = OrganelleRegistry()
        self.theta = ThetaMonitor(current=setpoint("CARE"), mode="CARE")
        self.alive = True
        self._step = 0

    # --- mode / phase ---
    def enter(self, mode: Mode | str) -> None:
        self.theta.set_mode(mode)
        # nudge global theta toward the new setpoint (phase transition)
        self.theta.update(setpoint(mode), source="internal_drift")

    def budget(self) -> float:
        """Boundary spend cap for the current action = the mode setpoint."""
        return setpoint(self.theta.mode)

    # --- one interaction (resample test of a reading) ---
    def observe_reading(self, reading_id: str, representation: dict, p_reading: float,
                        p_null: float, mi: float, real_tablet_id: Optional[str] = None,
                        origin: str = "machine", source_type: str = "internal",
                        signal: str = "internal"):
        if not self.alive:
            raise RuntimeError("Dead unit cannot interact")
        if reading_id not in self.boundary.entities:
            self.boundary.register(reading_id, representation, origin, source_type, signal)
        e = self.boundary.observe(reading_id, p_reading, p_null, mi, real_tablet_id,
                                  budget_cap=self.budget())
        # global theta = sum of per-reading commitments, tracked toward setpoint budget
        self.theta.update(min(self.boundary.total_theta(), K.THETA_CEILING),
                          source="game_dynamic", entity_id=reading_id)
        self._step += 1
        self.core.tick()
        return e

    def try_absorb(self, reading_id: str, reading_type: str, confidence: float):
        ok, checks = self.boundary.absorption_status(reading_id)
        if not ok:
            return None, checks
        e = self.boundary.entities[reading_id]
        o = self.organelle.absorb(reading_id, e.representation, e.theta_e,
                                  reading_type, self._step, confidence)
        self.boundary.expel(reading_id)
        return o, checks

    def snapshot(self) -> dict:
        return {
            "unit_id": self.unit_id, "role": self.role, "alive": self.alive,
            "mode": self.theta.mode, "theta": round(self.theta.current, 2),
            "residual_sigma": round(self.theta.residual_sigma(200), 3),
            "boundary": len(self.boundary.entities),
            "organelles": self.organelle.count(),
            "steps_remaining": self.core.steps_remaining,
        }
