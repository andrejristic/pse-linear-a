"""theta_e evolves by the log-likelihood-ratio of evidence under reading-vs-null.
(THETA_MODES.md, LIKELIHOOD MODELS section)

    theta_e(r) += eta * log( P(evidence_t | r) / P(evidence_t | null) )

Absorption requires BOTH clocks: resample-stability AND >= k independent real tablets.
Resample-volume alone = the Opening-Spiral overfit trap.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np

from .. import constants as K


def single_llr(p_reading: float, p_null: float) -> float:
    """One evidence draw's signed log-likelihood-ratio, clamped for robustness."""
    eps = 1e-9
    lr = np.log(max(p_reading, eps) / max(p_null, eps))
    return float(np.clip(lr, -K.LLR_LOG_RATIO_CLAMP, K.LLR_LOG_RATIO_CLAMP))


def llr_step(theta_e: float, log_ratio: float, eta: float = K.LLR_ETA) -> float:
    """Update per-reading commitment; clip into [0, ceiling]."""
    return float(np.clip(theta_e + eta * log_ratio, 0.0, K.THETA_CEILING))


@dataclass
class AbsorptionGate:
    residency_resample: int = K.ABSORB_RESIDENCY_RESAMPLE
    real_evidence_min: int = K.ABSORB_REAL_EVIDENCE_MIN
    weight_min: float = K.ABSORB_WEIGHT_MIN
    stable_steps: int = K.ABSORB_STABLE_STEPS
    mi_min: float = K.ABSORB_MI_MIN
    resample_sigma_max: float = K.ABSORB_RESAMPLE_STABILITY_MAX_SIGMA


def absorption_ok(residency_resample: int, real_evidence: int, theta_e: float,
                  stable_count: int, mi: float, resample_sigma: float,
                  gate: AbsorptionGate | None = None) -> tuple[bool, dict]:
    """Return (eligible, per-criterion status). ALL must pass."""
    g = gate or AbsorptionGate()
    checks = {
        "residency_resample": residency_resample >= g.residency_resample,
        "real_evidence>=k": real_evidence >= g.real_evidence_min,
        "theta_e>=min": theta_e >= g.weight_min,
        "stable_steps": stable_count >= g.stable_steps,
        "MI>=0.70": mi >= g.mi_min,
        "resample_stability": resample_sigma <= g.resample_sigma_max,
    }
    return all(checks.values()), checks
