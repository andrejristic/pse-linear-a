"""Phase 9 — State of Knowledge: a READ-ONLY living document, regenerated on every
VERIFIED learning event. Calibrated & conditional (never "Linear A says X"), append-only
+ timestamped (audit), each claim traceable to the readings that support it.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone

from ..llm.pse_l import PSELGenerator

TRUE_CONF = 0.70          # absorbed + confidence above this -> probably true
UNCERTAIN_CONF = 0.30


@dataclass
class KnowledgeVersion:
    version: int
    timestamp: str
    probably_true: list[dict]
    probably_false: list[dict]
    uncertain: list[dict]
    prose: str

    def render(self) -> str:
        def block(title, items, fmt):
            lines = [f"## {title}"]
            lines += [fmt(i) for i in items] or ["- (none yet)"]
            return "\n".join(lines)
        return (f"# State of Knowledge — Linear A  (v{self.version}, {self.timestamp})\n"
                f"_Read-only. Calibrated and conditional. Traceable to readings._\n\n"
                + block("Probably TRUE", self.probably_true,
                        lambda i: f"- {i['claim']}  _(conf {i['confidence']:.2f}; {i['trace']})_") + "\n\n"
                + block("Probably FALSE", self.probably_false,
                        lambda i: f"- {i['claim']}  _({i.get('motive','no motive-alignment')})_") + "\n\n"
                + block("UNCERTAIN", self.uncertain,
                        lambda i: f"- {i['claim']}  _(conf {i['confidence']:.2f})_") + "\n\n"
                + "## Summary\n" + self.prose + "\n")


class StateOfKnowledge:
    """Append-only. Never mutates a prior version."""
    def __init__(self, pse_l: PSELGenerator | None = None):
        self.pse_l = pse_l or PSELGenerator()
        self.versions: list[KnowledgeVersion] = []

    def regenerate(self, shared_lib, refutations: list[dict],
                   candidate_readings: list[dict] | None = None,
                   now: str | None = None) -> KnowledgeVersion:
        true_, false_, unc = [], [], []
        for oid, k in shared_lib.accumulated_knowledge.items():
            claim = self._claim(k)
            entry = {"claim": claim, "confidence": k.get("confidence", 0.0),
                     "trace": f"reading {oid}"}
            (true_ if k.get("confidence", 0) >= TRUE_CONF else unc).append(entry)
        for r in refutations:
            false_.append({"claim": r["hypothesis"], "motive": self._motive(r),
                           "refutation": r.get("refutation", "")})
        for c in (candidate_readings or []):
            if UNCERTAIN_CONF <= c.get("confidence", 0) < TRUE_CONF:
                unc.append({"claim": c["claim"], "confidence": c["confidence"]})
        prose = self.pse_l.state_of_knowledge(
            [t["claim"] for t in true_], [f["claim"] for f in false_],
            [u["claim"] for u in unc])
        v = KnowledgeVersion(
            version=len(self.versions) + 1,
            timestamp=now or datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ"),
            probably_true=true_, probably_false=false_, uncertain=unc, prose=prose)
        self.versions.append(v)                      # append-only
        shared_lib._log("STATE_OF_KNOWLEDGE_REGENERATED", version=v.version,
                        n_true=len(true_), n_false=len(false_))
        return v

    @staticmethod
    def _claim(k: dict) -> str:
        rep = k.get("representation", {})
        t = k.get("type")
        if t == "structural":
            return f'"{rep.get("target")}" functions as {rep.get("value")}'
        if t == "lexical":
            return f'"{rep.get("target")}" denotes {rep.get("value")}'
        if t == "phonetic":
            return f'sign {rep.get("target")} has value /{rep.get("value")}/'
        return str(rep)

    @staticmethod
    def _motive(r: dict) -> str:
        m = r.get("motive_tag")
        if not m:
            return "no interest-alignment"
        return f"persistence explained by interest: {m.get('modern')} ({m.get('interest')})"

    @property
    def latest(self) -> KnowledgeVersion | None:
        return self.versions[-1] if self.versions else None
