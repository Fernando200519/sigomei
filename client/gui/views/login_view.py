from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFormLayout
from PyQt6.QtCore import pyqtSignal

class LoginView(QWidget):
    login_attempted = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        title = QLabel("SIGOMEI - Inicio de Sesión")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 20px; color: #1565C0;")
        layout.addWidget(title)

        form_layout = QFormLayout()
        
        self.txt_correo = QLineEdit()
        self.txt_correo.setPlaceholderText("Ej. carlos.ruiz@empresa.mx")
        
        self.txt_password = QLineEdit()
        self.txt_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_password.setPlaceholderText("••••••••")

        form_layout.addRow("Correo Electrónico:", self.txt_correo)
        form_layout.addRow("Contraseña:", self.txt_password)
        layout.addLayout(form_layout)

        self.btn_login = QPushButton("Ingresar al Sistema")
        self.btn_login.clicked.connect(self._on_login_clicked)
        self.btn_login.setStyleSheet("background-color: #1565C0; color: white; font-weight: bold; padding: 8px; font-size: 13px;")
        layout.addWidget(self.btn_login)

        self.setLayout(layout)

    def _on_login_clicked(self):
        correo = self.txt_correo.text().strip()
        password = self.txt_password.text()

        self.login_attempted.emit(correo, password)