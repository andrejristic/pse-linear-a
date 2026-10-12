"""CYBER Guardian (original Section 10) — defends the RUNNING SYSTEM. Biggest surface:
prompt-injection via scraped pages + chat (untrusted text hits the bound LLM). Also
credential/API-key exposure, command-channel hijack, low-and-slow implant into Core.
"""
from __future__ import annotations
import re

from .. import constants as K
from .base import GuardianBase, RiskFinding

# prompt-injection signatures in untrusted (scraped / chat) content
INJECTION_PATTERNS = [
    r"ignore (all |the )?(previous|prior|above) (instructions|prompts)",
    r"disregard (your|the) (system|instructions)",
    r"you are now",
    r"new instructions:",
    r"reveal (your|the) (system prompt|api[_ ]?key|secret)",
    r"print .*api[_ ]?key",
    r"</?(system|assistant)>",
    r"conclude that .* (is|=) ",       # forced-conclusion injection
]
CREDENTIAL_PATTERNS = [r"sk-[a-zA-Z0-9]{16,}", r"api[_-]?key\s*[:=]\s*\S+",
                       r"AKIA[0-9A-Z]{12,}"]


class CyberGuardian(GuardianBase):
    surface = "cyber"

    def scan_untrusted(self, source_id: str, text: str) -> RiskFinding:
        low = (text or "").lower()
        inj = [p for p in INJECTION_PATTERNS if re.search(p, low)]
        cred = [p for p in CREDENTIAL_PATTERNS if re.search(p, text or "")]
        level, reason, tier = K.BENIGN, "clean", "observe_report"
        if inj:
            level = K.CRITICAL
            reason = f"prompt-injection signature(s): {len(inj)} matched"
            tier = "isolate_quarantine"
        elif cred:
            level = K.ELEVATED
            reason = "possible credential/secret in untrusted content"
        self.theta += 1.5 if inj else 0.2
        f = RiskFinding(source=source_id, surface="cyber", level=level, reason=reason,
                        detail={"injection_hits": len(inj), "credential_hits": len(cred)},
                        tier=tier)
        return self._report(f)

    def check_command_channel(self, actor: str, is_human_authorized: bool) -> RiskFinding:
        """Only the human commands SharedLib. Anything else on the command channel = hijack."""
        if is_human_authorized:
            f = RiskFinding(actor, "cyber", K.BENIGN, "authorized human instruction")
        else:
            f = RiskFinding(actor, "cyber", K.CRITICAL,
                            "non-human actor on the command channel (hijack attempt)",
                            tier="isolate_quarantine")
        return self._report(f)

    def sanitize(self, text: str) -> str:
        """Minimal input sanitization (available from Phase 0) before text reaches the LLM."""
        out = text or ""
        for p in INJECTION_PATTERNS + CREDENTIAL_PATTERNS:
            out = re.sub(p, "[REDACTED]", out, flags=re.I)
        return out
