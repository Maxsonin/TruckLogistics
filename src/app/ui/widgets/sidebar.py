from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel

from app.ui.theme import colors

_NAV_ITEMS = ["Assignments", "Trucks", "Drivers"]


class Sidebar(QWidget):
    page_changed = Signal(int)

    def __init__(self) -> None:
        super().__init__()
        self.setFixedWidth(200)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        title = QLabel("TruckLogistics")
        title.setObjectName("sidebarTitle")
        layout.addWidget(title)

        self._buttons: list[QPushButton] = []
        for i, label in enumerate(_NAV_ITEMS):
            btn = QPushButton(label)
            btn.setObjectName("navButton")
            btn.setProperty("navIndex", i)
            btn.clicked.connect(lambda _, idx=i: self._on_nav(idx))
            layout.addWidget(btn)
            self._buttons.append(btn)

        layout.addStretch()
        self._active = 0
        self._refresh_styles()

    def set_active(self, index: int) -> None:
        self._active = index
        self._refresh_styles()

    def _on_nav(self, index: int) -> None:
        self.set_active(index)
        self.page_changed.emit(index)

    def _refresh_styles(self) -> None:
        c = colors()
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {c['surface']};
                border-right: 1px solid {c['border']};
            }}
            QLabel#sidebarTitle {{
                color: {c['text']};
                font-size: 13px;
                font-weight: bold;
                padding: 20px 16px 16px 16px;
                border-bottom: 1px solid {c['border']};
                background: transparent;
                border-right: none;
            }}
            QPushButton#navButton {{
                background: transparent;
                color: {c['subtext']};
                border: none;
                border-left: 3px solid transparent;
                text-align: left;
                padding: 12px 16px;
                font-size: 13px;
                border-right: none;
            }}
            QPushButton#navButton:hover {{
                background-color: {c['border']};
                color: {c['text']};
            }}
        """)
        for i, btn in enumerate(self._buttons):
            if i == self._active:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: transparent;
                        color: {c['text']};
                        border: none;
                        border-left: 3px solid {c['text']};
                        text-align: left;
                        padding: 12px 16px;
                        font-size: 13px;
                        font-weight: bold;
                    }}
                """)
            else:
                btn.setStyleSheet("")

    def apply_theme(self) -> None:
        self._refresh_styles()
