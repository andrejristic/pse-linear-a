"""LEXICAL engine (collocation / pointwise-MI).
Reading: "word W belongs to semantic class of logogram L" (e.g. W ~ wine).
p_reading = P(L present | W); p_null = base rate of L. LLR accumulation = pointwise MI.
Cross-linguistic cognate matches are deliberately NOT used here (weak, prior-dependent).
"""
from __future__ import annotations
import random

from .base import Reading, ReadingEngine


class LexicalEngine(ReadingEngine):
    reading_type = "lexical"

    def __init__(self, corpus):
        super().__init__(corpus)
        self.occurrences = []           # (word, logogram or None, ident)
        self.logo_counts = {}
        self.total = 0
        for t in corpus:
            for e in t.entries:
                self.occurrences.append((e.word, e.logogram, t.ident))
                self.total += 1
                if e.logogram:
                    self.logo_counts[e.logogram] = self.logo_counts.get(e.logogram, 0) + 1

    def base_rate(self, logogram: str) -> float:
        return max(self.logo_counts.get(logogram, 0) / max(self.total, 1), 1e-3)

    def propose(self) -> list[Reading]:
        pairs = {}
        for w, logo, _ in self.occurrences:
            if logo:
                pairs.setdefault((w, logo), 0)
                pairs[(w, logo)] += 1
        readings = []
        for (w, logo), cnt in pairs.items():
            if cnt < 2:
                continue
            readings.append(Reading(
                ident=f"lex::{w}->{logo}", reading_type="lexical", target=w, value=logo,
                description=f'"{w}" denotes / co-indexes {logo}'))
        return readings

    def pi0(self) -> float:
        return 0.0   # MI normalized per-reading against that logogram's base rate

    def mi(self, reading: Reading) -> float:
        pi0 = self.base_rate(reading.value)
        hr = reading.hit_rate
        import numpy as np
        return float(np.clip((hr - pi0) / max(1.0 - pi0, 1e-6), 0.0, 1.0))

    def draw(self, reading: Reading, rng: random.Random):
        occ = [o for o in self.occurrences if o[0] == reading.target]
        if not occ:
            return 0.5, 0.5, False, None
        w, logo, ident = rng.choice(occ)                  # bootstrap draw
        hit = (logo == reading.value)
        b = self.base_rate(reading.value)
        p_reading = 0.85 if hit else 0.15
        p_null = b if hit else (1 - b)
        return p_reading, p_null, hit, ident
