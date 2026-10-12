"""EPISTEMIC Guardian — defends the CORPUS from motivated capture. Tags FALSE/refuted
conclusions with the neighboring group (and modern descendants) that would benefit
economically/politically. HONEST LIMIT: motive != falsity (no genetic fallacy) — the
tag RAISES the VERIFY bar and EXPLAINS persistence; it never rejects on who-said-it.
"""
from __future__ import annotations

from .. import constants as K
from .base import GuardianBase, RiskFinding

# which modern actor benefits if a given language-family claim is accepted
MOTIVE_MAP = {
    "Greek/pre-Greek": {"group": "Hellenic", "modern": "Greek national narrative",
                        "interest": "cultural primacy / heritage tourism"},
    "Anatolian/Luwian": {"group": "Anatolian", "modern": "Turkish/Anatolian narrative",
                         "interest": "claim to Aegean prehistory"},
    "Semitic": {"group": "Levantine/Phoenician", "modern": "Phoenician-heritage claims",
                "interest": "priority of Semitic maritime culture"},
    "Tyrsenian (Etruscan-related)": {"group": "Tyrrhenian", "modern": "Italic/Etruscan revival",
                                     "interest": "deep-time Italic prestige"},
}


class EpistemicGuardian(GuardianBase):
    surface = "epistemic"

    def motive_tag(self, claim_family: str) -> dict | None:
        return MOTIVE_MAP.get(claim_family)

    def assess_claim(self, source_id: str, claim_family: str, signal: str,
                     verdict: str) -> RiskFinding:
        """signal: 'cheap'|'costly'. A cheap-signal claim aligned with a source's own
        interest is a red flag (down-weight), not a truth verdict."""
        motive = self.motive_tag(claim_family)
        level = K.BENIGN
        reason = "no interest-alignment"
        if motive and signal == "cheap":
            level = K.ELEVATED
            reason = (f"cheap-signal claim aligns with interest of {motive['modern']} "
                      f"({motive['interest']}) -> down-weight, raise VERIFY bar")
        self.theta += 1.0    # engaging the claim
        f = RiskFinding(source=source_id, surface="epistemic", level=level, reason=reason,
                        detail={"family": claim_family, "motive": motive, "verdict": verdict},
                        tier="observe_report")
        return self._report(f)

    def tag_refutation(self, hypothesis_family: str) -> dict | None:
        """Attach the motive explanation to a refuted conclusion (graveyard)."""
        return self.motive_tag(hypothesis_family)
