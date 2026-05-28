# client/gui/components/crear_orden_dialog.py
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, 
    QComboBox, QDateEdit, QTextEdit, QPushButton, QMessageBox
)
from PyQt6.QtCore import QDate, Qt

class CrearOrdenDialog(QDialog):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle("➕ Registrar Nueva Orden de Mantenimiento")
        self.setMinimumWidth(420)
        self.init_ui()
        self.cargar_equipos_disponibles()

    def init_ui(self):
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form_layout.setSpacing(8)

        estilo_inputs = "QLineEdit, QComboBox, QDateEdit, QTextEdit { padding: 4px; border: 1px solid #CFD8DC; border-radius: 4px; }"

        self.txt_id = QLineEdit()
        self.txt_id.setPlaceholderText("Ej. OM-006")
        self.txt_id.setStyleSheet(estilo_inputs)

        self.cb_equipo = QComboBox()
        self.cb_equipo.setStyleSheet(estilo_inputs)
        self.cb_equipo.currentIndexChanged.connect(self._on_equipo_cambiado)

        self.cb_tipo = QComboBox()
        self.cb_tipo.addItems(["Electrico", "Mecanico", "Hidraulico", "Neumatico"])
        self.cb_tipo.setStyleSheet(estilo_inputs)

        self.date_prog = QDateEdit()
        self.date_prog.setCalendarPopup(True)
        self.date_prog.setDate(QDate.currentDate())
        # CORRECCIÓN: La fecha ahora es estrictamente de lectura (fecha de creación automática)
        self.date_prog.setReadOnly(True)
        self.date_prog.setStyleSheet(estilo_inputs)

        self.txt_desc = QTextEdit()
        self.txt_desc.setPlaceholderText("Describe detalladamente las acciones de mantenimiento a realizar...")
        self.txt_desc.setStyleSheet(estilo_inputs)
        self.txt_desc.setMaximumHeight(80)

        self.txt_costo = QLineEdit()
        self.txt_costo.setPlaceholderText("Ej. 2500.00")
        self.txt_costo.setStyleSheet(estilo_inputs)

        form_layout.addRow("ID Orden *:", self.txt_id)
        form_layout.addRow("Seleccionar Equipo *:", self.cb_equipo)
        form_layout.addRow("Tipo Mantenimiento *:", self.cb_tipo)
        form_layout.addRow("Fecha Programada:", self.date_prog)
        form_layout.addRow("Descripción Trabajo:", self.txt_desc)
        form_layout.addRow("Costo Estimado ($):", self.txt_costo)

        layout.addLayout(form_layout)

        self.btn_guardar = QPushButton("💾 Crear Orden de Mantenimiento")
        self.btn_guardar.clicked.connect(self._on_guardar_clicked)
        self.btn_guardar.setStyleSheet("background-color: #1565C0; color: white; font-weight: bold; padding: 7px; border-radius: 4px;")
        layout.addWidget(self.btn_guardar)

        self.setLayout(layout)

    def cargar_equipos_disponibles(self):
        """Consulta al servidor los equipos y las órdenes activas para filtrar la disponibilidad."""
        try:
            token = getattr(self.main_window, 'token', '')
            todos_equipos = self.main_window.proxy.listar_equipos(token)
            todas_ordenes = self.main_window.proxy.listar_ordenes_por_filtro(token, {})
            
            estados_activos = {"Programada", "En ejecucion", "Pendiente de cierre"}
            equipos_ocupados = {
                orden.get("id_equipo") for orden in todas_ordenes 
                if orden.get("estado_orden") in estados_activos
            }

            self.cb_equipo.clear()
            self.lista_datos_equipos = {}

            equipos_filtrados = 0
            for eq in todos_equipos:
                id_biz = eq.get("id_equipo")
                estado_op = eq.get("estado_operativo")
                
                if estado_op == "Operativo" and id_biz not in equipos_ocupados:
                    texto_descriptivo = f"{id_biz} — {eq.get('nombre')} ({eq.get('tipo')})"
                    self.cb_equipo.addItem(texto_descriptivo, id_biz)
                    self.lista_datos_equipos[id_biz] = eq
                    equipos_filtrados += 1

            if equipos_filtrados == 0:
                self.cb_equipo.addItem("⚠️ No hay equipos operativos disponibles", None)
                self.btn_guardar.setDisabled(True)
                self.btn_guardar.setStyleSheet("background-color: #B0BEC5; color: white; font-weight: bold; padding: 7px;")

        except Exception as e:
            QMessageBox.critical(self, "Error de Inicialización", f"Fallo al calcular la disponibilidad de equipos:\n{e}")

    def _on_equipo_cambiado(self, index):
        id_biz = self.cb_equipo.itemData(index)
        if id_biz and id_biz in self.lista_datos_equipos:
            eq = self.lista_datos_equipos[id_biz]
            tipo_industrial = eq.get("tipo", "")
            if tipo_industrial in ["Electrico", "Mecanico", "Hidraulico", "Neumatico"]:
                self.cb_tipo.setCurrentText(tipo_industrial)

    def _on_guardar_clicked(self):
        id_orden = self.txt_id.text().strip()
        id_equipo = self.cb_equipo.currentData()
        
        if not id_orden:
            QMessageBox.warning(self, "Campos Vacíos", "El código identificador de la orden es obligatorio.")
            return

        if not id_equipo:
            QMessageBox.warning(self, "Disponibilidad", "Debes seleccionar un equipo industrial de la lista.")
            return

        try:
            costo_estimado = float(self.txt_costo.text().strip() or 0.0)
        except ValueError:
            QMessageBox.warning(self, "Formato Incorrecto", "El costo estimado debe ser un valor numérico válido.")
            return

        token = getattr(self.main_window, 'token', '')
        try:
            # CORRECCIÓN CRÍTICA: Se corrigió el nombre de la variable remota a 'costo_estimado'
            exito = self.main_window.proxy.crear_orden(
                token,
                id_orden,
                id_equipo,
                self.cb_tipo.currentText(),
                self.date_prog.date().toString("yyyy-MM-dd"),
                self.txt_desc.toPlainText().strip(),
                costo_estimado
            )
            
            if exito:
                QMessageBox.information(self, "Éxito", f"Orden '{id_orden}' registrada y establecida como 'Programada'.")
                self.accept()
                
        except ValueError as e:
            QMessageBox.warning(self, "Folio Duplicado", str(e).replace("EntidadDuplicadaError: ", ""))
        except Exception as e:
            QMessageBox.critical(self, "Error de Servidor", f"No se pudo completar el registro:\n{e}")