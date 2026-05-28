from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QDateEdit, QDoubleSpinBox, QPushButton, QMessageBox
)
from PyQt6.QtCore import QDate, Qt

class FinalizarOrdenDialog(QDialog):
    def __init__(self, id_orden, main_window):
        super().__init__()
        self.id_orden = id_orden
        self.main_window = main_window
        
        self.setWindowTitle("Finalizar Orden de Mantenimiento")
        self.setMinimumWidth(350)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(12)

        lbl_info = QLabel(f"Cierre definitivo de la orden: <b>{self.id_orden}</b>")
        lbl_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_info)

        # Campos
        layout.addWidget(QLabel("Fecha de Cierre:"))
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setStyleSheet("padding: 4px; border: 1px solid #CFD8DC; border-radius: 4px;")
        layout.addWidget(self.date_edit)

        layout.addWidget(QLabel("Costo Real ($):"))
        self.spin_costo = QDoubleSpinBox()
        self.spin_costo.setRange(0.0, 99999999.99)
        self.spin_costo.setDecimals(2)
        self.spin_costo.setPrefix("$ ")
        self.spin_costo.setStyleSheet("padding: 4px; border: 1px solid #CFD8DC; border-radius: 4px;")
        layout.addWidget(self.spin_costo)

        # Botonera
        btn_layout = QHBoxLayout()
        self.btn_aceptar = QPushButton("Finalizar Orden")
        self.btn_aceptar.clicked.connect(self._on_aceptar_clicked)
        self.btn_aceptar.setStyleSheet("background-color: #2E7D32; color: white; font-weight: bold; padding: 5px;")
        
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.clicked.connect(self.reject)
        self.btn_cancelar.setStyleSheet("padding: 5px;")
        
        btn_layout.addWidget(self.btn_aceptar)
        btn_layout.addWidget(self.btn_cancelar)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def _on_aceptar_clicked(self):
        fecha_cierre_str = self.date_edit.date().toString("yyyy-MM-dd")
        costo_real = self.spin_costo.value()

        if costo_real <= 0:
            QMessageBox.warning(self, "Validación", "El costo real debe ser un monto mayor a cero.")
            return

        # CORRECCIÓN: Recuperar el token de la sesión activa
        token = getattr(self.main_window, 'token', '')

        try:
            # CORRECCIÓN: Pasar el 'token' como primer parámetro obligatorio
            exito = self.main_window.proxy.finalizar_orden(token, self.id_orden, fecha_cierre_str, costo_real)
            if exito:
                QMessageBox.information(
                    self, "Éxito", f"La orden {self.id_orden} ha sido cerrada y guardada con éxito."
                )
                self.accept()
        except PermissionError as e:
            QMessageBox.warning(self, "Regla de Negocio Denegada", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error de Red", f"No se pudo finalizar la orden:\n{e}")