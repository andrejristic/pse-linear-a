"""Provenance + interest mapping + costly/cheap-signal vetting. Load-bearing because
ALL evidence is scraped (no seed corpus in production)."""
from __future__ import annotations
from dataclasses import dataclass

# trusted scholarly sources -> costly signal; blogs/forums/unknown -> cheap
COSTLY_HOSTS = {"sigla.phis.me", "people.ku.edu", "damos.dcc.uchicago.edu",
                "jstor.org", "academia.edu", "cambridge.org", "brill.com"}


@dataclass
class SourceRecord:
    source_id: str
    host: str
    signal: str                  # "costly" | "cheap"
    kind: str                    # "database" | "corpus" | "paper" | "web"
    interest: str = "none"       # economic/political interest if any
    trust: float = 0.0


def classify_source(source_id: str, host: str, kind: str = "web",
                    interest: str = "none") -> SourceRecord:
    signal = "costly" if any(h in host for h in COSTLY_HOSTS) else "cheap"
    trust = 0.85 if signal == "costly" else 0.25
    return SourceRecord(source_id=source_id, host=host, signal=signal, kind=kind,
                        interest=interest, trust=trust)
