"""The four pathological attractors, detected on the RESIDUAL theta (phase-aware),
so legitimate action-phase oscillation is not misread. (Master Architecture Sec 7)
"""
from __future__ import annotations
from enum import Enum
import numpy as np

from .. import constants as K


class AttractorType(str, Enum):
    NARCISSISTIC = "narcissistic"   # <-> Circle
    BORDERLINE = "borderline"       # <-> Helix
    CODEPENDENT = "codependent"     # <-> Closing Spiral
    SCHIZOID = "schizoid"           # <-> Opening Spiral (most dangerous)
    NONE = "none"


def _acf1(x: np.ndarray) -> float:
    if x.size < 3:
        return 0.0
    x = x - x.mean()
    denom = np.sum(x * x)
    return float(np.sum(x[:-1] * x[1:]) / denom) if denom > 1e-9 else 0.0


def classify_attractor(theta_monitor, window: int = K.STABILITY_WINDOW_REAL) -> AttractorType:
    """Evaluate B, C, then S last (flatline is also consistent with under-exposure)."""
    r = theta_monitor.residuals(window)
    if r.size < 30:
        return AttractorType.NONE
    mu, sig, rho = float(np.mean(r)), float(np.std(r)), _acf1(r)
    # BORDERLINE: high variance, low autocorrelation
    if sig > K.SIGMA_HEALTHY[1] * 1.8 and rho < 0.5:
        return AttractorType.BORDERLINE
    # NARCISSISTIC: sustained high pull above setpoint, low variance
    if mu > K.THETA_BAND * 1.2 and sig < K.SIGMA_HEALTHY[0]:
        return AttractorType.NARCISSISTIC
    # CODEPENDENT: sustained low, dissolved boundary
    if mu < -K.THETA_BAND * 1.2 and sig < K.SIGMA_HEALTHY[0]:
        return AttractorType.CODEPENDENT
    # SCHIZOID last: flatline, lower variance than health itself is the signature
    if sig < K.SIGMA_SCHIZOID:
        return AttractorType.SCHIZOID
    return AttractorType.NONE
