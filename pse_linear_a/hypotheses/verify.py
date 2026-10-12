"""VERIFY — controlled theta excursion (engage-then-return). Per No-Immunity: to test a
hypothesis honestly the unit must let it genuinely move it (theta spikes ~38), then
health = the RETURN. Non-return -> real candidate OR seduction (flag). Refutations are
harvested to SharedLib (the graveyard). (THETA_MODES.md sixth mode)
"""
from __future__ import annotations
from dataclasses import dataclass

from .. import constants as K
from ..kernel.theta import Mode
from ..llm.pse_l import PSELGenerator
from .generator import Hypothesis


@dataclass
class VerifyExcursion:
    baseline: float
    peak: float
    returned: bool
    survived: bool


def verify_hypothesis(unit, hyp: Hypothesis, support: float,
                      pse_l: PSELGenerator | None = None) -> Hypothesis:
    """support in [0,1]: how strongly the corpus backs the hypothesis (from engines/
    cross-checks). High support -> theta stays elevated (survives). Low -> returns
    (refuted, with an LLM/template explanation)."""
    pse_l = pse_l or PSELGenerator()
    baseline = unit.theta.current
    unit.enter(Mode.VERIFY)                       # spike toward the excursion peak
    peak = unit.theta.current
    hyp.support = support
    # engage: if weakly supported, theta relaxes back to baseline (refutation)
    if support >= 0.6:
        unit.theta.update(K.VERIFY_EXCURSION_PEAK, source="game_dynamic")
        returned, survived = False, True
        hyp.verdict = "survived"
    else:
        unit.theta.update(baseline, source="game_dynamic")   # RETURN
        returned, survived = True, False
        hyp.verdict = "refuted"
        rec = pse_l.refute(hyp.text,
                           f"support={support:.2f} on the current corpus (below threshold)",
                           confidence=support)
        hyp.refutation = rec["refutation"]
    hyp.excursion = VerifyExcursion(round(baseline, 2), round(peak, 2), returned, survived)
    return hyp
