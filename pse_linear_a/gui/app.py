"""PySide6 entry. Measures the screen the app opens on (the one under the cursor for
multi-monitor) and sizes/centers BEFORE show(). (GUI_DESIGN.md)"""
from __future__ import annotations
import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QGuiApplication, QCursor
from PySide6.QtCore import Qt

STYLE = """
* { font-family: 'DejaVu Sans', 'Noto Sans', sans-serif; }
QMainWindow, QWidget { background: #14171c; color: #d7dce3; }
QLabel#h1 { font-size: 18px; font-weight: 700; color: #e8edf4; }
QLabel#h2 { font-size: 13px; font-weight: 600; color: #9fb2c8; }
QLabel#dim { color: #7f8ea3; }
QPushButton { background:#232a33; border:1px solid #313b47; border-radius:6px;
              padding:6px 10px; color:#d7dce3; }
QPushButton:hover { background:#2c3a49; border-color:#3f7cbf; }
QPushButton#nav { text-align:left; padding:8px 12px; border:none; background:transparent; }
QPushButton#nav:hover { background:#1d2229; }
QPushButton#nav:checked { background:#20303f; border-left:3px solid #3f9cff; color:#eaf2ff; }
QPushButton#primary { background:#1f6feb; border:none; color:white; font-weight:600; }
QPushButton#primary:hover { background:#3f8cff; }
QTableWidget { background:#171b21; gridline-color:#262d36; border:1px solid #262d36; }
QHeaderView::section { background:#1d232b; color:#9fb2c8; border:none; padding:5px; }
QTextEdit, QPlainTextEdit, QLineEdit { background:#171b21; border:1px solid #262d36;
              border-radius:6px; color:#d7dce3; padding:6px; }
QGroupBox { border:1px solid #2a323c; border-radius:8px; margin-top:10px; }
QGroupBox::title { subcontrol-origin: margin; left:10px; color:#9fb2c8; }
"""


def size_to_screen(win) -> None:
    screen = QGuiApplication.screenAt(QCursor.pos()) or QGuiApplication.primaryScreen()
    avail = screen.availableGeometry()
    w = max(1024, min(1600, int(avail.width() * 0.90)))
    h = max(640, min(1000, int(avail.height() * 0.90)))
    win.resize(w, h)
    win.move(avail.x() + (avail.width() - w) // 2, avail.y() + (avail.height() - h) // 2)


def main() -> int:
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication(sys.argv)
    app.setApplicationName("PSE Linear A")
    app.setStyleSheet(STYLE)
    from .main_window import MainWindow
    win = MainWindow()
    size_to_screen(win)            # measure BEFORE show
    win.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
