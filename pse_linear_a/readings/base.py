"""Shared reading-engine template. All three types are the SAME LLR engine; only the
evidence channel and the null model differ (THETA_MODES.md LIKELIHOOD MODELS).

One interaction = one bootstrap-resample test. The driver tracks the running hit-rate
to derive MI (normalized advantage over the null base rate) and feeds each draw's
(p_reading, p_null, mi, real_tablet_id) into unit.observe_reading.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import random
import numpy as np


@dataclass
class Reading:
    ident: str
    reading_type: str
    target: str                  # the sign / word / sign-group
    value: str                   # proposed value / gloss / role
    scope: str = ""
    description: str = ""
    theta_e: float = 0.0
    confidence: float = 0.0
    absorbed: bool = False
    hits: int = 0
    draws: int = 0
    real_support: set = field(default_factory=set)
    origin: str = "machine"

    @property
    def hit_rate(self) -> float:
        return self.hits / self.draws if self.draws else 0.0


class ReadingEngine:
    reading_type = "base"

    def __init__(self, corpus):
        self.corpus = corpus
        self._pi0 = None

    # ---- to implement per engine ----
    def propose(self) -> list[Reading]:
        raise NotImplementedError

    def pi0(self) -> float:
        """Null base rate for this engine (permutation / base-rate)."""
        raise NotImplementedError

    def draw(self, reading: Reading, rng: random.Random):
        """Return (p_reading, p_null, hit: bool, real_tablet_id or None)."""
        raise NotImplementedError

    # ---- shared MI from running advantage over the null ----
    def mi(self, reading: Reading) -> float:
        pi0 = self.pi0()
        hr = reading.hit_rate
        return float(np.clip((hr - pi0) / max(1.0 - pi0, 1e-6), 0.0, 1.0))


def run_reading(unit, engine: ReadingEngine, reading: Reading, n_resamples: int = 1200,
                seed: int = 0) -> Reading:
    """Drive one reading through n bootstrap-resample tests on a PSE unit."""
    rng = random.Random(seed or hash(reading.ident) & 0xFFFF)
    for _ in range(n_resamples):
        p_r, p_n, hit, real_id = engine.draw(reading, rng)
        reading.draws += 1
        reading.hits += int(hit)
        if real_id is not None:
            reading.real_support.add(real_id)
        mi = engine.mi(reading)
        unit.observe_reading(reading.ident, {"target": reading.target,
                             "value": reading.value, "type": reading.reading_type},
                             p_reading=p_r, p_null=p_n, mi=mi, real_tablet_id=real_id,
                             origin=reading.origin)
    e = unit.boundary.entities.get(reading.ident)
    if e:
        reading.theta_e = e.theta_e
    reading.confidence = engine.mi(reading)
    o, _ = unit.try_absorb(reading.ident, reading.reading_type, reading.confidence)
    reading.absorbed = bool(o)
    return reading
