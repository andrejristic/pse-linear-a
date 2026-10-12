from __future__ import annotations
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from ._common import page, make_table, fill_table


class CorpusTab(QWidget):
    def __init__(self):
        super().__init__()
        self.page, self.v = page("Corpus", "Both scripts: Linear A (target) + Linear B "
                                 "(deciphered anchor). Sign IDs → Linear B values → context.")
        lay = QVBoxLayout(self); lay.setContentsMargins(0, 0, 0, 0); lay.addWidget(self.page)
        self.count = QLabel(""); self.count.setObjectName("h2"); self.v.addWidget(self.count)
        self.table = make_table(["id", "script", "transliteration", "provenance", "note"])
        self.v.addWidget(self.table, 1)

    def refresh(self, s):
        self.count.setText(f"{len(s.corpus)} inscriptions")
        rows = [[i.ident, i.script, i.transliteration[:80], i.provenance, i.note[:50]]
                for i in s.corpus]
        fill_table(self.table, rows)
