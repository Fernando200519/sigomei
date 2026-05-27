# client/gui/views/tecnicos_view.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class TecnicosView(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        title = QLabel("👷 Gestión de Técnicos")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        layout.addWidget(QLabel("Próximamente: Catálogo de personal, especialidades y niveles de certificación."))
        layout.addStretch()
        self.setLayout(layout)