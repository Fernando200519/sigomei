from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QDateEdit, QPushButton, QMessageBox
from PyQt6.QtCore import QDate

class IniciarEjecucionDialog(QDialog):
    def __init__(self, id_orden, main_window):
        super().__init__()
        self.id_orden = id_orden
        self.main_window = main_window
        
        self.setWindowTitle("Iniciar Ejecución de Orden")
        self.resize(300, 140)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        lbl_info = QLabel(f"Establecer inicio para la orden: <b>{self.id_orden}</b>")
        layout.addWidget(lbl_info)

        layout.addWidget(QLabel("Fecha de Inicio:"))
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        layout.addWidget(self.date_edit)

        btn_layout = QHBoxLayout()
        self.btn_aceptar = QPushButton("Confirmar Inicio")
        self.btn_cancelar = QPushButton("Cancelar")
        
        self.btn_aceptar.clicked.connect(self._on_aceptar_clicked)
        self.btn_cancelar.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.btn_aceptar)
        btn_layout.addWidget(self.btn_cancelar)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def _on_aceptar_clicked(self):
        fecha_inicio_str = self.date_edit.date().toString("yyyy-MM-dd")

        try:
            exito = self.main_window.proxy.iniciar_ejecucion(self.id_orden, fecha_inicio_str)
            if exito:
                QMessageBox.information(
                    self, "Éxito", f"La orden {self.id_orden} ahora está 'En ejecucion'."
                )
                self.accept()
        except PermissionError as e:
            QMessageBox.warning(self, "Regla de Negocio Denegada", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error de Red", f"No se pudo iniciar la orden:\n{e}")