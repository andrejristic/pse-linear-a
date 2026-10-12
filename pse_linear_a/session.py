"""Application model wiring all 12 phases together. The GUI is thin over this.

Data flow (PHASES.md launcher): evidence in -> readings form -> swarm governs ->
knowledge out. The human is the sole external authority over SharedLib.
"""
from __future__ import annotations
from dataclasses import dataclass, field
import re

from . import constants as K
from .kernel import SharedLib
from .corpus import build_seed
from .readings import ENGINES, run_reading
from .swarm import Physician, detect_dedup, resolve_collision, classify_attractor
from .llm import PSELGenerator, get_provider, available_providers
from .hypotheses import HypothesisGenerator, verify_hypothesis
from .hypotheses.generator import LANGUAGE_FAMILIES
from .guardian import EpistemicGuardian, CyberGuardian
from .knowledge import StateOfKnowledge
from .harvest import Scraper
from .calibration import calibrate


@dataclass
class Session:
    provider_name: str = "local_gguf"
    corpus: list = field(default_factory=list)
    reading_rows: dict = field(default_factory=dict)     # type -> list of row dicts
    refutations: list = field(default_factory=list)
    harvest_result: object = None

    def __post_init__(self):
        self.sl = SharedLib()
        self.pse_l = PSELGenerator(get_provider(self.provider_name))
        self.epistemic = EpistemicGuardian(self.sl, "guardian_epistemic")
        self.cyber = CyberGuardian(self.sl, "guardian_cyber")
        self.physician = Physician(self.sl)
        self.sok = StateOfKnowledge(self.pse_l)
        self.scraper = Scraper(self.cyber)
        self.chat_log: list[dict] = []

    # ---- Phase 0: boot / harvest ----
    def boot(self) -> None:
        seed = build_seed()
        self.harvest_result = self.scraper.harvest(seed_fallback=seed)
        self.corpus = self.harvest_result.inscriptions or seed

    # ---- Phase 4: calibration gate ----
    def calibrate(self):
        return calibrate(self.corpus)

    # ---- Phase 3: run a reading engine ----
    def run_engine(self, reading_type: str, n_resamples: int = 1000) -> list[dict]:
        Eng = ENGINES[reading_type]
        eng = Eng(self.corpus)
        rows = []
        for r in eng.propose():
            u = self.sl.spawn({"state": "read", "action": f"decipher:{reading_type}",
                               "outcome": "reading"}, 10 ** 6)
            u.enter("SEEK")
            run_reading(u, eng, r, n_resamples=n_resamples)
            if r.absorbed:
                u.enter("BUILD")     # switch to producing/asserting
                self.sl.harvest_and_terminate(u.unit_id)
            rows.append({"target": r.target, "value": r.value, "type": reading_type,
                         "confidence": round(r.confidence, 3), "theta_e": round(r.theta_e, 1),
                         "absorbed": r.absorbed, "real_support": len(r.real_support),
                         "description": r.description})
        rows.sort(key=lambda d: d["confidence"], reverse=True)
        self.reading_rows[reading_type] = rows
        return rows

    def run_all_engines(self) -> dict:
        for t in K.READING_TYPES:
            self.run_engine(t)
        return self.reading_rows

    # ---- Phase 7 + 8: hypotheses, VERIFY, motive tags ----
    def run_hypotheses(self) -> list[dict]:
        gen = HypothesisGenerator(self.corpus, self.sl.accumulated_knowledge)
        out = []
        for h in gen.machine_hypotheses():
            u = self.sl.spawn({"state": "test", "action": "verify", "outcome": "verdict"}, 1000)
            # offline support proxy: reading-kind hypotheses get some support; language
            # families lack cross-linguistic evidence offline -> mostly refuted.
            support = 0.65 if (h.kind == "reading" and h.prior >= 0.3) else h.prior
            verify_hypothesis(u, h, support, self.pse_l)
            if h.kind == "language-family":
                h.motive_tag = self.epistemic.tag_refutation(_family_of(h.text))
                self.epistemic.assess_claim(h.ident, _family_of(h.text), "cheap", h.verdict)
            if h.verdict == "refuted":
                rec = {"hypothesis": h.text, "refutation": h.refutation,
                       "motive_tag": h.motive_tag, "origin": h.origin, "kind": h.kind}
                self.refutations.append(rec)
                self.sl.refutations.append(rec)
            out.append({"text": h.text, "kind": h.kind, "origin": h.origin,
                        "verdict": h.verdict, "support": round(h.support, 2),
                        "motive": (h.motive_tag or {}).get("modern") if h.motive_tag else None})
            self.sl.harvest_and_terminate(u.unit_id)
        return out

    # ---- Phase 5: swarm maintenance ----
    def maintenance(self) -> dict:
        dedup = detect_dedup(list(self.sl.units.values()))
        for a, b, _ in dedup:
            resolve_collision(self.sl, a, b)
        phys = self.physician.round()
        return {"dedup": dedup, "physician": phys}

    # ---- Phase 9: regenerate the read-only knowledge doc ----
    def regenerate_knowledge(self):
        candidates = [{"claim": r["description"], "confidence": r["confidence"]}
                      for rows in self.reading_rows.values() for r in rows if not r["absorbed"]]
        return self.sok.regenerate(self.sl, self.refutations, candidates)

    # ---- chat: advisory / source / command (Phase 6 + GUI) ----
    def classify_intent(self, message: str) -> str:
        if message.strip().startswith("/cmd") or message.strip().startswith("/"):
            return "instruction"
        if re.search(r"\b(spawn|run|scrape|calibrate|verify|fission|retire)\b", message, re.I):
            return "instruction"
        if "?" in message or re.search(r"\b(what|why|how|is|does|which)\b", message, re.I):
            return "advisory"
        return "source"

    def chat(self, message: str, force_intent: str | None = None,
             use_as_source: bool = True) -> dict:
        # cyber guardian scans untrusted human text before it reaches the LLM
        finding = self.cyber.scan_untrusted("chat", message)
        safe = self.cyber.sanitize(message)
        intent = force_intent or self.classify_intent(message)
        result = {"intent": intent, "guardian": finding.level_name, "reply": "",
                  "staged": False}
        if intent == "instruction":
            result["staged"] = True     # commands are STAGED, require confirmation
            result["reply"] = f"Interpreted as instruction to SharedLib: '{safe}'. Execute?"
        elif intent == "advisory":
            ctx = self._knowledge_context()
            result["reply"] = self.pse_l.advise(safe, ctx)
        else:  # source
            if use_as_source:
                result["reply"] = "(ingested as cheap-signal source; tagged source=human)"
            else:
                result["reply"] = "(not ingested)"
        self.chat_log.append({"message": message, **result})
        return result

    def execute_instruction(self, message: str) -> dict:
        """Only reached after human confirmation of a staged command."""
        self.cyber.check_command_channel("human", is_human_authorized=True)
        self.sl.human_instruction("chat_command", {"text": message})
        low = message.lower()
        if "calibrate" in low:
            return {"done": "calibrate", "result": self.calibrate().summary()}
        if "scrape" in low or "harvest" in low:
            self.boot()
            return {"done": "harvest", "result": self.harvest_result.note}
        if "verify" in low or "hypoth" in low:
            return {"done": "hypotheses", "result": f"{len(self.run_hypotheses())} tested"}
        if "run" in low or "read" in low:
            self.run_all_engines()
            return {"done": "run_engines", "result": {k: len(v) for k, v in self.reading_rows.items()}}
        return {"done": "noop", "result": "no matching action"}

    # ---- helpers ----
    def _knowledge_context(self) -> str:
        parts = [f"{k['type']}: {k['representation'].get('target')} = {k['representation'].get('value')}"
                 for k in self.sl.accumulated_knowledge.values()]
        return "; ".join(parts[:20])

    def providers(self) -> dict:
        return available_providers()

    def snapshot(self) -> dict:
        units = [u.snapshot() for u in self.sl.units.values()]
        return {
            "corpus": len(self.corpus),
            "absorbed": len(self.sl.accumulated_knowledge),
            "refutations": len(self.refutations),
            "units": units,
            "threat_intel": self.sl.threat_intel[-30:],
            "audit": self.sl.audit_log[-40:],
            "guardian_theta": {"epistemic": round(self.epistemic.theta, 1),
                               "cyber": round(self.cyber.theta, 1)},
        }


def _family_of(text: str) -> str:
    for fam in LANGUAGE_FAMILIES:
        if fam.split("/")[0].split(" ")[0] in text:
            return fam
    return "isolate/unknown"
