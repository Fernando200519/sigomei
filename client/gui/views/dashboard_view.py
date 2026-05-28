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

    def inicializar_vistas(self):
        """
        Orquesta la configuración de permisos y la carga de datos remotos 
        en todas las sub-vistas una vez que el token y el rol están listos.
        """
        # --- Configuración de pestaña: Equipos ---
        if hasattr(self.equipos_view, 'verificar_permisos_ui'):
            self.equipos_view.verificar_permisos_ui()
        if hasattr(self.equipos_view, 'cargar_equipos'):
            self.equipos_view.cargar_equipos()
            
        # --- Configuración de pestaña: Órdenes ---
        if hasattr(self.ordenes_view, 'verificar_permisos_ui'):
            self.ordenes_view.verificar_permisos_ui()
        if hasattr(self.ordenes_view, 'cargar_ordenes'):
            self.ordenes_view.cargar_ordenes()
            
        # --- Configuración de pestaña: Técnicos ---
        if hasattr(self.tecnicos_view, 'verificar_permisos_ui'):
            self.tecnicos_view.verificar_permisos_ui()
        if hasattr(self.tecnicos_view, 'cargar_tecnicos'):
            self.tecnicos_view.cargar_tecnicos()