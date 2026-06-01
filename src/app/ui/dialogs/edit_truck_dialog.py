from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QWidget,
)

from app.core.domain.truck import Truck
from app.core.truck.dto.truck import UpdateTruckDTO
from app.core.truck.services.truck_service import TruckService
from app.infrastructure.db.repositories.truck_repository import TruckRepository
from app.infrastructure.db.session import get_session
from app.ui.theme import colors


class EditTruckDialog(QDialog):
    def __init__(self, truck: Truck, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._truck = truck
        self.setWindowTitle("Edit Truck")
        self.setMinimumWidth(400)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("Edit Truck")
        title.setObjectName("dialogTitle")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self._plate = QLineEdit(truck.plate_number)
        self._plate.setObjectName("formField")
        form.addRow("Plate Number *", self._plate)

        self._model = QLineEdit(truck.model or "")
        self._model.setPlaceholderText("optional")
        self._model.setObjectName("formField")
        form.addRow("Model", self._model)

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
        save_btn = QPushButton("Save Changes")
        save_btn.setObjectName("primaryButton")
        save_btn.setDefault(True)
        save_btn.clicked.connect(self._on_submit)
        buttons.addWidget(cancel_btn)
        buttons.addWidget(save_btn)
        layout.addLayout(buttons)

        self._apply_styles()

    def _on_submit(self) -> None:
        plate = self._plate.text().strip()
        model_text = self._model.text().strip()
        model = model_text if model_text else None

        if not plate:
            self._show_error("Plate number is required.")
            return

        try:
            with get_session() as session:
                TruckService(TruckRepository(session)).update_truck(
                    self._truck.id, UpdateTruckDTO(plate_number=plate, model=model)
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
            QDialog {{ background: {c['bg']}; }}
            QLabel#dialogTitle {{
                font-size: 16px; font-weight: bold; color: {c['text']};
            }}
            QLabel {{ color: {c['text']}; font-size: 13px; }}
            QLabel#errorLabel {{ color: {c['danger']}; font-size: 12px; }}
            QLineEdit#formField {{
                background: {c['surface']}; border: 1px solid {c['border']};
                border-radius: 4px; padding: 8px 10px; font-size: 13px; color: {c['text']};
            }}
            QLineEdit#formField:focus {{ border-color: {c['text']}; }}
            QPushButton#primaryButton {{
                background: {c['text']}; color: {c['bg']}; border: none;
                border-radius: 4px; padding: 8px 20px; font-size: 13px; font-weight: bold;
            }}
            QPushButton#secondaryButton {{
                background: transparent; color: {c['text']};
                border: 1px solid {c['border']}; border-radius: 4px; padding: 8px 20px; font-size: 13px;
            }}
            QPushButton#secondaryButton:hover {{ background: {c['surface']}; }}
        """)
