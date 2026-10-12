"""STRUCTURAL engine (strongest, language-free).
Reading: "word W is a SUMMATION MARKER" (the number beside W = sum of the other
line items). Null = permutation: probability a random word's number coincidentally
equals the sum of the rest. This is exactly how KU-RO was deciphered.
"""
from __future__ import annotations
import random

from .base import Reading, ReadingEngine

EPS = 0.10           # scribal-error / damage rate -> P(arith holds | reading) = 1-EPS
TOL = 1e-6


def _is_total(entry_num, others) -> bool:
    return abs(entry_num - sum(others)) <= TOL


class StructuralEngine(ReadingEngine):
    reading_type = "structural"

    def __init__(self, corpus):
        super().__init__(corpus)
        self.acc = [t for t in corpus if len(t.entries) >= 3]   # accounting tablets

    def propose(self) -> list[Reading]:
        words = {}
        for t in self.acc:
            for e in t.entries:
                words.setdefault(e.word, 0)
                words[e.word] += 1
        readings = []
        for w, cnt in words.items():
            if cnt < 2:
                continue
            readings.append(Reading(
                ident=f"struct::{w}", reading_type="structural", target=w,
                value="summation_marker",
                description=f'"{w}" marks the total (its number = sum of the other items)'))
        return readings

    def pi0(self) -> float:
        """Permutation null: over many random (tablet, word) picks, fraction where that
        word's number coincidentally equals the sum of the rest."""
        if self._pi0 is not None:
            return self._pi0
        rng = random.Random(1234)
        hits = trials = 0
        for _ in range(4000):
            t = rng.choice(self.acc)
            if len(t.entries) < 2:
                continue
            idx = rng.randrange(len(t.entries))
            others = [e.number for j, e in enumerate(t.entries) if j != idx]
            hits += int(_is_total(t.entries[idx].number, others))
            trials += 1
        self._pi0 = max(hits / trials, 1e-3) if trials else 1e-3
        return self._pi0

    def draw(self, reading: Reading, rng: random.Random):
        tablets = [t for t in self.acc if any(e.word == reading.target for e in t.entries)]
        if not tablets:
            return 0.5, 0.5, False, None
        t = rng.choice(tablets)                          # bootstrap draw
        idx = next(i for i, e in enumerate(t.entries) if e.word == reading.target)
        others = [e.number for j, e in enumerate(t.entries) if j != idx]
        hit = _is_total(t.entries[idx].number, others)
        p_reading = (1 - EPS) if hit else EPS
        p_null = self.pi0()
        return p_reading, p_null, hit, t.ident
