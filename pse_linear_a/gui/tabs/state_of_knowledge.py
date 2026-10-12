from __future__ import annotations
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
                               QComboBox)
from ._common import page


class StateOfKnowledgeTab(QWidget):
    def __init__(self):
        super().__init__()
        self.page, self.v = page("State of Knowledge",
                                 "READ-ONLY living document — what is probably true / false / "
                                 "uncertain about Linear A. Calibrated, append-only, versioned, "
                                 "traceable. Regenerated on every verified learning event.")
        lay = QVBoxLayout(self); lay.setContentsMargins(0, 0, 0, 0); lay.addWidget(self.page)
        row = QHBoxLayout(); row.addWidget(QLabel("version:"))
        self.picker = QComboBox(); self.picker.currentIndexChanged.connect(self._show)
        row.addWidget(self.picker); row.addStretch(1); self.v.addLayout(row)
        self.doc = QTextEdit(); self.doc.setReadOnly(True)          # read-only enforced
        self.v.addWidget(self.doc, 1)
        self._session = None

    def refresh(self, s):
        self._session = s
        n = len(s.sok.versions)
        self.picker.blockSignals(True)
        self.picker.clear()
        self.picker.addItems([f"v{v.version} — {v.timestamp}" for v in s.sok.versions])
        if n:
            self.picker.setCurrentIndex(n - 1)
        self.picker.blockSignals(False)
        self._show()

    def _show(self):
        if not self._session or not self._session.sok.versions:
            self.doc.setMarkdown("_No version yet. Run readings/hypotheses, then "
                                 "**Regen knowledge**._"); return
        idx = max(0, self.picker.currentIndex())
        v = self._session.sok.versions[idx]
        self.doc.setMarkdown(v.render())
