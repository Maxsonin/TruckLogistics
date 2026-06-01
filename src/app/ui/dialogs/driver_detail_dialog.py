from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QWidget,
    QMessageBox,
)

from app.core.domain.driver import Driver
from app.core.driver.services.driver_service import DriverService
from app.infrastructure.db.repositories.assignment_repository import AssignmentRepository
from app.infrastructure.db.repositories.driver_repository import DriverRepository
from app.infrastructure.db.session import get_session
from app.ui.theme import colors


class DriverDetailDialog(QDialog):
    driver_updated = Signal()
    driver_deleted = Signal()

    def __init__(self, driver: Driver, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._driver = driver

        self.setWindowTitle(f"Driver #{driver.id[:8]}")
        self.setMinimumWidth(420)
        self.setModal(False)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self._build_ui()
        self._apply_styles()

    def _build_ui(self) -> None:
        d = self._driver
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(0)

        # ── Header ────────────────────────────────────────────────────────
        title = QLabel(f"Driver <b>#{d.id[:8]}</b>")
        title.setObjectName("detailTitle")
        title.setToolTip(d.id)
        layout.addWidget(title)
        layout.addSpacing(16)

        # ── Identity banner ───────────────────────────────────────────────
        banner = QFrame()
        banner.setObjectName("bannerFrame")
        banner_layout = QVBoxLayout(banner)
        banner_layout.setContentsMargins(16, 14, 16, 14)
        banner_layout.setSpacing(4)

        name_lbl = QLabel(d.name)
        name_lbl.setObjectName("bannerPrimary")
        banner_layout.addWidget(name_lbl)

        if d.phone:
            phone_lbl = QLabel(d.phone)
            phone_lbl.setObjectName("bannerSecondary")
            banner_layout.addWidget(phone_lbl)

        layout.addWidget(banner)
        layout.addSpacing(20)

        # ── Info rows ─────────────────────────────────────────────────────
        rows = [
            ("Name", d.name),
            ("Phone", d.phone or "—"),
            ("Full ID", d.id),
        ]
        grid = QVBoxLayout()
        grid.setSpacing(0)
        for label, value in rows:
            row_widget = QFrame()
            row_widget.setObjectName("infoRow")
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 10, 0, 10)

            key = QLabel(label)
            key.setObjectName("infoKey")
            key.setFixedWidth(80)

            val = QLabel(value)
            val.setObjectName("infoValue")
            val.setWordWrap(True)
            val.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

            row_layout.addWidget(key)
            row_layout.addWidget(val, 1)
            grid.addWidget(row_widget)

            sep = QFrame()
            sep.setObjectName("separator")
            sep.setFrameShape(QFrame.Shape.HLine)
            grid.addWidget(sep)

        layout.addLayout(grid)
        layout.addSpacing(24)

        # ── Actions ───────────────────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        delete_btn = QPushButton("Delete")
        delete_btn.setObjectName("dangerButton")
        delete_btn.clicked.connect(self._on_delete)

        edit_btn = QPushButton("Edit")
        edit_btn.setObjectName("secondaryButton")
        edit_btn.clicked.connect(self._on_edit)

        close_btn = QPushButton("Close")
        close_btn.setObjectName("closeButton")
        close_btn.clicked.connect(self.accept)

        btn_row.addWidget(delete_btn)
        btn_row.addWidget(edit_btn)
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

    def _on_edit(self) -> None:
        from app.ui.dialogs.edit_driver_dialog import EditDriverDialog
        dialog = EditDriverDialog(self._driver, parent=self)
        if dialog.exec() == EditDriverDialog.DialogCode.Accepted:
            self.driver_updated.emit()
            self.accept()

    def _on_delete(self) -> None:
        reply = QMessageBox.question(
            self,
            "Delete Driver",
            f"Delete driver <b>{self._driver.name}</b>? This cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        try:
            with get_session() as session:
                DriverService(
                    DriverRepository(session),
                    AssignmentRepository(session),
                ).delete_driver(self._driver.id)
        except ValueError as exc:
            QMessageBox.warning(self, "Cannot Delete", str(exc))
            return
        except Exception as exc:
            QMessageBox.critical(self, "Error", str(exc))
            return
        self.driver_deleted.emit()
        self.accept()

    def _apply_styles(self) -> None:
        c = colors()
        self.setStyleSheet(f"""
            QDialog {{ background: {c['bg']}; }}
            QLabel#detailTitle {{ font-size: 15px; color: {c['text']}; }}
            QFrame#bannerFrame {{
                background: {c['surface']};
                border: 1px solid {c['border']};
                border-radius: 6px;
            }}
            QLabel#bannerPrimary {{
                font-size: 20px; font-weight: bold; color: {c['text']};
            }}
            QLabel#bannerSecondary {{
                font-size: 13px; color: {c['subtext']};
            }}
            QLabel#infoKey {{
                font-size: 12px; color: {c['subtext']};
                font-weight: bold; text-transform: uppercase;
            }}
            QLabel#infoValue {{
                font-size: 13px; color: {c['text']};
            }}
            QFrame#separator {{
                color: {c['border']}; background: {c['border']}; max-height: 1px;
            }}
            QPushButton#dangerButton {{
                background: transparent; color: {c['danger']};
                border: 1px solid {c['danger']}; border-radius: 4px;
                padding: 8px 18px; font-size: 13px;
            }}
            QPushButton#dangerButton:hover {{
                background: {c['danger']}; color: {c['bg']};
            }}
            QPushButton#secondaryButton {{
                background: transparent; color: {c['text']};
                border: 1px solid {c['border']}; border-radius: 4px;
                padding: 8px 18px; font-size: 13px;
            }}
            QPushButton#secondaryButton:hover {{ background: {c['surface']}; }}
            QPushButton#closeButton {{
                background: {c['text']}; color: {c['bg']}; border: none;
                border-radius: 4px; padding: 8px 18px; font-size: 13px; font-weight: bold;
            }}
        """)
