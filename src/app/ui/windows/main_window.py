from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QStackedWidget,
    QToolBar,
    QPushButton,
    QSizePolicy,
)

from app.ui.theme import ThemeManager, colors
from app.ui.widgets.sidebar import Sidebar
from app.ui.views.assignment_view import AssignmentView
from app.ui.views.driver_view import DriverView
from app.ui.views.truck_view import TruckView


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Truck Logistics")
        self.resize(1200, 800)

        self._build_toolbar()
        self._build_body()
        self._apply_window_styles()

    def _build_toolbar(self) -> None:
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        toolbar.setContextMenuPolicy(Qt.ContextMenuPolicy.PreventContextMenu)
        toolbar.setObjectName("mainToolbar")

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        toolbar.addWidget(spacer)

        self._theme_btn = QPushButton()
        self._theme_btn.setObjectName("themeToggle")
        self._theme_btn.setFixedSize(32, 32)
        self._theme_btn.clicked.connect(self._toggle_theme)
        toolbar.addWidget(self._theme_btn)

        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)
        self._toolbar = toolbar

    def _build_body(self) -> None:
        root = QWidget()
        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._sidebar = Sidebar()
        self._sidebar.page_changed.connect(self._on_page_changed)

        self._stack = QStackedWidget()
        self._assignment_view = AssignmentView()
        self._truck_view = TruckView()
        self._driver_view = DriverView()
        self._stack.addWidget(self._assignment_view)  # index 0
        self._stack.addWidget(self._truck_view)        # index 1
        self._stack.addWidget(self._driver_view)       # index 2

        layout.addWidget(self._sidebar)
        layout.addWidget(self._stack)

        self.setCentralWidget(root)

    def _on_page_changed(self, index: int) -> None:
        self._stack.setCurrentIndex(index)
        view = self._stack.currentWidget()
        if hasattr(view, "refresh"):
            view.refresh()

    def _toggle_theme(self) -> None:
        ThemeManager.toggle()
        self._apply_window_styles()
        self._sidebar.apply_theme()
        self._assignment_view.apply_theme()
        self._truck_view.apply_theme()
        self._driver_view.apply_theme()

    def _apply_window_styles(self) -> None:
        c = colors()
        is_dark = ThemeManager.is_dark()
        self._theme_btn.setText("☀" if is_dark else "☾")
        self.setStyleSheet(f"""
            QMainWindow {{
                background: {c['bg']};
            }}
            QToolBar#mainToolbar {{
                background: {c['surface']};
                border: none;
                border-bottom: 1px solid {c['border']};
                spacing: 4px;
                padding: 4px 8px;
            }}
            QPushButton#themeToggle {{
                background: transparent;
                border: 1px solid {c['border']};
                border-radius: 4px;
                font-size: 16px;
                color: {c['text']};
            }}
            QPushButton#themeToggle:hover {{
                background: {c['border']};
            }}
        """)
