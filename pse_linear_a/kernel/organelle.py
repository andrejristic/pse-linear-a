"""Organelle Registry: permanent, constitutive store of absorbed readings =
accumulated, earned decipherment knowledge. Absorption of a source (by a Guardian)
is a SECURITY EVENT, never routine.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

from .. import constants as K


@dataclass
class Organelle:
    entity_id: str
    representation: dict
    weight: float
    reading_type: str
    absorbed_at: int                  # logical step
    confidence: float = 0.0
    is_inherited: bool = False


class OrganelleRegistry:
    def __init__(self):
        self.organelles: dict[str, Organelle] = {}

    def total_weight(self) -> float:
        return sum(o.weight for o in self.organelles.values())

    def absorb(self, entity_id: str, representation: dict, weight: float,
               reading_type: str, step: int, confidence: float = 0.0) -> Organelle:
        o = Organelle(entity_id, representation, weight, reading_type, step, confidence)
        self.organelles[entity_id] = o
        return o

    def de_absorb(self, entity_id: str) -> Optional[Organelle]:
        """Costly, last-resort (Guardian Tier-2 analog). Logged loud by caller."""
        return self.organelles.pop(entity_id, None)

    def by_type(self, reading_type: str) -> list[Organelle]:
        return [o for o in self.organelles.values() if o.reading_type == reading_type]

    def count(self) -> int:
        return len(self.organelles)
