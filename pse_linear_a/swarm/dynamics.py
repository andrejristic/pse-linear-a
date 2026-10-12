"""Swarm growth dynamics: peer-collision/dedup and fission assessment.
SharedLib controls all fission (units cannot self-initiate or resist)."""
from __future__ import annotations
from difflib import SequenceMatcher

from .. import constants as K
from ..kernel.theta import peer_setpoint


def _task_key(unit) -> str:
    m = unit.core.mission
    return f"{m.get('action','')}::{m.get('outcome','')}::{unit.role}"


def _similar(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def detect_dedup(units) -> list[tuple[str, str, float]]:
    """Find pairs of units doing (near-)identical work."""
    us = [u for u in units if u.alive]
    out = []
    for i in range(len(us)):
        for j in range(i + 1, len(us)):
            s = _similar(_task_key(us[i]), _task_key(us[j]))
            if s >= K.DEDUP_SIMILARITY:
                out.append((us[i].unit_id, us[j].unit_id, round(s, 3)))
    return out


def resolve_collision(shared_lib, unit_a_id: str, unit_b_id: str) -> dict:
    """Unit A found unit B already did the task. Peer handshake runs at peer theta
    (=0.5 x setpoint); BOTH return to SharedLib; the redundant one is harvested."""
    a = shared_lib.units.get(unit_a_id)
    b = shared_lib.units.get(unit_b_id)
    if not (a and b):
        return {"resolved": False}
    peer_theta = peer_setpoint(a.theta.mode)
    a.theta.update(peer_theta, source="game_dynamic")
    b.theta.update(peer_setpoint(b.theta.mode), source="game_dynamic")
    # keep whichever has more organelles; harvest the other
    keep, drop = (a, b) if a.organelle.count() >= b.organelle.count() else (b, a)
    shared_lib.harvest_and_terminate(drop.unit_id)
    shared_lib._log("PEER_COLLISION_DEDUP", kept=keep.unit_id, harvested=drop.unit_id,
                    peer_theta=round(peer_theta, 2))
    return {"resolved": True, "kept": keep.unit_id, "harvested": drop.unit_id,
            "peer_theta": peer_theta}


def assess_fission(unit) -> str | None:
    """Simplified S1/S3 signal on residual bimodality. Returns scenario name or None.
    Real fission needs the phase timeline to exclude action-phase oscillation."""
    r = unit.theta.residuals(K.STABILITY_WINDOW_REAL)
    if r.size < 60:
        return None
    import numpy as np
    sig = float(np.std(r))
    # unimodal sustained drift with high autocorrelation -> possible pathological (S3)
    from .pathology import classify_attractor, AttractorType
    if classify_attractor(unit.theta) in (AttractorType.SCHIZOID, AttractorType.NARCISSISTIC):
        return "S3_pathological_induction"
    if sig > K.SIGMA_HEALTHY[1] * 2:
        return "S1_aspectual_incoherence"
    return None
