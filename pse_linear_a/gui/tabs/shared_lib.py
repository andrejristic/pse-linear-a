from __future__ import annotations
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTabWidget
from ._common import page, make_table, fill_table


class SharedLibTab(QWidget):
    def __init__(self):
        super().__init__()
        self.page, self.v = page("SharedLib", "The orchestrator + Registry. Only the human "
                                 "commands it. Absorbed readings, threat intel, audit log, "
                                 "human-review queue.")
        lay = QVBoxLayout(self); lay.setContentsMargins(0, 0, 0, 0); lay.addWidget(self.page)
        self.tabs = QTabWidget(); self.v.addWidget(self.tabs, 1)
        self.know = make_table(["reading", "type", "weight", "confidence", "from unit"])
        self.threat = make_table(["source", "surface", "level", "reason", "by"])
        self.audit = make_table(["step", "kind", "detail"])
        self.review = make_table(["item"])
        self.tabs.addTab(self.know, "Registry (absorbed)")
        self.tabs.addTab(self.threat, "Threat intel")
        self.tabs.addTab(self.audit, "Audit log")
        self.tabs.addTab(self.review, "Human review")

    def refresh(self, s):
        fill_table(self.know, [[oid, k["type"], round(k["weight"], 1),
                                round(k.get("confidence", 0), 2), k["from_unit"]]
                               for oid, k in s.sl.accumulated_knowledge.items()])
        fill_table(self.threat, [[t.get("source"), t.get("surface"), t.get("level"),
                                  t.get("reason", "")[:60], t.get("by", "")]
                                 for t in s.sl.threat_intel[-50:]])
        fill_table(self.audit, [[a.get("step"), a.get("kind"),
                                 ", ".join(f"{k}={v}" for k, v in a.items()
                                           if k not in ("step", "kind"))[:70]]
                                for a in s.sl.audit_log[-80:]])
        fill_table(self.review, [[str(r)[:120]] for r in s.sl.human_review_queue[-30:]])
