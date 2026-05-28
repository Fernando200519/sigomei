import sys
import Pyro5.errors
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QMessageBox

from client.gui.views.login_view import LoginView
from client.gui.views.dashboard_view import DashboardView
from client.proxy.sigomei_proxy import SigomeiProxy


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SIGOMEI — Panel de Control")
        self.resize(1024, 700)

        try:
            self.proxy = SigomeiProxy()
            self.token = None
            self.id_rol = None
        except Exception as e:
            QMessageBox.critical(self, "Error de Configuración", f"No se pudo inicializar el proxy: {e}")
            sys.exit(1)

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        self.login_view = LoginView()
        self.dashboard_view = DashboardView(main_window=self)

        self.stacked_widget.addWidget(self.login_view)
        self.stacked_widget.addWidget(self.dashboard_view)

        self.login_view.login_attempted.connect(self.handle_login)

    def handle_login(self, correo, password):
        """Maneja la lógica de comunicación y autenticación con el servidor remoto."""
        if not correo or not password:
            QMessageBox.warning(self, "Campos Vacíos", "Por favor introduce tu correo y contraseña.")
            return

        try:
            token = self.proxy.login(correo, password)
            self.token = token
            
            try:
                self.proxy.listar_usuarios(self.token)
                self.id_rol = 3
            except PermissionError:
                self.id_rol = 4
            
            QMessageBox.information(self, "Acceso Autorizado", "Sesión iniciada correctamente.")

            self.dashboard_view.inicializar_vistas()
            
            self.stacked_widget.setCurrentIndex(1)
            
        except ConnectionRefusedError as e:
            QMessageBox.critical(self, "Error de Autenticación", str(e).replace("AutenticacionError: ", ""))
            
        except Pyro5.errors.CommunicationError:
            QMessageBox.critical(
                self, 
                "Error de Red", 
                "No se pudo establecer conexión con el servidor SIGOMEI.\n"
                "Verifica que el servicio del Backend Docker/Pyro5 esté encendido."
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Error Crítico", f"Ocurrió un problema inesperado:\n{e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())