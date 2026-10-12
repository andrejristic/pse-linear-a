from __future__ import annotations
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from ._common import page, make_table, fill_table


class HarvestTab(QWidget):
    def __init__(self):
        super().__init__()
        self.page, self.v = page("Harvest", "Phase 0 foundation. All evidence is scraped; "
                                 "sources vetted by costly/cheap signal; untrusted content "
                                 "sanitized by the cyber Guardian before it reaches the LLM.")
        lay = QVBoxLayout(self); lay.setContentsMargins(0, 0, 0, 0); lay.addWidget(self.page)
        self.status = QLabel(""); self.status.setObjectName("h2"); self.v.addWidget(self.status)
        self.table = make_table(["source", "host", "signal", "trust", "reachable", "guardian"])
        self.v.addWidget(self.table, 1)

    def refresh(self, s):
        hr = s.harvest_result
        if not hr:
            self.status.setText("not harvested yet"); return
        self.status.setText(("ONLINE" if hr.online else "OFFLINE") + " — " + hr.note)
        rows = []
        for rec in hr.sources:
            r = hr.reachability.get(rec.source_id, {})
            rows.append([rec.source_id, rec.host, rec.signal, f"{rec.trust:.2f}",
                         "yes" if r.get("ok") else "no", r.get("guardian", "-")])
        fill_table(self.table, rows)
