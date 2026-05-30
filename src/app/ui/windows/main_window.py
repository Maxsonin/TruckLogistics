from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout
from app.ui.widgets.sidebar import Sidebar
from app.ui.views.dashboard_view import DashboardView


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Truck Logistics")
        self.resize(1200, 800)

        root = QWidget()
        layout = QHBoxLayout(root)

        self.sidebar = Sidebar()
        self.dashboard = DashboardView()

        layout.addWidget(self.sidebar)
        layout.addWidget(self.dashboard)

        self.setCentralWidget(root)