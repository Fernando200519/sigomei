# client/gui/components/asignar_tecnico_dialog.py
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QMessageBox
from PyQt6.QtCore import Qt

class AsignarTecnicoDialog(QDialog):
    def __init__(self, id_orden, main_window):
        super().__init__()
        self.id_orden = id_orden
        self.main_window = main_window
        self.setWindowTitle("👤 Asignar Técnico a Orden")
        self.setMinimumWidth(400)
        self.init_ui()
        self.cargar_tecnicos_aptos()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(12)

        self.lbl_info = QLabel(f"Selecciona el técnico para la orden: <b>{self.id_orden}</b>")
        self.lbl_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_info)

        self.cb_tecnicos = QComboBox()
        self.cb_tecnicos.setStyleSheet("padding: 4px; border: 1px solid #CFD8DC; border-radius: 4px;")
        layout.addWidget(self.cb_tecnicos)

        # Botonera
        btn_layout = QHBoxLayout()
        self.btn_asignar = QPushButton("Asignar")
        self.btn_asignar.clicked.connect(self._on_asignar_clicked)
        self.btn_asignar.setStyleSheet("background-color: #1565C0; color: white; font-weight: bold; padding: 5px;")
        
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.clicked.connect(self.reject)
        self.btn_cancelar.setStyleSheet("padding: 5px;")
        
        btn_layout.addWidget(self.btn_asignar)
        btn_layout.addWidget(self.btn_cancelar)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def cargar_tecnicos_aptos(self):
        """Consulta los requerimientos de la orden y filtra los técnicos aptos desde el servidor."""
        try:
            token = getattr(self.main_window, 'token', '')
            
            # 1. Consultar el detalle de la orden
            orden_detalles = self.main_window.proxy.consultar_orden(token, self.id_orden)
            if not orden_detalles:
                QMessageBox.warning(self, "Error", "No se pudieron recuperar los detalles de la orden.")
                self.reject()
                return
                
            # Este campo viene de tu DB: Electrico, Mecanico, Hidraulico, o Neumatico
            especialidad_requerida = orden_detalles.get("tipo_mantenimiento")

            # 2. Listar personal
            todos_tecnicos = self.main_window.proxy.listar_tecnicos(token)

            self.cb_tecnicos.clear()
            tecnicos_filtrados = 0

            # 3. Filtrar correctamente
            for tec in todos_tecnicos:
                estatus = tec.get("estatus")
                esp_tec = tec.get("especialidad")
                id_biz = tec.get("id_tecnico")

                # CORRECCIÓN: Comparamos directamente contra la especialidad_requerida
                # Eliminamos la dependencia del list(todos_tecnicos)[0]
                if estatus == "Activo" and esp_tec and esp_tec.lower() == especialidad_requerida.lower():
                    texto = f"{id_biz} — {tec.get('nombre_completo')} ({esp_tec})"
                    self.cb_tecnicos.addItem(texto, id_biz)
                    tecnicos_filtrados += 1

            if tecnicos_filtrados == 0:
                self.cb_tecnicos.addItem(f"⚠️ No hay técnicos disponibles en {especialidad_requerida}", None)
                self.btn_asignar.setDisabled(True)
                self.btn_asignar.setStyleSheet("background-color: #B0BEC5; color: white;")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Fallo al cargar técnicos desde el servidor:\n{e}")

    def _on_asignar_clicked(self):
        id_tecnico = self.cb_tecnicos.currentData()
        if not id_tecnico:
            QMessageBox.warning(self, "Advertencia", "Debes seleccionar un técnico válido.")
            return

        token = getattr(self.main_window, 'token', '')
        try:
            # Invoca la asignación remota inyectando el token de seguridad obligatorio
            exito = self.main_window.proxy.asignar_tecnico(token, self.id_orden, id_tecnico)
            if exito:
                QMessageBox.information(self, "Éxito", f"Técnico {id_tecnico} asignado a la orden con éxito.")
                self.accept()
        except PermissionError as e: # Captura si la orden no está en estado 'Programada' (EstadoInvalidoError)
            QMessageBox.warning(self, "Operación Denegada", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo completar la asignación:\n{e}")