"""Known Linear A / Linear B source adapters. stdlib urllib only; OFFLINE-GRACEFUL:
on any failure returns [] with a note, so the app falls back to the bundled seed.
Live scraping/parsing per source is intentionally conservative (HEAD/short GET) — the
full per-source parsers are extended here as the project grows.
"""
from __future__ import annotations
import urllib.request
import urllib.error

SOURCES = {
    "sigla": {"host": "sigla.phis.me", "url": "https://sigla.phis.me/",
              "kind": "database", "desc": "SigLA — the Signs of Linear A database"},
    "younger": {"host": "people.ku.edu", "url": "https://people.ku.edu/~jyounger/LinearA/",
                "kind": "corpus", "desc": "J. G. Younger — Linear A texts in transcription"},
    "damos": {"host": "damos.dcc.uchicago.edu", "url": "https://damos.dcc.uchicago.edu/",
              "kind": "database", "desc": "DAMOS — Linear B (anchor)"},
}


def fetch_source(key: str, timeout: float = 8.0) -> dict:
    """Attempt a lightweight reachability fetch. Returns {ok, status, note, raw_len}."""
    src = SOURCES.get(key)
    if not src:
        return {"ok": False, "note": f"unknown source '{key}'"}
    try:
        req = urllib.request.Request(src["url"], headers={"User-Agent": "PSE-LinearA/0.1"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read(4096)
        return {"ok": True, "status": getattr(r, "status", 200),
                "raw_len": len(body), "note": "reachable (parser stub)",
                "sample": body[:200].decode("utf-8", "replace")}
    except Exception as e:  # offline / blocked / timeout
        return {"ok": False, "note": f"offline or unreachable: {e.__class__.__name__}"}
