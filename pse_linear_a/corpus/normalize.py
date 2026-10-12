"""Normalize scraped raw records into canonical Inscription objects.
Maps GORILA/AB sign IDs to Linear B phonetic values where shared."""
from __future__ import annotations
from typing import Optional

from .schema import Inscription, Entry, SIGN_VALUES


def signs_to_translit(signs: list[str]) -> str:
    return "-".join(SIGN_VALUES.get(s, s) for s in signs)


def normalize_raw(raw: dict) -> Inscription:
    """raw: {ident, script, signs?, transliteration?, entries?:[{word,number,logogram?}],
    provenance, source_signal?}"""
    entries = [Entry(e["word"], float(e.get("number", 0.0)), e.get("logogram"))
               for e in raw.get("entries", [])]
    signs = raw.get("signs", [])
    translit = raw.get("transliteration") or (signs_to_translit(signs) if signs else "")
    return Inscription(
        ident=raw["ident"],
        script=raw.get("script", "linear_a"),
        signs=signs,
        transliteration=translit,
        entries=entries,
        words=raw.get("words", [e.word for e in entries]),
        logograms=raw.get("logograms", []),
        provenance=raw.get("provenance", "scraped"),
        source_signal=raw.get("source_signal", "cheap"),
        note=raw.get("note", ""),
    )
