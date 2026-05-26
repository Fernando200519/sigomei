from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, 
    QLineEdit, QComboBox, QDateEdit, QPushButton, QTableWidget, 
    QTableWidgetItem, QHeaderView, QMessageBox
)
from PyQt6.QtCore import QDate

class EquiposView(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()
        self.cargar_equipos()

    def init_ui(self):
        main_layout = QHBoxLayout()

        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)

        title_list = QLabel("Catálogo de Equipos Industriales")
        title_list.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 5px;")
        left_layout.addWidget(title_list)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID Equipo", "Nombre", "Tipo", "Ubicación", "Estado", "Criticidad"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        left_layout.addWidget(self.table)

        self.btn_refrescar = QPushButton("Actualizar Lista")
        self.btn_refrescar.clicked.connect(self.cargar_equipos)
        left_layout.addWidget(self.btn_refrescar)

        right_container = QWidget()
        right_container.setFixedWidth(320)
        right_layout = QVBoxLayout(right_container)

        title_form = QLabel("Registrar Nuevo Equipo")
        title_form.setStyleSheet("font-size: 14px; font-weight: bold; color: #1565C0; margin-bottom: 5px;")
        right_layout.addWidget(title_form)

        form_layout = QFormLayout()

        self.txt_id = QLineEdit()
        self.txt_id.setPlaceholderText("Ej. EQ-007")
        
        self.txt_nombre = QLineEdit()
        self.txt_nombre.setPlaceholderText("Ej. Motor Extractor M1")
        
        self.txt_marca = QLineEdit()
        self.txt_marca.setPlaceholderText("Ej. Siemens")
        
        self.txt_modelo = QLineEdit()
        self.txt_modelo.setPlaceholderText("Ej. V20-3HP")
        
        self.txt_serie = QLineEdit()
        self.txt_serie.setPlaceholderText("Ej. SN-XYZ-789")
        
        self.txt_ubicacion = QLineEdit()
        self.txt_ubicacion.setPlaceholderText("Ej. Nave B - Línea 2")

        self.cb_tipo = QComboBox()
        self.cb_tipo.addItems(["Electrico", "Mecanico", "Hidraulico", "Neumatico"])

        self.cb_estado = QComboBox()
        self.cb_estado.addItems(["Operativo", "En Mantenimiento", "Fuera de Servicio"])

        self.cb_criticidad = QComboBox()
        self.cb_criticidad.addItems(["Baja", "Media", "Alta"])

        self.date_instalacion = QDateEdit()
        self.date_instalacion.setCalendarPopup(True)
        self.date_instalacion.setDate(QDate.currentDate())

        form_layout.addRow("ID Equipo:", self.txt_id)
        form_layout.addRow("Nombre:", self.txt_nombre)
        form_layout.addRow("Tipo:", self.cb_tipo)
        form_layout.addRow("Marca:", self.txt_marca)
        form_layout.addRow("Modelo:", self.txt_modelo)
        form_layout.addRow("Núm. Serie:", self.txt_serie)
        form_layout.addRow("Ubicación:", self.txt_ubicacion)
        form_layout.addRow("Instalación:", self.date_instalacion)
        form_layout.addRow("Estado Op.:", self.cb_estado)
        form_layout.addRow("Criticidad:", self.cb_criticidad)

        right_layout.addLayout(form_layout)

        self.btn_registrar = QPushButton("💾 Guardar en Base de Datos")
        self.btn_registrar.clicked.connect(self._on_registrar_clicked)
        self.btn_registrar.setStyleSheet("background-color: #1565C0; color: white; font-weight: bold; padding: 6px;")
        right_layout.addWidget(self.btn_registrar)
        right_layout.addStretch()

        main_layout.addWidget(left_container, stretch=3)
        main_layout.addWidget(right_container, stretch=1)
        self.setLayout(main_layout)

    def cargar_equipos(self):
        """Consulta los equipos al servidor y llena la tabla."""
        try:
            if hasattr(self.main_window.proxy, 'listar_equipos'):
                equipos = self.main_window.proxy.listar_equipos()
            else:
                equipos = []

            self.table.setRowCount(0)
            for row_idx, eq in enumerate(equipos):
                self.table.insertRow(row_idx)
                self.table.setItem(row_idx, 0, QTableWidgetItem(str(eq["id_equipo"])))
                self.table.setItem(row_idx, 1, QTableWidgetItem(str(eq["nombre"])))
                self.table.setItem(row_idx, 2, QTableWidgetItem(str(eq["tipo"])))
                self.table.setItem(row_idx, 3, QTableWidgetItem(str(eq["ubicacion_planta"])))
                self.table.setItem(row_idx, 4, QTableWidgetItem(str(eq["estado_operativo"])))
                self.table.setItem(row_idx, 5, QTableWidgetItem(str(eq["criticidad"])))
        except Exception as e:
            QMessageBox.critical(self, "Error de Datos", f"No se pudieron cargar los equipos:\n{e}")

    def _on_registrar_clicked(self):
        """Captura los datos del formulario, los valida localmente y los envía al Proxy."""
        id_eq = self.txt_id.text().strip()
        nombre = self.txt_nombre.text().strip()
        marca = self.txt_marca.text().strip()
        modelo = self.txt_modelo.text().strip()
        serie = self.txt_serie.text().strip()
        ubicacion = self.txt_ubicacion.text().strip()
        
        tipo = self.cb_tipo.currentText()
        estado = self.cb_estado.currentText()
        criticidad = self.cb_criticidad.currentText()
        fecha_inst_str = self.date_instalacion.date().toString("yyyy-MM-dd")

        if not all([id_eq, nombre, marca, modelo, serie, ubicacion]):
            QMessageBox.warning(self, "Campos Vacíos", "Por favor completa todos los campos del formulario.")
            return

        try:
            exito = self.main_window.proxy.alta_equipo(
                id_eq, nombre, tipo, marca, modelo, 
                serie, ubicacion, fecha_inst_str, estado, criticidad
            )
            
            if exito:
                QMessageBox.information(self, "Éxito", f"Equipo '{nombre}' dado de alta exitosamente.")
                self._limpiar_formulario()
                self.cargar_equipos()
                
        except ValueError as e:
            QMessageBox.warning(self, "Registro Denegado", str(e).replace("EntidadDuplicadaError: ", ""))
        except Exception as e:
            QMessageBox.critical(self, "Error de Servidor", f"No se pudo guardar el registro:\n{e}")

    def _limpiar_formulario(self):
        """Limpia los campos de texto después de un registro exitoso."""
        self.txt_id.clear()
        self.txt_nombre.clear()
        self.txt_marca.clear()
        self.txt_modelo.clear()
        self.txt_serie.clear()
        self.txt_ubicacion.clear()
        self.cb_tipo.setCurrentIndex(0)
        self.cb_estado.setCurrentIndex(0)
        self.cb_criticidad.setCurrentIndex(0)
        self.date_instalacion.setDate(QDate.currentDate())