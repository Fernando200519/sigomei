from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget

from client.gui.views.ordenes_view import OrdenesView
from client.gui.views.equipos_view import EquiposView
from client.gui.views.tecnicos_view import TecnicosView

class DashboardView(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.tabs = QTabWidget()
        
        self.ordenes_view = OrdenesView(self.main_window)
        self.equipos_view = EquiposView(self.main_window)
        self.tecnicos_view = TecnicosView(self.main_window)

        self.tabs.addTab(self.ordenes_view, "📋 Órdenes de Mantenimiento")
        self.tabs.addTab(self.equipos_view, "⚙️ Equipos Industriales")
        self.tabs.addTab(self.tecnicos_view, "👷 Gestión de Técnicos")

        layout.addWidget(self.tabs)
        self.setLayout(layout)