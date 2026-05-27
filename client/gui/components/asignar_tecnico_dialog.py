from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QMessageBox

class AsignarTecnicoDialog(QDialog):
    def __init__(self, id_orden, main_window):
        super().__init__()
        self.id_orden = id_orden
        self.main_window = main_window
        
        self.setWindowTitle("Asignar Técnico a Orden")
        self.resize(380, 160)
        self.init_ui()
        self.cargar_tecnicos_disponibles()

    def init_ui(self):
        layout = QVBoxLayout()

        lbl_info = QLabel(f"Selecciona el técnico para la orden: <b>{self.id_orden}</b>")
        layout.addWidget(lbl_info)

        self.cb_tecnicos = QComboBox()
        layout.addWidget(self.cb_tecnicos)

        btn_layout = QHBoxLayout()
        self.btn_aceptar = QPushButton("Asignar")
        self.btn_cancelar = QPushButton("Cancelar")
        
        self.btn_aceptar.clicked.connect(self._on_aceptar_clicked)
        self.btn_cancelar.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.btn_aceptar)
        btn_layout.addWidget(self.btn_cancelar)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def cargar_tecnicos_disponibles(self):
        """Pide los técnicos al servidor y los monta en el ComboBox."""
        try:
            tecnicos = self.main_window.proxy.listar_tecnicos()
            
            if not tecnicos:
                self.cb_tecnicos.addItem("No hay técnicos registrados", None)
                self.btn_aceptar.setEnabled(False)
                return

            for tec in tecnicos:
                texto_visible = f"{tec['nombre_completo']} — {tec['especialidad']} ({tec['estatus']})"
                self.cb_tecnicos.addItem(texto_visible, tec['id_tecnico'])
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Fallo al cargar técnicos desde el servidor:\n{e}")
            self.reject()

    def _on_aceptar_clicked(self):
        id_tecnico = self.cb_tecnicos.currentData()
        
        if not id_tecnico:
            QMessageBox.warning(self, "Advertencia", "Selección inválida.")
            return

        try:
            exito = self.main_window.proxy.asignar_tecnico(self.id_orden, id_tecnico)
            
            if exito:
                QMessageBox.information(self, "Éxito", f"Técnico asignado correctamente a la orden {self.id_orden}.")
                self.accept()
                
        except PermissionError as e:
            QMessageBox.warning(self, "Regla de Negocio Denegada", str(e).replace("ReglaNegocioError: ", ""))
        except Exception as e:
            QMessageBox.critical(self, "Error de Red", f"No se pudo completar la asignación:\n{e}")