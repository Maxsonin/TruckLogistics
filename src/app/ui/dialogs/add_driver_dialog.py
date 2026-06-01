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
from PySide6.QtCore import Qt

from app.core.driver.dto.driver import CreateDriverDTO
from app.core.driver.services.driver_service import DriverService
from app.infrastructure.db.repositories.driver_repository import DriverRepository
from app.infrastructure.db.session import get_session
from app.ui.theme import colors


class AddDriverDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Add Driver")
        self.setMinimumWidth(400)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("Add Driver")
        title.setObjectName("dialogTitle")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self._name = QLineEdit()
        self._name.setPlaceholderText("e.g. John Smith")
        self._name.setObjectName("formField")
        form.addRow("Name *", self._name)

        self._phone = QLineEdit()
        self._phone.setPlaceholderText("e.g. +1-555-0100 (optional)")
        self._phone.setObjectName("formField")
        form.addRow("Phone", self._phone)

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
        self._submit_btn = QPushButton("Add Driver")
        self._submit_btn.setObjectName("primaryButton")
        self._submit_btn.setDefault(True)
        self._submit_btn.clicked.connect(self._on_submit)
        buttons.addWidget(cancel_btn)
        buttons.addWidget(self._submit_btn)
        layout.addLayout(buttons)

        self._apply_styles()

    def _on_submit(self) -> None:
        name = self._name.text().strip()
        phone_text = self._phone.text().strip()
        phone = phone_text if phone_text else None

        if not name:
            self._show_error("Driver name is required.")
            return

        try:
            with get_session() as session:
                DriverService(DriverRepository(session)).register_driver(
                    CreateDriverDTO(name=name, phone=phone)
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
            QLineEdit#formField {{
                background: {c['surface']};
                border: 1px solid {c['border']};
                border-radius: 4px;
                padding: 8px 10px;
                font-size: 13px;
                color: {c['text']};
            }}
            QLineEdit#formField:focus {{
                border-color: {c['text']};
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
