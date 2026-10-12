"""Phase 4 — CALIBRATION, the HARD CREDIBILITY GATE.

Until the system reproduces the KNOWN reading KU-RO (= total) from clean data — and
cleanly separates it from decoy words — nothing downstream is trusted. This is the
"smallest useful first step" built in as a gate (PHASES.md).
"""
from __future__ import annotations
from dataclasses import dataclass, field

from ..kernel import SharedLib
from ..readings import StructuralEngine, run_reading


@dataclass
class CalibrationReport:
    passed: bool = False
    kuro_confidence: float = 0.0
    kuro_absorbed: bool = False
    top_word: str = ""
    decoy_max_confidence: float = 0.0
    separation: float = 0.0            # kuro_conf - best decoy
    details: list[dict] = field(default_factory=list)

    def summary(self) -> str:
        v = "PASS" if self.passed else "FAIL"
        return (f"[{v}] KU-RO conf={self.kuro_confidence:.3f} absorbed={self.kuro_absorbed} "
                f"top='{self.top_word}' decoy_max={self.decoy_max_confidence:.3f} "
                f"separation={self.separation:.3f}")


def calibrate(corpus, n_resamples: int = 1200, target: str = "ku-ro",
              min_separation: float = 0.5) -> CalibrationReport:
    eng = StructuralEngine(corpus)
    sl = SharedLib()
    rows = []
    for r in eng.propose():
        u = sl.spawn({"state": "read", "action": "decipher", "outcome": "reading"}, 10 ** 6)
        u.enter("SEEK")
        run_reading(u, eng, r, n_resamples=n_resamples)
        rows.append({"word": r.target, "confidence": round(r.confidence, 4),
                     "theta_e": round(r.theta_e, 2), "absorbed": r.absorbed})
    rows.sort(key=lambda d: d["confidence"], reverse=True)
    kuro = next((d for d in rows if d["word"] == target), None)
    decoys = [d for d in rows if d["word"] != target]
    rep = CalibrationReport(details=rows)
    if kuro is None:
        return rep
    rep.kuro_confidence = kuro["confidence"]
    rep.kuro_absorbed = kuro["absorbed"]
    rep.top_word = rows[0]["word"]
    rep.decoy_max_confidence = max((d["confidence"] for d in decoys), default=0.0)
    rep.separation = rep.kuro_confidence - rep.decoy_max_confidence
    rep.passed = (rep.top_word == target and rep.kuro_absorbed
                  and rep.separation >= min_separation)
    return rep


if __name__ == "__main__":
    from ..corpus import build_seed
    print(calibrate(build_seed()).summary())
