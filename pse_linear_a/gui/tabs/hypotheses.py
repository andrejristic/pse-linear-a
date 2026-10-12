from __future__ import annotations
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                               QPushButton)
from ._common import page, make_table, fill_table


class HypothesesTab(QWidget):
    def __init__(self):
        super().__init__()
        self.page, self.v = page("Hypotheses", "Machine self-generates testable hypotheses "
                                 "(non-random prior), VERIFY-excursion tests them, and writes "
                                 "'why it fails' refutations. False conclusions carry a motive "
                                 "tag (motive ≠ falsity — it explains persistence).")
        lay = QVBoxLayout(self); lay.setContentsMargins(0, 0, 0, 0); lay.addWidget(self.page)
        row = QHBoxLayout()
        self.entry = QLineEdit(); self.entry.setPlaceholderText("Ask your own hypothesis (tagged source=human)…")
        ask = QPushButton("Ask + VERIFY"); ask.setObjectName("primary"); ask.clicked.connect(self._ask)
        row.addWidget(self.entry, 1); row.addWidget(ask); self.v.addLayout(row)
        self.table = make_table(["origin", "kind", "verdict", "support", "hypothesis", "motive"])
        self.v.addWidget(self.table, 1)
        self._session = None

    def _ask(self):
        if not self._session or not self.entry.text().strip():
            return
        from ...hypotheses import HypothesisGenerator, verify_hypothesis
        gen = HypothesisGenerator(self._session.corpus)
        h = gen.human_hypothesis(self.entry.text().strip())
        u = self._session.sl.spawn({"state": "test", "action": "verify", "outcome": "verdict"}, 500)
        verify_hypothesis(u, h, support=h.prior, pse_l=self._session.pse_l)
        rec = {"hypothesis": h.text, "refutation": h.refutation, "motive_tag": None,
               "origin": "human", "kind": h.kind}
        if h.verdict == "refuted":
            self._session.refutations.append(rec); self._session.sl.refutations.append(rec)
        self.entry.clear(); self.refresh(self._session)

    def refresh(self, s):
        self._session = s
        rows = [[r.get("origin", "machine"), r.get("kind", ""), "refuted", "-",
                 r["hypothesis"][:70], (r.get("motive_tag") or {}).get("modern", "") if r.get("motive_tag") else ""]
                for r in s.refutations]
        fill_table(self.table, rows)
