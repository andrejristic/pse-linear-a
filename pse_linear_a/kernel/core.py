"""Core Self: mission + lifespan, written at instantiation, never self-modified.
0.70 compute weight = the Conservation-of-Self invariant."""
from __future__ import annotations
from dataclasses import dataclass, field

from .. import constants as K


@dataclass
class CoreSelf:
    mission: dict                       # {state, action, outcome}
    lifespan_max: int
    community_tag: str = "linear_a"
    compute_weight: float = 0.70
    steps_remaining: int = 0

    def __post_init__(self):
        if self.steps_remaining == 0:
            self.steps_remaining = self.lifespan_max

    def tick(self) -> None:
        self.steps_remaining = max(0, self.steps_remaining - 1)
