from datetime import datetime, timedelta

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
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

from app.core.assignment.services.assignment_service import AssignmentService
from app.core.domain.assignment import Assignment, AssignmentStatus
from app.core.domain.driver import Driver
from app.core.domain.truck import Truck
from app.infrastructure.db.repositories.assignment_repository import AssignmentRepository
from app.infrastructure.db.repositories.driver_repository import DriverRepository
from app.infrastructure.db.repositories.truck_repository import TruckRepository
from app.infrastructure.db.session import get_session
from app.ui.dialogs.assignment_detail_dialog import AssignmentDetailDialog
from app.ui.dialogs.create_assignment_dialog import CreateAssignmentDialog
from app.ui.theme import colors

_HEADERS = ["ID", "Truck", "Driver", "Origin", "Destination", "Started", "Duration", "ETA", "Status"]
_COL_STATUS = 8


def _fmt_dt(dt: datetime) -> str:
    return dt.astimezone().strftime("%Y-%m-%d %H:%M")


def _compute_eta(a: Assignment) -> str:
    eta = a.started_at + timedelta(minutes=a.estimated_duration_min)
    return _fmt_dt(eta)


class AssignmentView(QWidget):
    def __init__(self) -> None:
        super().__init__()

        self._assignments: list[Assignment] = []
        self._trucks: dict[str, Truck] = {}
        self._drivers: dict[str, Driver] = {}
        self._detail_dialog: AssignmentDetailDialog | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        header = QHBoxLayout()
        title = QLabel("Assignments")
        title.setObjectName("viewTitle")
        header.addWidget(title)
        header.addStretch()
        new_btn = QPushButton("+ New Assignment")
        new_btn.setObjectName("primaryButton")
        new_btn.clicked.connect(self._on_new)
        header.addWidget(new_btn)
        self._refresh_btn = QPushButton("Refresh")
        self._refresh_btn.setObjectName("secondaryButton")
        self._refresh_btn.clicked.connect(self.refresh)
        header.addWidget(self._refresh_btn)
        layout.addLayout(header)

        self._table = QTableWidget(0, len(_HEADERS))
        self._table.setHorizontalHeaderLabels(_HEADERS)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setAlternatingRowColors(True)
        self._table.verticalHeader().setVisible(False)
        self._table.horizontalHeader().setStretchLastSection(False)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
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
        self.refresh()

    def _on_new(self) -> None:
        dialog = CreateAssignmentDialog(parent=self)
        if dialog.exec() == CreateAssignmentDialog.DialogCode.Accepted:
            self.refresh()

    def _on_row_clicked(self, row: int, _col: int) -> None:
        item = self._table.item(row, 0)
        if item is None:
            return
        assignment_id: str = item.data(Qt.ItemDataRole.UserRole)
        assignment = next((a for a in self._assignments if a.id == assignment_id), None)
        if assignment is None:
            return

        truck = self._trucks.get(assignment.truck_id)
        driver = self._drivers.get(assignment.driver_id)
        truck_label = truck.plate_number if truck else assignment.truck_id[:8]
        driver_label = driver.name if driver else assignment.driver_id[:8]

        if self._detail_dialog is not None:
            self._detail_dialog.close()

        self._detail_dialog = AssignmentDetailDialog(
            assignment, truck_label, driver_label, parent=self
        )
        self._detail_dialog.finished.connect(lambda _: setattr(self, "_detail_dialog", None))
        self._detail_dialog.assignment_cancelled.connect(self.refresh)
        self._detail_dialog.show()

    def refresh(self) -> None:
        self._error_label.setVisible(False)
        try:
            with get_session() as session:
                self._assignments = AssignmentService(AssignmentRepository(session)).list_assignments()
                self._trucks = {t.id: t for t in TruckRepository(session).get_all()}
                self._drivers = {d.id: d for d in DriverRepository(session).get_all()}
        except Exception as exc:
            self._show_error(str(exc))
            return

        self._table.setRowCount(0)
        for assignment in self._assignments:
            row = self._table.rowCount()
            self._table.insertRow(row)

            truck = self._trucks.get(assignment.truck_id)
            driver = self._drivers.get(assignment.driver_id)
            truck_label = truck.plate_number if truck else assignment.truck_id[:8]
            driver_label = driver.name if driver else assignment.driver_id[:8]
            status = assignment.status

            values = [
                assignment.id[:8],
                truck_label,
                driver_label,
                assignment.origin,
                assignment.destination,
                _fmt_dt(assignment.started_at),
                f"{assignment.estimated_duration_min} min",
                _compute_eta(assignment),
                status.value,
            ]
            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setData(Qt.ItemDataRole.UserRole, assignment.id)
                if col == 0:
                    item.setToolTip(assignment.id)
                if col == _COL_STATUS:
                    item.setForeground(self._status_color(status))
                self._table.setItem(row, col, item)

    def _show_error(self, message: str) -> None:
        self._error_label.setText(f"Error: {message}")
        self._error_label.setVisible(True)

    def _status_color(self, status: AssignmentStatus) -> QColor:
        c = colors()
        if status == AssignmentStatus.ACTIVE:
            return QColor("#2E7D32")
        if status == AssignmentStatus.CANCELLED:
            return QColor(c["subtext"])
        return QColor(c["text"])

    def _apply_styles(self) -> None:
        c = colors()
        self.setStyleSheet(f"""
            QLabel#viewTitle {{
                font-size: 20px;
                font-weight: bold;
                color: {c['text']};
            }}
            QLabel#errorLabel {{
                color: {c['danger']};
                font-size: 12px;
            }}
            QPushButton#primaryButton {{
                background: {c['text']};
                color: {c['bg']};
                border: none;
                border-radius: 4px;
                padding: 6px 14px;
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton#secondaryButton {{
                background: transparent;
                color: {c['text']};
                border: 1px solid {c['border']};
                border-radius: 4px;
                padding: 6px 14px;
                font-size: 13px;
            }}
            QPushButton#secondaryButton:hover {{
                background: {c['surface']};
            }}
            QTableWidget {{
                border: 1px solid {c['border']};
                border-radius: 4px;
                gridline-color: transparent;
                font-size: 13px;
                color: {c['text']};
                background: {c['bg']};
                alternate-background-color: {c['surface']};
            }}
            QHeaderView::section {{
                background: {c['surface']};
                color: {c['subtext']};
                border: none;
                border-bottom: 1px solid {c['border']};
                padding: 8px;
                font-size: 12px;
                font-weight: bold;
                text-transform: uppercase;
            }}
            QTableWidget::item {{
                padding: 8px;
            }}
            QTableWidget::item:selected {{
                background: {c['border']};
                color: {c['text']};
            }}
        """)

    def apply_theme(self) -> None:
        self._apply_styles()
        self.refresh()
