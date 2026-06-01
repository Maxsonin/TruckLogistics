from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QComboBox,
    QSpinBox,
    QWidget,
)
from PySide6.QtCore import Qt, QDateTime

from app.core.assignment.dto.assignment import CreateAssignmentDTO
from app.core.assignment.services.assignment_service import AssignmentService
from app.core.domain.driver import Driver
from app.core.domain.truck import Truck
from app.infrastructure.db.repositories.assignment_repository import AssignmentRepository
from app.infrastructure.db.repositories.driver_repository import DriverRepository
from app.infrastructure.db.repositories.truck_repository import TruckRepository
from app.infrastructure.db.session import get_session
from app.ui.theme import colors

try:
    from PySide6.QtWidgets import QDateTimeEdit
    _HAS_DATETIME_EDIT = True
except ImportError:
    _HAS_DATETIME_EDIT = False


class CreateAssignmentDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("New Assignment")
        self.setMinimumWidth(440)
        self.setModal(True)

        self._trucks: list[Truck] = []
        self._drivers: list[Driver] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("New Assignment")
        title.setObjectName("dialogTitle")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self._truck_combo = QComboBox()
        self._truck_combo.setObjectName("formCombo")
        form.addRow("Truck *", self._truck_combo)

        self._driver_combo = QComboBox()
        self._driver_combo.setObjectName("formCombo")
        form.addRow("Driver *", self._driver_combo)

        self._origin = QLineEdit()
        self._origin.setPlaceholderText("e.g. Warsaw")
        self._origin.setObjectName("formField")
        form.addRow("Origin *", self._origin)

        self._destination = QLineEdit()
        self._destination.setPlaceholderText("e.g. Berlin")
        self._destination.setObjectName("formField")
        form.addRow("Destination *", self._destination)

        self._started_at = QDateTimeEdit()
        self._started_at.setObjectName("formField")
        self._started_at.setDisplayFormat("yyyy-MM-dd HH:mm")
        self._started_at.setCalendarPopup(True)
        self._started_at.setDateTime(QDateTime.currentDateTime())
        form.addRow("Started At *", self._started_at)

        self._duration = QSpinBox()
        self._duration.setObjectName("formSpin")
        self._duration.setRange(1, 99999)
        self._duration.setValue(60)
        self._duration.setSuffix(" min")
        form.addRow("Duration *", self._duration)

        layout.addLayout(form)

        self._error = QLabel("")
        self._error.setObjectName("errorLabel")
        self._error.setWordWrap(True)
        self._error.setVisible(False)
        layout.addWidget(self._error)

        layout.addStretch()

        buttons = QHBoxLayout()
        buttons.addStretch()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("secondaryButton")
        cancel_btn.clicked.connect(self.reject)
        self._submit_btn = QPushButton("Create")
        self._submit_btn.setObjectName("primaryButton")
        self._submit_btn.setDefault(True)
        self._submit_btn.clicked.connect(self._on_submit)
        buttons.addWidget(cancel_btn)
        buttons.addWidget(self._submit_btn)
        layout.addLayout(buttons)

        self._apply_styles()
        self._load_data()

    def _load_data(self) -> None:
        self._error.setVisible(False)
        try:
            with get_session() as session:
                self._trucks = TruckRepository(session).get_all()
                self._drivers = DriverRepository(session).get_all()
        except Exception as exc:
            self._show_error(f"Failed to load trucks/drivers: {exc}")
            self._submit_btn.setEnabled(False)
            return

        self._truck_combo.clear()
        if not self._trucks:
            self._truck_combo.addItem("No trucks available", None)
            self._submit_btn.setEnabled(False)
        else:
            for truck in self._trucks:
                label = f"{truck.plate_number}" + (f" — {truck.model}" if truck.model else "")
                self._truck_combo.addItem(label, truck.id)

        self._driver_combo.clear()
        if not self._drivers:
            self._driver_combo.addItem("No drivers available", None)
            self._submit_btn.setEnabled(False)
        else:
            for driver in self._drivers:
                label = driver.name + (f" ({driver.phone})" if driver.phone else "")
                self._driver_combo.addItem(label, driver.id)

    def _on_submit(self) -> None:
        truck_id: str | None = self._truck_combo.currentData()
        driver_id: str | None = self._driver_combo.currentData()
        origin = self._origin.text().strip()
        destination = self._destination.text().strip()
        duration = self._duration.value()
        qt_dt = self._started_at.dateTime()

        if not truck_id:
            self._show_error("Please select a truck.")
            return
        if not driver_id:
            self._show_error("Please select a driver.")
            return
        if not origin:
            self._show_error("Origin is required.")
            return
        if not destination:
            self._show_error("Destination is required.")
            return

        from datetime import datetime, timezone
        qt_dt_utc = qt_dt.toUTC()
        py_dt = datetime(
            qt_dt_utc.date().year(),
            qt_dt_utc.date().month(),
            qt_dt_utc.date().day(),
            qt_dt_utc.time().hour(),
            qt_dt_utc.time().minute(),
            tzinfo=timezone.utc,
        )

        selected_truck = next((t for t in self._trucks if t.id == truck_id), None)
        selected_driver = next((d for d in self._drivers if d.id == driver_id), None)
        truck_label = selected_truck.plate_number if selected_truck else truck_id
        driver_label = selected_driver.name if selected_driver else driver_id

        try:
            with get_session() as session:
                AssignmentService(AssignmentRepository(session)).create_assignment(
                    CreateAssignmentDTO(
                        truck_id=truck_id,
                        driver_id=driver_id,
                        origin=origin,
                        destination=destination,
                        estimated_duration_min=duration,
                        started_at=py_dt,
                        truck_label=truck_label,
                        driver_label=driver_label,
                    )
                )
        except ValueError as exc:
            self._show_error(str(exc))
            return
        except Exception as exc:
            self._show_error(f"Unexpected error: {exc}")
            return

        self.accept()

    def _show_error(self, message: str) -> None:
        self._error.setText(message)
        self._error.setVisible(True)

    def _apply_styles(self) -> None:
        c = colors()
        self.setStyleSheet(f"""
            QDialog {{
                background: {c['bg']};
            }}
            QLabel#dialogTitle {{
                font-size: 16px;
                font-weight: bold;
                color: {c['text']};
            }}
            QLabel {{
                color: {c['text']};
                font-size: 13px;
            }}
            QLabel#errorLabel {{
                color: {c['danger']};
                font-size: 12px;
            }}
            QLineEdit#formField, QDateTimeEdit#formField {{
                background: {c['surface']};
                border: 1px solid {c['border']};
                border-radius: 4px;
                padding: 8px 10px;
                font-size: 13px;
                color: {c['text']};
            }}
            QLineEdit#formField:focus, QDateTimeEdit#formField:focus {{
                border-color: {c['text']};
            }}
            QComboBox#formCombo {{
                background: {c['surface']};
                border: 1px solid {c['border']};
                border-radius: 4px;
                padding: 7px 10px;
                font-size: 13px;
                color: {c['text']};
            }}
            QComboBox#formCombo::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox#formCombo QAbstractItemView {{
                background: {c['surface']};
                border: 1px solid {c['border']};
                color: {c['text']};
                selection-background-color: {c['border']};
            }}
            QSpinBox#formSpin {{
                background: {c['surface']};
                border: 1px solid {c['border']};
                border-radius: 4px;
                padding: 7px 10px;
                font-size: 13px;
                color: {c['text']};
            }}
            QPushButton#primaryButton {{
                background: {c['text']};
                color: {c['bg']};
                border: none;
                border-radius: 4px;
                padding: 8px 20px;
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton#secondaryButton {{
                background: transparent;
                color: {c['text']};
                border: 1px solid {c['border']};
                border-radius: 4px;
                padding: 8px 20px;
                font-size: 13px;
            }}
            QPushButton#secondaryButton:hover {{
                background: {c['surface']};
            }}
        """)
