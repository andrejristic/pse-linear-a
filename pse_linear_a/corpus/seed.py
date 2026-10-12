"""Illustrative offline seed corpus so the app runs without network.

HONESTY NOTE: these tablets are STRUCTURE-FAITHFUL but the numeric values are
SYNTHETIC (illustrative). They reproduce the real, documented fact that on Linear A
accounting tablets the word KU-RO (ku-ro) marks a TOTAL: the number beside KU-RO
equals the sum of the preceding line items; KI-RO (ki-ro) marks a deficit/owed.
Real tablet values are pulled by the scraper (Phase 0) from SigLA / J. Younger.
The seed exists only to (a) make the app runnable offline and (b) let the calibration
gate (Phase 4) demonstrate the structural engine re-discovering KU-RO from arithmetic.
"""
from __future__ import annotations
import random
from .schema import Inscription, Entry

_WORDS = ["ka-pa", "da-ro", "ki-re-ta", "pa-i-to", "su-ki-ri-ta", "di-de-ru",
          "qa-ra2-wa", "ku-pa3-nu", "sa-ra2", "a-du", "ma-ka-ri-te", "wi-na-du"]


def _accounting_tablet(ident: str, rng: random.Random, n_items: int = 4,
                       total_word: str = "ku-ro") -> Inscription:
    items = rng.sample(_WORDS, n_items)
    entries = [Entry(w, float(rng.randint(1, 40))) for w in items]
    total = sum(e.number for e in entries)
    entries.append(Entry(total_word, float(total)))     # KU-RO = sum of the above
    words = [e.word for e in entries]
    return Inscription(ident=ident, script="linear_a", entries=entries, words=words,
                       transliteration=" / ".join(f"{e.word} {int(e.number)}" for e in entries),
                       provenance="seed", note="synthetic values; KU-RO=total structure faithful")


def build_seed(n_tablets: int = 12, seed: int = 7) -> list[Inscription]:
    rng = random.Random(seed)
    corpus: list[Inscription] = []
    # accounting tablets with KU-RO totals
    for i in range(n_tablets):
        corpus.append(_accounting_tablet(f"HT{i+1}", rng, n_items=rng.randint(3, 6)))
    # a couple of KI-RO (deficit) tablets: last number does NOT equal the sum
    for i in range(3):
        t = _accounting_tablet(f"HT{100+i}", rng, n_items=4, total_word="ki-ro")
        t.entries[-1].number = float(rng.randint(1, 10))   # a deficit, not the sum
        t.words[-1] = "ki-ro"
        t.transliteration = " / ".join(f"{e.word} {int(e.number)}" for e in t.entries)
        t.note = "synthetic; ki-ro=deficit (not the sum)"
        corpus.append(t)
    # lexical: tablets where a word co-occurs systematically with a commodity logogram
    for i in range(6):
        w = "sa-ra2"  # pretend this associates with wine
        e = [Entry(w, float(rng.randint(5, 30)), logogram="VINa")]
        ins = Inscription(ident=f"ZA{i+1}", script="linear_a", entries=e, words=[w],
                          logograms=["VINa"], provenance="seed",
                          transliteration=f"{w} VINa {int(e[0].number)}",
                          note="synthetic lexical collocation sa-ra2<->wine")
        corpus.append(ins)
    # a Linear B anchor inscription (deciphered) for scaffolding
    corpus.append(Inscription(ident="KNb1", script="linear_b", words=["ko-no-so", "wa-na-ka"],
                              transliteration="ko-no-so (Knossos) / wa-na-ka (king)",
                              provenance="seed_anchor", note="Linear B, securely read"))
    return corpus
