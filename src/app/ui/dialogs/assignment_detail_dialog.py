from datetime import timedelta

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

from app.core.assignment.services.assignment_service import AssignmentService
from app.core.domain.assignment import Assignment, AssignmentStatus
from app.infrastructure.db.repositories.assignment_repository import AssignmentRepository
from app.infrastructure.db.session import get_session
from app.ui.theme import colors


from datetime import datetime

def _fmt_dt(dt: datetime) -> str:
    return dt.astimezone().strftime("%Y-%m-%d %H:%M")


class AssignmentDetailDialog(QDialog):
    assignment_cancelled = Signal()

    def __init__(
        self,
        assignment: Assignment,
        truck_label: str,
        driver_label: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._assignment = assignment
        self._truck_label = truck_label
        self._driver_label = driver_label

        self.setWindowTitle(f"Assignment #{assignment.id[:8]}")
        self.setMinimumWidth(480)
        self.setModal(False)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self._build_ui()
        self._apply_styles()

    def _build_ui(self) -> None:
        a = self._assignment
        status = a.status

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(0)

        # ── Header: ID + Status badge ──────────────────────────────────────
        header = QHBoxLayout()
        id_label = QLabel(f"Assignment <b>#{a.id[:8]}</b>")
        id_label.setObjectName("detailTitle")
        id_label.setToolTip(a.id)
        header.addWidget(id_label)
        header.addStretch()

        badge = QLabel(status.value)
        badge.setObjectName(f"badge_{status.name}")
        header.addWidget(badge)
        layout.addLayout(header)

        layout.addSpacing(16)

        # ── Route banner ───────────────────────────────────────────────────
        route_frame = QFrame()
        route_frame.setObjectName("routeFrame")
        route_layout = QHBoxLayout(route_frame)
        route_layout.setContentsMargins(16, 14, 16, 14)

        origin_lbl = QLabel(a.origin)
        origin_lbl.setObjectName("routeCity")
        arrow_lbl = QLabel("→")
        arrow_lbl.setObjectName("routeArrow")
        dest_lbl = QLabel(a.destination)
        dest_lbl.setObjectName("routeCity")

        route_layout.addWidget(origin_lbl)
        route_layout.addStretch()
        route_layout.addWidget(arrow_lbl)
        route_layout.addStretch()
        route_layout.addWidget(dest_lbl)
        layout.addWidget(route_frame)

        layout.addSpacing(20)

        # ── Info grid ──────────────────────────────────────────────────────
        eta = a.started_at + timedelta(minutes=a.estimated_duration_min)
        rows = [
            ("Truck", self._truck_label),
            ("Driver", self._driver_label),
            ("Started", _fmt_dt(a.started_at)),
            ("ETA", _fmt_dt(eta)),
            ("Duration", f"{a.estimated_duration_min} min"),
            ("Created", _fmt_dt(a.created_at) if a.created_at else "—"),
            ("Full ID", a.id),
        ]
        if a.cancelled_at:
            rows.insert(5, ("Cancelled", _fmt_dt(a.cancelled_at)))

        grid = QVBoxLayout()
        grid.setSpacing(0)
        for label, value in rows:
            row_widget = QFrame()
            row_widget.setObjectName("infoRow")
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 10, 0, 10)

            lbl = QLabel(label)
            lbl.setObjectName("infoKey")
            lbl.setFixedWidth(100)

            val = QLabel(value)
            val.setObjectName("infoValue")
            val.setWordWrap(True)
            val.setTextInteractionFlags(
                Qt.TextInteractionFlag.TextSelectableByMouse
            )

            row_layout.addWidget(lbl)
            row_layout.addWidget(val, 1)
            grid.addWidget(row_widget)

            sep = QFrame()
            sep.setObjectName("separator")
            sep.setFrameShape(QFrame.Shape.HLine)
            grid.addWidget(sep)

        layout.addLayout(grid)
        layout.addSpacing(24)

        # ── Action buttons ─────────────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        if status == AssignmentStatus.ACTIVE:
            self._cancel_btn = QPushButton("Cancel Assignment")
            self._cancel_btn.setObjectName("dangerButton")
            self._cancel_btn.clicked.connect(self._on_cancel)
            btn_row.addWidget(self._cancel_btn)

        close_btn = QPushButton("Close")
        close_btn.setObjectName("secondaryButton")
        close_btn.clicked.connect(self.accept)
        btn_row.addWidget(close_btn)

        layout.addLayout(btn_row)

    def _on_cancel(self) -> None:
        reply = QMessageBox.question(
            self,
            "Cancel Assignment",
            "Are you sure you want to cancel this assignment?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        try:
            with get_session() as session:
                AssignmentService(AssignmentRepository(session)).cancel_assignment(
                    self._assignment.id
                )
        except Exception as exc:
            QMessageBox.critical(self, "Error", str(exc))
            return
        self.assignment_cancelled.emit()
        self.accept()

    def _apply_styles(self) -> None:
        c = colors()
        status = self._assignment.status

        if status == AssignmentStatus.ACTIVE:
            badge_bg, badge_fg = "#E8F5E9", "#2E7D32"
        elif status == AssignmentStatus.CANCELLED:
            badge_bg, badge_fg = c["surface"], c["subtext"]
        else:
            badge_bg, badge_fg = c["surface"], c["text"]

        self.setStyleSheet(f"""
            QDialog {{
                background: {c['bg']};
            }}
            QLabel#detailTitle {{
                font-size: 15px;
                color: {c['text']};
            }}
            QLabel#badge_ACTIVE {{
                background: {badge_bg if status == AssignmentStatus.ACTIVE else c['surface']};
                color: {badge_fg if status == AssignmentStatus.ACTIVE else c['subtext']};
                border-radius: 4px;
                padding: 3px 10px;
                font-size: 11px;
                font-weight: bold;
            }}
            QLabel#badge_COMPLETED {{
                background: {badge_bg if status == AssignmentStatus.COMPLETED else c['surface']};
                color: {badge_fg if status == AssignmentStatus.COMPLETED else c['text']};
                border-radius: 4px;
                padding: 3px 10px;
                font-size: 11px;
                font-weight: bold;
            }}
            QLabel#badge_CANCELLED {{
                background: {badge_bg if status == AssignmentStatus.CANCELLED else c['surface']};
                color: {badge_fg if status == AssignmentStatus.CANCELLED else c['text']};
                border-radius: 4px;
                padding: 3px 10px;
                font-size: 11px;
                font-weight: bold;
            }}
            QFrame#routeFrame {{
                background: {c['surface']};
                border: 1px solid {c['border']};
                border-radius: 6px;
            }}
            QLabel#routeCity {{
                font-size: 16px;
                font-weight: bold;
                color: {c['text']};
            }}
            QLabel#routeArrow {{
                font-size: 18px;
                color: {c['subtext']};
            }}
            QLabel#infoKey {{
                font-size: 12px;
                color: {c['subtext']};
                font-weight: bold;
                text-transform: uppercase;
            }}
            QLabel#infoValue {{
                font-size: 13px;
                color: {c['text']};
            }}
            QFrame#separator {{
                color: {c['border']};
                background: {c['border']};
                max-height: 1px;
            }}
            QPushButton#dangerButton {{
                background: transparent;
                color: {c['danger']};
                border: 1px solid {c['danger']};
                border-radius: 4px;
                padding: 8px 18px;
                font-size: 13px;
            }}
            QPushButton#dangerButton:hover {{
                background: {c['danger']};
                color: {c['bg']};
            }}
            QPushButton#secondaryButton {{
                background: transparent;
                color: {c['text']};
                border: 1px solid {c['border']};
                border-radius: 4px;
                padding: 8px 18px;
                font-size: 13px;
            }}
            QPushButton#secondaryButton:hover {{
                background: {c['surface']};
            }}
        """)
