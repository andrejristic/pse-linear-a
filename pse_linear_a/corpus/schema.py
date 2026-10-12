"""Canonical corpus schema: sign-ID (GORILA/AB) -> Linear B phonetic value -> context.
Both scripts share this schema; Linear B is the securely-read anchor.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

# A subset of the REAL shared Linear A / Linear B (AB) sign -> phonetic value table.
# These transliteration values are standard (Linear B values applied to shared signs).
SIGN_VALUES: dict[str, str] = {
    "AB01": "da", "AB02": "ro", "AB03": "pa", "AB04": "te", "AB05": "to",
    "AB08": "a", "AB09": "se", "AB10": "u", "AB13": "me", "AB16": "pa3",
    "AB28": "i", "AB37": "ti", "AB38": "e", "AB39": "pi", "AB40": "wi",
    "AB53": "ri", "AB54": "wa", "AB59": "ta", "AB60": "ra", "AB67": "ki",
    "AB70": "ko", "AB77": "ka", "AB80": "ma", "AB81": "ku", "A303": "?",  # A### = Linear-A-only (open value)
    "A304": "?", "A305": "?",
}

# commodity logograms (ideograms) — securely identified from Linear B parallels
LOGOGRAMS = {"VINa": "wine", "OLE": "oil", "GRA": "grain", "FIC": "figs", "OVISm": "sheep"}


@dataclass
class Entry:
    """One line item on an accounting tablet: a word and its numeral."""
    word: str                 # transliterated sign-group, e.g. "ku-ro"
    number: float
    logogram: Optional[str] = None


@dataclass
class Inscription:
    ident: str                        # e.g. "HT13"
    script: str = "linear_a"          # "linear_a" | "linear_b"
    signs: list[str] = field(default_factory=list)          # raw sign IDs
    transliteration: str = ""
    entries: list[Entry] = field(default_factory=list)      # for accounting tablets
    words: list[str] = field(default_factory=list)          # all word tokens in order
    logograms: list[str] = field(default_factory=list)
    provenance: str = "seed"          # source id
    source_signal: str = "internal"   # cheap | costly | internal
    note: str = ""

    def numbers(self) -> list[float]:
        return [e.number for e in self.entries]

    def word_tokens(self) -> list[str]:
        if self.words:
            return self.words
        return [e.word for e in self.entries]
