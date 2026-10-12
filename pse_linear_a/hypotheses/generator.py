"""Machine SELF-GENERATES testable hypotheses (non-random prior). The human may also
ask -> tagged origin='human' (prioritized, A5). Each hypothesis names its origin.
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class Hypothesis:
    ident: str
    text: str
    kind: str                     # "language-family" | "reading" | "structural"
    origin: str = "machine"       # "machine" | "human"
    prior: float = 0.1            # non-random prior of being true
    support: float = 0.0          # evidence support found during VERIFY
    motive_tag: dict | None = None
    verdict: str = "untested"     # "survived" | "refuted"
    refutation: str = ""


# candidate language families with rough priors (illustrative; refined by evidence)
LANGUAGE_FAMILIES = {
    "Anatolian/Luwian": 0.20, "Semitic": 0.15, "Greek/pre-Greek": 0.12,
    "Tyrsenian (Etruscan-related)": 0.10, "isolate/unknown": 0.25,
}


class HypothesisGenerator:
    def __init__(self, corpus, absorbed_readings: dict | None = None):
        self.corpus = corpus
        self.absorbed = absorbed_readings or {}

    def machine_hypotheses(self) -> list[Hypothesis]:
        hyps: list[Hypothesis] = []
        # language-family hypotheses
        for i, (fam, prior) in enumerate(LANGUAGE_FAMILIES.items()):
            hyps.append(Hypothesis(
                ident=f"H_lang_{i}", kind="language-family", prior=prior,
                text=f"The Minoan language of Linear A belongs to: {fam}."))
        # reading hypotheses from structural regularities not yet absorbed
        words = {}
        for t in self.corpus:
            for w in t.word_tokens():
                words[w] = words.get(w, 0) + 1
        for i, (w, c) in enumerate(sorted(words.items(), key=lambda x: -x[1])[:5]):
            hyps.append(Hypothesis(
                ident=f"H_read_{i}", kind="reading", prior=min(0.05 * c, 0.4),
                text=f'The recurring sign-group "{w}" carries a fixed administrative role.'))
        return hyps

    def human_hypothesis(self, text: str) -> Hypothesis:
        return Hypothesis(ident=f"H_human_{abs(hash(text)) % 10000}", text=text,
                          kind="reading", origin="human", prior=0.15)
