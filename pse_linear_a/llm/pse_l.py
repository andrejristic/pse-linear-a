"""PSE-L generator — the ONLY place natural language is produced for a human.
Enforces I-4/I-5 (no strategic naming, domain language only) via a forbidden-terms
list and I-6 (suppress below confidence 0.3). Works OFFLINE via template fallbacks so
the app is fully functional without an LLM.
"""
from __future__ import annotations

from .providers import LLMProvider, get_provider

FORBIDDEN_TERMS = ["game", "strategy", "attrition", "chicken", "nash", "equilibrium",
                   "prisoner", "signalling", "hawk", "dove", "auction", "bargaining",
                   "war of attrition", "adversary"]

CONFIDENCE_SUPPRESS = 0.30


def _scrub(text: str) -> str:
    low = text.lower()
    for t in FORBIDDEN_TERMS:
        if t in low:
            # soft redaction rather than leaking strategic framing to a human
            import re
            text = re.compile(re.escape(t), re.I).sub("[dynamic]", text)
    return text


class PSELGenerator:
    def __init__(self, provider: LLMProvider | None = None):
        self.provider = provider or get_provider("local_gguf")

    def _try_llm(self, system: str, user: str, max_tokens: int = 300) -> str | None:
        out = self.provider.complete(system, user, max_tokens)
        return _scrub(out) if out else None

    # --- refutation: "why this hypothesis falls in water" ---
    def refute(self, hypothesis: str, evidence_summary: str, confidence: float) -> dict:
        system = ("You are the language layer of a decipherment system for Linear A. "
                  "Explain, in careful epigraphic language, in 2-4 sentences, why the given "
                  "hypothesis is not supported by the evidence. Be conditional and calibrated; "
                  "never make unconditional claims.")
        user = f"Hypothesis: {hypothesis}\nEvidence against: {evidence_summary}"
        llm = self._try_llm(system, user)
        text = llm or (f"The hypothesis '{hypothesis}' is not supported: {evidence_summary}. "
                       f"On the available corpus the pattern does not hold above chance, so the "
                       f"reading cannot presently be sustained.")
        return {"hypothesis": hypothesis, "refutation": text,
                "confidence": round(confidence, 3), "via": "llm" if llm else "template"}

    # --- prognosis / advisory ---
    def prognosis(self, target: str, role: str, confidence: float, domain: str = "linear_a") -> str | None:
        if confidence < CONFIDENCE_SUPPRESS:
            return None
        system = (f"You are the communication layer of a Linear A decipherment system. "
                  f"Produce ONE to THREE sentences in epigraphic language. Confidence "
                  f"{confidence:.2f}. Never make unconditional predictions; uncertainty must "
                  f"be present in the phrasing. Do not use strategic framing.")
        user = f"Structural role under consideration for '{target}': {role}."
        llm = self._try_llm(system, user, 150)
        return llm or (f"'{target}' appears, with confidence {confidence:.2f}, to function "
                       f"as {role}; further attestations would be needed to confirm.")

    # --- advisory chat answer ---
    def advise(self, question: str, context: str) -> str:
        system = ("You are a Linear A / Linear B advisor. Answer briefly, in epigraphic "
                  "language, calibrated and honest about uncertainty. Linear A is undeciphered.")
        llm = self._try_llm(system, f"Context:\n{context}\n\nQuestion: {question}", 350)
        return llm or ("(offline) No LLM provider is reachable. Based on the current knowledge "
                       "state: " + (context[:400] if context else "no readings absorbed yet."))

    # --- State of Knowledge prose ---
    def state_of_knowledge(self, probably_true: list[str], probably_false: list[str],
                           uncertain: list[str]) -> str:
        system = ("You are writing a read-only 'State of Knowledge' note about Linear A. "
                  "Summarize what is probably true, probably false, and uncertain. Calibrated, "
                  "conditional, never 'Linear A says X'. 1-2 short paragraphs.")
        user = ("PROBABLY TRUE:\n- " + "\n- ".join(probably_true or ["(none yet)"]) +
                "\nPROBABLY FALSE:\n- " + "\n- ".join(probably_false or ["(none yet)"]) +
                "\nUNCERTAIN:\n- " + "\n- ".join(uncertain or ["(none yet)"]))
        llm = self._try_llm(system, user, 500)
        return llm or user
