"""Shared tab helpers."""
from __future__ import annotations

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTableWidget,
                               QTableWidgetItem, QHeaderView)
from PySide6.QtCore import Qt


def page(title: str, subtitle: str = "") -> tuple[QWidget, QVBoxLayout]:
    w = QWidget(); v = QVBoxLayout(w); v.setContentsMargins(18, 16, 18, 16); v.setSpacing(8)
    h = QLabel(title); h.setObjectName("h1"); v.addWidget(h)
    if subtitle:
        s = QLabel(subtitle); s.setObjectName("dim"); s.setWordWrap(True); v.addWidget(s)
    return w, v


def make_table(headers: list[str]) -> QTableWidget:
    t = QTableWidget(0, len(headers))
    t.setHorizontalHeaderLabels(headers)
    t.verticalHeader().setVisible(False)
    t.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    t.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
    t.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    return t


def fill_table(t: QTableWidget, rows: list[list]):
    t.setRowCount(len(rows))
    for r, row in enumerate(rows):
        for c, val in enumerate(row):
            it = QTableWidgetItem(str(val))
            t.setItem(r, c, it)
