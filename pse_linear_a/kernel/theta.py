"""theta = other-directed compute %, action-dependent setpoint. (THETA_MODES.md)

theta is a property of the ACTION, not the agent. A unit slides its setpoint across
a work cycle: SEEK(40) -> BUILD(20) -> report/ORCH(10). Pathology tests run on the
RESIDUAL (theta - setpoint(current phase)), so phase-driven oscillation is not read
as aspectual incoherence.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import numpy as np

from .. import constants as K


class Mode(str, Enum):
    SEEK = "SEEK"
    CARE = "CARE"
    BUILD = "BUILD"
    ORCH = "ORCH"
    VERIFY = "VERIFY"   # excursion, not a flat setpoint


def setpoint(mode: Mode | str) -> float:
    m = mode.value if isinstance(mode, Mode) else mode
    if m == "VERIFY":
        return K.VERIFY_EXCURSION_PEAK
    return K.THETA_SETPOINTS[m]


def peer_setpoint(mode: Mode | str) -> float:
    """Peer-directed theta = 0.5 x current setpoint (recovers COLLABORATIVE_BUDGET
    0.15 as the CARE case)."""
    return K.PEER_FACTOR * setpoint(mode)


def band_for(mode: Mode | str) -> tuple[float, float]:
    c = setpoint(mode)
    return (c - K.THETA_BAND, c + K.THETA_BAND)


@dataclass
class ThetaEvent:
    value: float
    source: str            # theta-source taxonomy; "unknown" x3 -> human review
    mode: str
    entity_id: Optional[str] = None


@dataclass
class ThetaMonitor:
    """Global theta of a unit = sum of per-reading theta_e, tracked toward the mode
    setpoint. Keeps a phase timeline so residual pathology tests are phase-aware."""
    current: float = K.THETA_SETPOINTS["CARE"]
    mode: str = "CARE"
    history: list[float] = field(default_factory=list)
    mode_timeline: list[str] = field(default_factory=list)   # mode active at each step
    sources: list[str] = field(default_factory=list)
    consecutive_unknown: int = 0

    def set_mode(self, mode: Mode | str) -> None:
        self.mode = mode.value if isinstance(mode, Mode) else mode

    def update(self, value: float, source: str = "game_dynamic",
               entity_id: Optional[str] = None) -> ThetaEvent:
        self.current = float(np.clip(value, 0.0, K.THETA_CEILING))
        self.history.append(self.current)
        self.mode_timeline.append(self.mode)
        self.sources.append(source)
        self.consecutive_unknown = self.consecutive_unknown + 1 if source == "unknown" else 0
        return ThetaEvent(self.current, source, self.mode, entity_id)

    # --- diagnostics (phase-aware) ---
    def residuals(self, window: int = 0) -> np.ndarray:
        h = self.history[-window:] if window else self.history
        m = self.mode_timeline[-window:] if window else self.mode_timeline
        if not h:
            return np.array([])
        sp = np.array([setpoint(mode) for mode in m])
        return np.array(h) - sp

    def residual_sigma(self, window: int = 0) -> float:
        r = self.residuals(window)
        return float(np.std(r)) if r.size > 1 else 0.0

    def residual_mean(self, window: int = 0) -> float:
        r = self.residuals(window)
        return float(np.mean(r)) if r.size else 0.0

    def in_band(self) -> bool:
        lo, hi = band_for(self.mode)
        return lo <= self.current <= hi
