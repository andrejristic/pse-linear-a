"""Main window: grouped launcher (left) + stacked tabs (center) + persistent chat
pane (right 25%). Toolbar drives the pipeline. (GUI_DESIGN.md)"""
from __future__ import annotations

from PySide6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel,
                               QPushButton, QStackedWidget, QButtonGroup, QToolBar,
                               QStatusBar, QApplication, QFrame)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QCursor

from ..session import Session
from .chat_pane import ChatPane
from .tabs.overview import OverviewTab
from .tabs.harvest import HarvestTab
from .tabs.corpus import CorpusTab
from .tabs.reading_tab import ReadingTab
from .tabs.swarm import SwarmTab
from .tabs.shared_lib import SharedLibTab
from .tabs.hypotheses import HypothesesTab
from .tabs.state_of_knowledge import StateOfKnowledgeTab

# ordered tabs
TABS = ["Overview", "Harvest", "Corpus", "Structural", "Lexical", "Phonetic",
        "Swarm / θ", "SharedLib", "Hypotheses", "State of Knowledge"]
# launcher groups -> (label, [tab indices])
GROUPS = [("INPUT / EVIDENCE", [1, 2]), ("READING ENGINES", [3, 4, 5]),
          ("SWARM / CONTROL", [6, 7, 8]), ("OUTPUT", [0, 9])]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PSE Linear A — decipherment swarm")
        self.session = Session()
        self.session.boot()

        self._build_toolbar()
        self.setStatusBar(QStatusBar())

        root = QWidget(); self.setCentralWidget(root)
        lay = QHBoxLayout(root); lay.setContentsMargins(0, 0, 0, 0); lay.setSpacing(0)

        lay.addWidget(self._build_launcher(), 0)

        self.stack = QStackedWidget()
        self.tabs = [
            OverviewTab(), HarvestTab(), CorpusTab(),
            ReadingTab("structural"), ReadingTab("lexical"), ReadingTab("phonetic"),
            SwarmTab(), SharedLibTab(), HypothesesTab(), StateOfKnowledgeTab(),
        ]
        for t in self.tabs:
            self.stack.addWidget(t)
        lay.addWidget(self.stack, 1)

        self.chat = ChatPane(self.session)
        self.chat.setMinimumWidth(320)
        lay.addWidget(self.chat, 0)

        self._select(0)
        self.refresh_all()
        # chat may change state (source ingestion / executed command) -> refresh
        self.chat.stateChanged.connect(self.refresh_all)

    # ---------- chrome ----------
    def _build_toolbar(self):
        tb = QToolBar(); tb.setMovable(False); self.addToolBar(tb)
        acts = [("Harvest", self.on_harvest), ("Calibrate", self.on_calibrate),
                ("Run readings", self.on_run_readings), ("Run hypotheses", self.on_run_hypotheses),
                ("Maintenance", self.on_maintenance), ("Regen knowledge", self.on_regen),
                ("Refresh", self.refresh_all)]
        for label, fn in acts:
            a = QAction(label, self); a.triggered.connect(fn); tb.addAction(a)

    def _build_launcher(self) -> QWidget:
        panel = QFrame(); panel.setFixedWidth(210)
        panel.setStyleSheet("QFrame{background:#101318;border-right:1px solid #232a33;}")
        v = QVBoxLayout(panel); v.setContentsMargins(8, 12, 8, 12); v.setSpacing(2)
        title = QLabel("PSE · Linear A"); title.setObjectName("h1"); v.addWidget(title)
        sub = QLabel("evidence → readings → swarm → knowledge")
        sub.setObjectName("dim"); sub.setWordWrap(True); v.addWidget(sub); v.addSpacing(8)
        self.nav_group = QButtonGroup(self); self.nav_group.setExclusive(True)
        self.nav_buttons = {}
        for glabel, idxs in GROUPS:
            gl = QLabel(glabel); gl.setObjectName("h2"); v.addSpacing(6); v.addWidget(gl)
            for i in idxs:
                b = QPushButton(TABS[i]); b.setObjectName("nav"); b.setCheckable(True)
                b.clicked.connect(lambda _=False, k=i: self._select(k))
                self.nav_group.addButton(b); self.nav_buttons[i] = b; v.addWidget(b)
        v.addStretch(1)
        return panel

    def _select(self, idx: int):
        self.stack.setCurrentIndex(idx)
        if idx in self.nav_buttons:
            self.nav_buttons[idx].setChecked(True)

    # ---------- actions ----------
    def _busy(self, msg: str):
        self.statusBar().showMessage(msg)
        QApplication.setOverrideCursor(QCursor(Qt.CursorShape.WaitCursor))
        QApplication.processEvents()

    def _done(self, msg: str):
        QApplication.restoreOverrideCursor()
        self.statusBar().showMessage(msg, 6000)
        self.refresh_all()

    def on_harvest(self):
        self._busy("Harvesting sources...")
        self.session.boot(); self._done(self.session.harvest_result.note)

    def on_calibrate(self):
        self._busy("Running calibration gate (KU-RO)...")
        self._done(self.session.calibrate().summary())

    def on_run_readings(self):
        self._busy("Running reading engines over bootstrap resamples...")
        self.session.run_all_engines(); self._done("Reading engines complete.")

    def on_run_hypotheses(self):
        self._busy("Generating + VERIFY-ing hypotheses...")
        n = len(self.session.run_hypotheses()); self._done(f"{n} hypotheses tested.")

    def on_maintenance(self):
        self._busy("Swarm maintenance (dedup + physician)...")
        m = self.session.maintenance()
        self._done(f"dedup {len(m['dedup'])}, physician {len(m['physician'])}")

    def on_regen(self):
        self._busy("Regenerating State of Knowledge...")
        v = self.session.regenerate_knowledge(); self._done(f"State of Knowledge v{v.version}")

    def refresh_all(self):
        for t in self.tabs:
            try:
                t.refresh(self.session)
            except Exception as e:  # never let one tab break the app
                self.statusBar().showMessage(f"{t.__class__.__name__}: {e}", 8000)
