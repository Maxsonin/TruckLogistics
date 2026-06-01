from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)

from app.core.domain.driver import Driver
from app.infrastructure.db.repositories.driver_repository import DriverRepository
from app.infrastructure.db.session import get_session
from app.ui.dialogs.add_driver_dialog import AddDriverDialog
from app.ui.dialogs.driver_detail_dialog import DriverDetailDialog
from app.ui.theme import colors

_HEADERS = ["ID", "Name", "Phone"]


class DriverView(QWidget):
    def __init__(self) -> None:
        super().__init__()

        self._drivers: list[Driver] = []
        self._detail_dialog: DriverDetailDialog | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        header = QHBoxLayout()
        title = QLabel("Drivers")
        title.setObjectName("viewTitle")
        header.addWidget(title)
        header.addStretch()
        add_btn = QPushButton("+ Add Driver")
        add_btn.setObjectName("primaryButton")
        add_btn.clicked.connect(self._on_add)
        header.addWidget(add_btn)
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setObjectName("secondaryButton")
        refresh_btn.clicked.connect(self.refresh)
        header.addWidget(refresh_btn)
        layout.addLayout(header)

        self._table = QTableWidget(0, len(_HEADERS))
        self._table.setHorizontalHeaderLabels(_HEADERS)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setAlternatingRowColors(True)
        self._table.verticalHeader().setVisible(False)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self._table.setShowGrid(False)
        self._table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._table.setCursor(Qt.CursorShape.PointingHandCursor)
        self._table.cellClicked.connect(self._on_row_clicked)
        layout.addWidget(self._table)

        self._error_label = QLabel("")
        self._error_label.setObjectName("errorLabel")
        self._error_label.setVisible(False)
        layout.addWidget(self._error_label)

        self._apply_styles()

    def _on_add(self) -> None:
        dialog = AddDriverDialog(parent=self)
        if dialog.exec() == AddDriverDialog.DialogCode.Accepted:
            self.refresh()

    def _on_row_clicked(self, row: int, _col: int) -> None:
        item = self._table.item(row, 0)
        if item is None:
            return
        driver_id: str = item.data(Qt.ItemDataRole.UserRole)
        driver = next((d for d in self._drivers if d.id == driver_id), None)
        if driver is None:
            return

        if self._detail_dialog is not None:
            self._detail_dialog.close()

        self._detail_dialog = DriverDetailDialog(driver, parent=self)
        self._detail_dialog.finished.connect(lambda _: setattr(self, "_detail_dialog", None))
        self._detail_dialog.driver_updated.connect(self.refresh)
        self._detail_dialog.driver_deleted.connect(self.refresh)
        self._detail_dialog.show()

    def refresh(self) -> None:
        self._error_label.setVisible(False)
        try:
            with get_session() as session:
                self._drivers = DriverRepository(session).get_all()
        except Exception as exc:
            self._error_label.setText(f"Error: {exc}")
            self._error_label.setVisible(True)
            return

        self._table.setRowCount(0)
        for driver in self._drivers:
            row = self._table.rowCount()
            self._table.insertRow(row)
            for col, value in enumerate([driver.id[:8], driver.name, driver.phone or "—"]):
                item = QTableWidgetItem(value)
                item.setData(Qt.ItemDataRole.UserRole, driver.id)
                if col == 0:
                    item.setToolTip(driver.id)
                self._table.setItem(row, col, item)

    def _apply_styles(self) -> None:
        c = colors()
        self.setStyleSheet(f"""
            QLabel#viewTitle {{
                font-size: 20px; font-weight: bold; color: {c['text']};
            }}
            QLabel#errorLabel {{ color: {c['danger']}; font-size: 12px; }}
            QPushButton#primaryButton {{
                background: {c['text']}; color: {c['bg']}; border: none;
                border-radius: 4px; padding: 6px 14px; font-size: 13px; font-weight: bold;
            }}
            QPushButton#secondaryButton {{
                background: transparent; color: {c['text']};
                border: 1px solid {c['border']}; border-radius: 4px;
                padding: 6px 14px; font-size: 13px;
            }}
            QPushButton#secondaryButton:hover {{ background: {c['surface']}; }}
            QTableWidget {{
                border: 1px solid {c['border']}; border-radius: 4px;
                gridline-color: transparent; font-size: 13px;
                color: {c['text']}; background: {c['bg']};
                alternate-background-color: {c['surface']};
            }}
            QHeaderView::section {{
                background: {c['surface']}; color: {c['subtext']}; border: none;
                border-bottom: 1px solid {c['border']}; padding: 8px;
                font-size: 12px; font-weight: bold; text-transform: uppercase;
            }}
            QTableWidget::item {{ padding: 8px; }}
            QTableWidget::item:selected {{ background: {c['border']}; color: {c['text']}; }}
        """)

    def apply_theme(self) -> None:
        self._apply_styles()
        self.refresh()
