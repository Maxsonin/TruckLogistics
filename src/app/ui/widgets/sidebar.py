from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton


class Sidebar(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        self.btn_dashboard = QPushButton("Dashboard")
        self.btn_trucks = QPushButton("Trucks")
        self.btn_routes = QPushButton("Routes")

        layout.addWidget(self.btn_dashboard)
        layout.addWidget(self.btn_trucks)
        layout.addWidget(self.btn_routes)
        layout.addStretch()