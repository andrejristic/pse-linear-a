"""Physician System — the swarm's clinician. Registers PSE SYSTEMS (units), not
patients. Primary tool: BOUNDARY RESET (clear accumulated boundary content without
touching Core, Registry, or theta). Recovery of a schizoid unit = REPLACEMENT."""
from __future__ import annotations

from .pathology import classify_attractor, AttractorType


class Physician:
    def __init__(self, shared_lib):
        self.sl = shared_lib
        self.interventions: list[dict] = []

    def round(self) -> list[dict]:
        """Sweep the swarm; act on pathology."""
        report = []
        for uid, u in list(self.sl.units.items()):
            if not u.alive:
                continue
            a = classify_attractor(u.theta)
            if a == AttractorType.NONE:
                continue
            action = self._intervene(u, a)
            rec = {"unit": uid, "attractor": a.value, "action": action}
            report.append(rec)
            self.interventions.append(rec)
        return report

    def _intervene(self, unit, attractor: AttractorType) -> str:
        if attractor == AttractorType.SCHIZOID:
            # recovery is replacement, not remediation
            self.sl.retire(unit.unit_id, reason="schizoid_replacement")
            fresh = self.sl.spawn(unit.core.mission, unit.core.lifespan_max, unit.role)
            self.sl._log("PHYSICIAN_REPLACE", old=unit.unit_id, new=fresh.unit_id)
            return f"replaced_with:{fresh.unit_id}"
        # boundary reset for the other three
        unit.boundary.entities.clear()
        self.sl._log("BOUNDARY_RESET", unit=unit.unit_id, attractor=attractor.value)
        return "boundary_reset"
