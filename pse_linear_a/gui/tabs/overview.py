from __future__ import annotations
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox
from ._common import page, make_table, fill_table


def _stat(title, value):
    g = QGroupBox(); v = QVBoxLayout(g)
    val = QLabel(str(value)); val.setObjectName("h1")
    t = QLabel(title); t.setObjectName("dim")
    v.addWidget(val); v.addWidget(t); return g


class OverviewTab(QWidget):
    def __init__(self):
        super().__init__()
        self.page, self.v = page("Overview", "How close are we — absorbed readings, "
                                 "confidence, top candidates.")
        lay = QVBoxLayout(self); lay.setContentsMargins(0, 0, 0, 0); lay.addWidget(self.page)
        self.stats = QHBoxLayout(); self.v.addLayout(self.stats)
        self.v.addWidget(QLabel("Top absorbed / candidate readings"))
        self.table = make_table(["type", "target", "value", "confidence", "absorbed"])
        self.v.addWidget(self.table, 1)

    def refresh(self, s):
        while self.stats.count():
            w = self.stats.takeAt(0).widget()
            if w: w.deleteLater()
        snap = s.snapshot()
        self.stats.addWidget(_stat("corpus inscriptions", snap["corpus"]))
        self.stats.addWidget(_stat("absorbed readings", snap["absorbed"]))
        self.stats.addWidget(_stat("refuted hypotheses", snap["refutations"]))
        self.stats.addWidget(_stat("live units", sum(1 for u in snap["units"] if u["alive"])))
        self.stats.addStretch(1)
        rows = []
        for t, rs in s.reading_rows.items():
            for r in rs[:4]:
                rows.append([t, r["target"], r["value"], r["confidence"], r["absorbed"]])
        rows.sort(key=lambda x: x[3], reverse=True)
        fill_table(self.table, rows)
