"""Shared reading-tab template (structural / lexical / phonetic). One widget, three
instances; only the null-panel description differs. (GUI_DESIGN.md)"""
from __future__ import annotations
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QGroupBox
from ._common import page, make_table, fill_table

NULL_DESC = {
    "structural": "Null = permutation/shuffle test (P a random word's number coincidentally "
                  "equals the sum). Strongest, language-free. Reproduces KU-RO from arithmetic.",
    "lexical": "Null = base rate of the logogram. LLR = pointwise-MI accumulation "
               "(collocation word↔logogram). Feeds the MI≥0.70 absorption gate.",
    "phonetic": "Null = average over candidate values under a phonotactic bigram LM trained "
                "on securely-read (Linear B) words. Weakest; most VERIFY excursions.",
}
GATE = ["residency (resample)", "≥k real tablets", "θ_e ≥ 10", "stable steps",
        "MI ≥ 0.70", "resample-stability"]


class ReadingTab(QWidget):
    def __init__(self, reading_type: str):
        super().__init__()
        self.rtype = reading_type
        self.page, self.v = page(f"{reading_type.capitalize()} readings",
                                 NULL_DESC[reading_type])
        lay = QVBoxLayout(self); lay.setContentsMargins(0, 0, 0, 0); lay.addWidget(self.page)
        self.table = make_table(["confidence", "θ_e", "absorbed", "real", "target", "value"])
        self.v.addWidget(self.table, 1)
        gate = QGroupBox("Absorption gate (all must pass)")
        gl = QHBoxLayout(gate)
        for g in GATE:
            gl.addWidget(QLabel("• " + g))
        self.v.addWidget(gate)

    def refresh(self, s):
        rows = s.reading_rows.get(self.rtype, [])
        fill_table(self.table, [[r["confidence"], r["theta_e"], r["absorbed"],
                                 r["real_support"], r["target"], r["value"]] for r in rows])
