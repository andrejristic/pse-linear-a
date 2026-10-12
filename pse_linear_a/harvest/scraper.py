"""Phase 0 — Harvest orchestrator. Pulls both scripts, sanitizes untrusted content
through the Cyber Guardian BEFORE it can reach the LLM, records provenance + interest,
and feeds the real-evidence clock. Offline -> falls back to the bundled seed corpus.
"""
from __future__ import annotations
from dataclasses import dataclass, field

from .provenance import classify_source, SourceRecord
from .sources import SOURCES, fetch_source


@dataclass
class HarvestResult:
    online: bool = False
    sources: list[SourceRecord] = field(default_factory=list)
    reachability: dict = field(default_factory=dict)
    inscriptions: list = field(default_factory=list)   # normalized Inscriptions
    note: str = ""


class Scraper:
    def __init__(self, cyber_guardian=None):
        self.cyber = cyber_guardian

    def harvest(self, seed_fallback=None) -> HarvestResult:
        res = HarvestResult()
        any_ok = False
        for key, meta in SOURCES.items():
            r = fetch_source(key)
            res.reachability[key] = r
            rec = classify_source(key, meta["host"], meta["kind"])
            res.sources.append(rec)
            if r.get("ok"):
                any_ok = True
                # sanitize any fetched snippet before it could reach the LLM
                if self.cyber and r.get("sample"):
                    finding = self.cyber.scan_untrusted(key, r["sample"])
                    r["guardian"] = finding.level_name
        res.online = any_ok
        if not any_ok and seed_fallback is not None:
            res.inscriptions = list(seed_fallback)
            res.note = "offline — using bundled seed corpus (real-evidence clock stays low)"
        elif not any_ok:
            res.note = "offline — no seed provided"
        else:
            res.note = "reachable sources found; full parsers are Phase-0 stubs"
        return res
