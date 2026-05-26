import sys
import Pyro5.errors
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QMessageBox, QWidget, QLabel, QVBoxLayout

from client.gui.views.login_view import LoginView
from client.gui.views.dashboard_view import DashboardView
from client.proxy.sigomei_proxy import SigomeiProxy


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SIGOMEI — Panel de Control")
        self.resize(900, 600)

        try:
            self.proxy = SigomeiProxy()
            self.sesion_token = None 
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

    def handle_login(self, username, password):
        """Maneja la lógica de comunicación con el servidor remoto."""
        if not username or not password:
            QMessageBox.warning(self, "Campos Vacíos", "Por favor introduce un usuario y contraseña.")
            return

        try:
            token = self.proxy.login(username, password)
            self.sesion_token = token
            
            QMessageBox.information(self, "Acceso Autorizado", "Sesión iniciada correctamente.")
            
            self.dashboard_view.ordenes_view.cargar_ordenes()
            
            self.stacked_widget.setCurrentIndex(1)
            
        except ConnectionRefusedError as e:
            QMessageBox.critical(self, "Error de Autenticación", str(e).replace("AutenticacionError: ", ""))
            
        except Pyro5.errors.CommunicationError:
            QMessageBox.critical(
                self, 
                "Error de Red", 
                "No se pudo establecer conexión con el servidor SIGOMEI.\n"
                "Verifica que el servicio esté encendido e intenta de nuevo."
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Error Crítico", f"Ocurrió un problema inesperado:\n{e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())