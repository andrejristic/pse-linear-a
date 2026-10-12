"""Persistent chat pane (right 25%). Three roles: advisor (CARE θ=30) / source-ingestion
(cheap-signal, tagged) / command channel (STAGED, requires confirm). Shows the machine's
intent classification on each message. (GUI_DESIGN.md)"""
from __future__ import annotations

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit,
                               QPushButton, QLabel, QCheckBox)
from PySide6.QtCore import Signal, Qt


INTENT_COLOR = {"advisory": "#3f9cff", "source": "#8a7", "instruction": "#e0a030"}


class ChatPane(QWidget):
    stateChanged = Signal()

    def __init__(self, session):
        super().__init__()
        self.session = session
        self._pending_cmd = None
        v = QVBoxLayout(self); v.setContentsMargins(10, 10, 10, 10)
        h = QLabel("Advisor · Source · Command"); h.setObjectName("h2"); v.addWidget(h)
        note = QLabel("LLM advises on Linear A/B; relevant talk becomes cheap-signal "
                      "source; instructions route to SharedLib (staged).")
        note.setObjectName("dim"); note.setWordWrap(True); v.addWidget(note)

        self.log = QTextEdit(); self.log.setReadOnly(True); v.addWidget(self.log, 1)

        self.use_source = QCheckBox("use my messages as source material");
        self.use_source.setChecked(True); v.addWidget(self.use_source)

        row = QHBoxLayout()
        self.entry = QLineEdit(); self.entry.setPlaceholderText("Ask, tell, or /cmd …")
        self.entry.returnPressed.connect(self.on_send)
        send = QPushButton("Send"); send.setObjectName("primary"); send.clicked.connect(self.on_send)
        row.addWidget(self.entry, 1); row.addWidget(send); v.addLayout(row)

        self.confirm_row = QWidget(); cr = QHBoxLayout(self.confirm_row); cr.setContentsMargins(0,0,0,0)
        self.confirm_label = QLabel(""); self.confirm_label.setWordWrap(True)
        yes = QPushButton("Execute"); yes.setObjectName("primary"); yes.clicked.connect(self.on_confirm)
        no = QPushButton("Cancel"); no.clicked.connect(self.on_cancel)
        cr.addWidget(self.confirm_label, 1); cr.addWidget(yes); cr.addWidget(no)
        self.confirm_row.setVisible(False); v.addWidget(self.confirm_row)

        self._say("system", "Chat ready. Providers: " +
                  ", ".join(k for k, ok in session.providers().items() if ok) or "(offline templates)")

    def _say(self, who: str, text: str, color: str = "#9fb2c8"):
        self.log.append(f'<div style="margin:4px 0"><b style="color:{color}">{who}:</b> '
                        f'<span style="color:#d7dce3">{text}</span></div>')

    def on_send(self):
        msg = self.entry.text().strip()
        if not msg:
            return
        self.entry.clear()
        self._say("you", msg, "#eaf2ff")
        res = self.session.chat(msg, use_as_source=self.use_source.isChecked())
        col = INTENT_COLOR.get(res["intent"], "#9fb2c8")
        self._say(f"[{res['intent']} · guardian {res['guardian']}]", res["reply"], col)
        if res.get("staged"):
            self._pending_cmd = msg
            self.confirm_label.setText(f"Staged command → SharedLib: “{msg}”")
            self.confirm_row.setVisible(True)
        self.stateChanged.emit()

    def on_confirm(self):
        if self._pending_cmd:
            out = self.session.execute_instruction(self._pending_cmd)
            self._say("SharedLib", f"executed {out.get('done')}: {out.get('result')}", "#e0a030")
        self.on_cancel()
        self.stateChanged.emit()

    def on_cancel(self):
        self._pending_cmd = None
        self.confirm_row.setVisible(False)
