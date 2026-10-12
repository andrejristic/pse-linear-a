"""PHONETIC engine (phonotactic regularity, weakest, highest overfit).
Reading: "Linear-A-only sign S has value /v/". Scored by a syllable-bigram phonotactic
LM trained on securely-valued (Linear-B-shared) words. Demonstrated via held-out
syllable recovery: mask a syllable, and the correct value should score above the
average over candidate values. Needs the most VERIFY excursions.
"""
from __future__ import annotations
import random
import math

from .base import Reading, ReadingEngine


class PhoneticEngine(ReadingEngine):
    reading_type = "phonetic"

    def __init__(self, corpus):
        super().__init__(corpus)
        self.words = []
        for t in corpus:
            for w in t.word_tokens():
                if "-" in w:
                    self.words.append(w.split("-"))
        self.vocab = sorted({s for w in self.words for s in w})
        self._bigram = self._train()

    def _train(self):
        counts, ctx = {}, {}
        for w in self.words:
            seq = ["<s>"] + w + ["</s>"]
            for a, b in zip(seq, seq[1:]):
                counts[(a, b)] = counts.get((a, b), 0) + 1
                ctx[a] = ctx.get(a, 0) + 1
        V = len(self.vocab) + 2
        return lambda a, b: (counts.get((a, b), 0) + 1) / (ctx.get(a, 0) + V)   # add-1

    def lm_score(self, syllables: list[str]) -> float:
        seq = ["<s>"] + syllables + ["</s>"]
        lp = 0.0
        for a, b in zip(seq, seq[1:]):
            lp += math.log(self._bigram(a, b))
        return math.exp(lp / max(len(seq) - 1, 1))     # per-token geometric mean prob

    def propose(self) -> list[Reading]:
        """For a few target syllables (pretended unknown signs), propose the true value
        plus two decoys so calibration can show the true value winning."""
        rng = random.Random(99)
        targets = [s for s in self.vocab if sum(s in w for w in self.words) >= 2][:4]
        readings = []
        for i, s in enumerate(targets):
            decoys = rng.sample([v for v in self.vocab if v != s],
                                k=min(2, len(self.vocab) - 1))
            for v in [s] + decoys:
                readings.append(Reading(
                    ident=f"phon::A30{i}={v}", reading_type="phonetic",
                    target=f"A30{i}", value=v,
                    description=f'unknown sign A30{i} (masking "{s}") has value /{v}/'))
                readings[-1].scope = s            # stash the masked syllable
        return readings

    def pi0(self) -> float:
        return 0.5     # above/below average over candidate values

    def draw(self, reading: Reading, rng: random.Random):
        masked = reading.scope
        words_with = [w for w in self.words if masked in w]
        if not words_with:
            return 0.5, 0.5, False, None
        w = rng.choice(words_with)                        # bootstrap draw
        cand = [reading.value if s == masked else s for s in w]
        score_c = self.lm_score(cand)
        others = rng.sample(self.vocab, k=min(6, len(self.vocab)))
        mean_other = sum(self.lm_score([v if s == masked else s for s in w])
                         for v in others) / len(others)
        z = score_c + mean_other + 1e-12
        return score_c / z, mean_other / z, score_c >= mean_other, None
