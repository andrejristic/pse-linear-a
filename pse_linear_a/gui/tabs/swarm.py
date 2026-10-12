from __future__ import annotations
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox
from ._common import page, make_table, fill_table
from ...swarm import classify_attractor


class SwarmTab(QWidget):
    def __init__(self):
        super().__init__()
        self.page, self.v = page("Swarm / θ", "Live units, action-mode setpoints (SEEK 40 / "
                                 "CARE 30 / BUILD 20 / ORCH 10 / VERIFY), pathology on the "
                                 "residual θ, and the two independent Guardians' own θ.")
        lay = QVBoxLayout(self); lay.setContentsMargins(0, 0, 0, 0); lay.addWidget(self.page)
        self.gbox = QHBoxLayout(); self.v.addLayout(self.gbox)
        self.table = make_table(["unit", "role", "mode", "θ", "resid σ", "boundary",
                                 "organelles", "attractor"])
        self.v.addWidget(self.table, 1)

    def _g(self, title, val):
        g = QGroupBox(); v = QVBoxLayout(g)
        a = QLabel(str(val)); a.setObjectName("h1"); v.addWidget(a)
        b = QLabel(title); b.setObjectName("dim"); v.addWidget(b); return g

    def refresh(self, s):
        while self.gbox.count():
            w = self.gbox.takeAt(0).widget()
            if w: w.deleteLater()
        gt = s.snapshot()["guardian_theta"]
        self.gbox.addWidget(self._g("epistemic Guardian θ (25–35)", gt["epistemic"]))
        self.gbox.addWidget(self._g("cyber Guardian θ (25–35)", gt["cyber"]))
        self.gbox.addStretch(1)
        rows = []
        for u in s.sl.units.values():
            att = classify_attractor(u.theta).value if u.alive else "-"
            snap = u.snapshot()
            rows.append([snap["unit_id"], snap["role"], snap["mode"], snap["theta"],
                         snap["residual_sigma"], snap["boundary"], snap["organelles"], att])
        fill_table(self.table, rows[-60:])
