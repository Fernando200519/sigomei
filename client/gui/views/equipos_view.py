from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, 
    QLineEdit, QComboBox, QDateEdit, QPushButton, QTableWidget, 
    QTableWidgetItem, QHeaderView, QMessageBox, QGroupBox
)
from PyQt6.QtCore import QDate, Qt

class EquiposView(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # ================= PANEL IZQUIERDO: TABLA DE EQUIPOS =================
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # Grupo para la Tabla
        grupo_tabla = QGroupBox("Catálogo de Equipos Industriales")
        grupo_tabla.setStyleSheet("QGroupBox { font-size: 14px; font-weight: bold; color: #1565C0; }")
        tabla_layout = QVBoxLayout(grupo_tabla)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID Equipo", "Nombre", "Tipo", "Ubicación", "Estado", "Criticidad"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setStyleSheet("""
            QTableWidget { gridline-color: #E0E0E0; alternate-background-color: #F9F9F9; }
            QHeaderView::section { background-color: #F5F5F5; font-weight: bold; border: 1px solid #D3D3D3; }
        """)
        self.table.setAlternatingRowColors(True)
        self.table.itemSelectionChanged.connect(self._on_fila_seleccionada)
        tabla_layout.addWidget(self.table)

        self.btn_refrescar = QPushButton("🔄 Actualizar Lista de Equipos")
        self.btn_refrescar.setStyleSheet("padding: 6px; font-weight: bold;")
        self.btn_refrescar.clicked.connect(self.cargar_equipos)
        tabla_layout.addWidget(self.btn_refrescar)
        
        left_layout.addWidget(grupo_tabla)

        # ================= PANEL DERECHO: FORMULARIO CRUD =================
        self.grupo_formulario = QGroupBox("💾 Registrar Nuevo Equipo")
        self.grupo_formulario.setFixedWidth(360)
        self.grupo_formulario.setStyleSheet("""
            QGroupBox { font-size: 14px; font-weight: bold; color: #1565C0; border: 1px solid #B0BEC5; border-radius: 6px; margin-top: 12px; }
            QGroupBox::title { subcontrol-origin: margin; left: 8px; padding: 0 3px; }
        """)
        right_layout = QVBoxLayout(self.grupo_formulario)
        right_layout.setContentsMargins(12, 18, 12, 12)

        self.lbl_permiso_aviso = QLabel("")
        self.lbl_permiso_aviso.setStyleSheet("color: #D32F2F; font-weight: bold; font-size: 11px;")
        self.lbl_permiso_aviso.setWordWrap(True)
        right_layout.addWidget(self.lbl_permiso_aviso)

        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form_layout.setSpacing(8)

        # Estilo común para inputs
        estilo_inputs = "QLineEdit, QComboBox, QDateEdit { padding: 4px; border: 1px solid #CFD8DC; border-radius: 4px; }"

        self.txt_id = QLineEdit()
        self.txt_id.setPlaceholderText("Ej. EQ-001")
        self.txt_id.setStyleSheet(estilo_inputs)
        
        self.txt_nombre = QLineEdit()
        self.txt_nombre.setPlaceholderText("Ej. Compresor Atlas 01")
        self.txt_nombre.setStyleSheet(estilo_inputs)
        
        # CORRECCIÓN CRÍTICA: Se cambió de QLineEdit a QComboBox
        self.cb_tipo = QComboBox()
        self.cb_tipo.addItems(["Electrico", "Mecanico", "Hidraulico", "Neumatico"])
        self.cb_tipo.setStyleSheet(estilo_inputs)
        
        self.txt_marca = QLineEdit()
        self.txt_marca.setPlaceholderText("Ej. Atlas Copco")
        self.txt_marca.setStyleSheet(estilo_inputs)
        
        self.txt_modelo = QLineEdit()
        self.txt_modelo.setPlaceholderText("Ej. GA-90")
        self.txt_modelo.setStyleSheet(estilo_inputs)
        
        self.txt_serie = QLineEdit()
        self.txt_serie.setPlaceholderText("Ej. SN-ATL-001")
        self.txt_serie.setStyleSheet(estilo_inputs)
        
        self.txt_ubicacion = QLineEdit()
        self.txt_ubicacion.setPlaceholderText("Ej. Nave A – Zona 1")
        self.txt_ubicacion.setStyleSheet(estilo_inputs)

        self.cb_estado = QComboBox()
        self.cb_estado.addItems(["Operativo", "En Mantenimiento", "Fuera de Servicio"])
        self.cb_estado.setStyleSheet(estilo_inputs)

        self.cb_criticidad = QComboBox()
        self.cb_criticidad.addItems(["Baja", "Media", "Alta"])
        self.cb_criticidad.setStyleSheet(estilo_inputs)

        self.date_instalacion = QDateEdit()
        self.date_instalacion.setCalendarPopup(True)
        self.date_instalacion.setDate(QDate.currentDate())
        self.date_instalacion.setStyleSheet(estilo_inputs)

        form_layout.addRow("ID Equipo *:", self.txt_id)
        form_layout.addRow("Nombre *:", self.txt_nombre)
        form_layout.addRow("Tipo Industrial:", self.cb_tipo) # Cambiado a cb_tipo
        form_layout.addRow("Marca:", self.txt_marca)
        form_layout.addRow("Modelo:", self.txt_modelo)
        form_layout.addRow("Núm. Serie *:", self.txt_serie)
        form_layout.addRow("Ubicación Planta:", self.txt_ubicacion)
        form_layout.addRow("Fecha Inst.:", self.date_instalacion)
        form_layout.addRow("Estado Op. *:", self.cb_estado)
        form_layout.addRow("Criticidad *:", self.cb_criticidad)

        right_layout.addLayout(form_layout)
        right_layout.addSpacing(10)

        # BOTONES DE ACCIÓN CONFIGURADOS CON IDENTIDAD VISUAL
        self.btn_registrar = QPushButton("💾 Guardar Nuevo Equipo")
        self.btn_registrar.clicked.connect(self._on_registrar_clicked)
        self.btn_registrar.setStyleSheet("background-color: #1565C0; color: white; font-weight: bold; padding: 7px; border-radius: 4px;")
        right_layout.addWidget(self.btn_registrar)

        self.btn_modificar = QPushButton("✏️ Actualizar Cambios")
        self.btn_modificar.clicked.connect(self._on_modificar_clicked)
        self.btn_modificar.setStyleSheet("background-color: #2E7D32; color: white; font-weight: bold; padding: 7px; border-radius: 4px;")
        self.btn_modificar.setEnabled(False)
        right_layout.addWidget(self.btn_modificar)

        self.btn_eliminar = QPushButton("❌ Dar de Baja / Eliminar")
        self.btn_eliminar.clicked.connect(self._on_eliminar_clicked)
        self.btn_eliminar.setStyleSheet("background-color: #C62828; color: white; font-weight: bold; padding: 7px; border-radius: 4px;")
        self.btn_eliminar.setEnabled(False)
        right_layout.addWidget(self.btn_eliminar)

        self.btn_limpiar = QPushButton("🧹 Cancelar / Limpiar Campos")
        self.btn_limpiar.clicked.connect(self._limpiar_formulario)
        self.btn_limpiar.setStyleSheet("padding: 5px;")
        right_layout.addWidget(self.btn_limpiar)

        right_layout.addStretch()

        main_layout.addWidget(left_container, stretch=3)
        main_layout.addWidget(self.grupo_formulario, stretch=1)
        self.setLayout(main_layout)

    def verificar_permisos_ui(self):
        """Bloquea el CRUD únicamente si el usuario en sesión es un Técnico (Rol 4)."""
        id_rol_usuario = getattr(self.main_window, 'id_rol', None)
        
        if id_rol_usuario == 4:
            self.txt_id.setDisabled(True)
            self.txt_nombre.setDisabled(True)
            self.cb_tipo.setDisabled(True) # Ajustado
            self.txt_marca.setDisabled(True)
            self.txt_modelo.setDisabled(True)
            self.txt_serie.setDisabled(True)
            self.txt_ubicacion.setDisabled(True)
            self.cb_estado.setDisabled(True)
            self.cb_criticidad.setDisabled(True)
            self.date_instalacion.setDisabled(True)
            
            self.btn_registrar.hide()
            self.btn_modificar.hide()
            self.btn_eliminar.hide()
            self.btn_limpiar.hide()
            
            self.lbl_permiso_aviso.setText("⚠️ Modo Lectura: No cuentas con privilegios de edición sobre este catálogo.")
            self.grupo_formulario.setTitle("🔍 Detalles del Equipo Seleccionado")
        else:
            self.txt_id.setDisabled(False)
            self.btn_registrar.show()
            self.btn_modificar.show()
            self.btn_eliminar.show()
            self.btn_limpiar.show()
            self.lbl_permiso_aviso.setText("")
            self.grupo_formulario.setTitle("💾 Registrar Nuevo Equipo")

    def cargar_equipos(self):
        """Consulta remota estructurada de equipos."""
        try:
            token = getattr(self.main_window, 'token', '')
            equipos = self.main_window.proxy.listar_equipos(token) if hasattr(self.main_window.proxy, 'listar_equipos') else []

            self.table.setRowCount(0)
            for row_idx, eq in enumerate(equipos):
                self.table.insertRow(row_idx)
                self.table.setItem(row_idx, 0, QTableWidgetItem(str(eq.get("id_equipo", ""))))
                self.table.setItem(row_idx, 1, QTableWidgetItem(str(eq.get("nombre", ""))))
                self.table.setItem(row_idx, 2, QTableWidgetItem(str(eq.get("tipo", ""))))
                self.table.setItem(row_idx, 3, QTableWidgetItem(str(eq.get("ubicacion_planta", ""))))
                self.table.setItem(row_idx, 4, QTableWidgetItem(str(eq.get("estado_operativo", ""))))
                self.table.setItem(row_idx, 5, QTableWidgetItem(str(eq.get("criticidad", ""))))
        except Exception as e:
            QMessageBox.critical(self, "Error de Red", f"No se pudo sincronizar el listado central:\n{e}")

    def _on_fila_seleccionada(self):
        """Pasa el formulario al modo 'Edición' y rellena todos los campos."""
        filas_seleccionadas = self.table.selectionModel().selectedRows()
        if not filas_seleccionadas:
            return

        fila = filas_seleccionadas[0].row()
        item_id = self.table.item(fila, 0)
        if not item_id: return
        
        id_equipo = item_id.text()

        try:
            token = getattr(self.main_window, 'token', '')
            eq_detalles = self.main_window.proxy.consultar_equipo(token, id_equipo)
            
            if eq_detalles:
                self.txt_id.setText(str(eq_detalles.get("id_equipo", "")))
                self.txt_id.setDisabled(True)
                self.txt_nombre.setText(str(eq_detalles.get("nombre", "")))
                self.cb_tipo.setCurrentText(str(eq_detalles.get("tipo", "Mecanico"))) # Ajustado para QComboBox
                self.txt_marca.setText(str(eq_detalles.get("marca", "")))
                self.txt_modelo.setText(str(eq_detalles.get("modelo", "")))
                self.txt_serie.setText(str(eq_detalles.get("numero_serie", "")))
                self.txt_ubicacion.setText(str(eq_detalles.get("ubicacion_planta", "")))
                
                self.cb_estado.setCurrentText(str(eq_detalles.get("estado_operativo", "Operativo")))
                self.cb_criticidad.setCurrentText(str(eq_detalles.get("criticidad", "Media")))
                
                fecha_str = eq_detalles.get("fecha_instalacion")
                if fecha_str:
                    self.date_instalacion.setDate(QDate.fromString(str(fecha_str), "yyyy-MM-dd"))

                id_rol_usuario = getattr(self.main_window, 'id_rol', None)
                if id_rol_usuario != 4:
                    self.grupo_formulario.setTitle(f"✏️ Editando Equipo: {id_equipo}")
                    self.btn_registrar.setEnabled(False)
                    self.btn_modificar.setEnabled(True)
                    self.btn_eliminar.setEnabled(True)
        except Exception as e:
            QMessageBox.critical(self, "Error de Carga", f"No se pudo consultar el registro:\n{e}")

    def _on_registrar_clicked(self):
        id_eq = self.txt_id.text().strip()
        nombre = self.txt_nombre.text().strip()
        serie = self.txt_serie.text().strip()
        
        if not id_eq or not nombre or not serie:
            QMessageBox.warning(self, "Campos Vacíos", "Los campos marcados con (*) son estrictamente obligatorios.")
            return

        token = getattr(self.main_window, 'token', '')
        try:
            exito = self.main_window.proxy.alta_equipo(
                token, id_eq, nombre, self.cb_tipo.currentText(), # Ajustado para QComboBox
                self.txt_marca.text().strip(), self.txt_modelo.text().strip(), 
                serie, self.txt_ubicacion.text().strip(), 
                self.date_instalacion.date().toString("yyyy-MM-dd"), 
                self.cb_estado.currentText(), self.cb_criticidad.currentText()
            )
            
            if exito:
                QMessageBox.information(self, "Éxito", f"Equipo '{id_eq}' registrado satisfactoriamente.")
                self._limpiar_formulario()
                self.cargar_equipos()
                
        except ValueError as e:
            QMessageBox.warning(self, "Registro Duplicado", str(e).replace("EntidadDuplicadaError: ", ""))
        except PermissionError as e:
            QMessageBox.critical(self, "Validación Denegada", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Fallo imprevisto:\n{e}")

    def _on_modificar_clicked(self):
        id_eq = self.txt_id.text().strip()
        
        datos_actualizados = {
            "nombre": self.txt_nombre.text().strip(),
            "tipo": self.cb_tipo.currentText(), # Ajustado para QComboBox
            "marca": self.txt_marca.text().strip(),
            "modelo": self.txt_modelo.text().strip(),
            "numero_serie": self.txt_serie.text().strip(),
            "ubicacion_planta": self.txt_ubicacion.text().strip(),
            "fecha_instalacion": self.date_instalacion.date().toString("yyyy-MM-dd"),
            "estado_operativo": self.cb_estado.currentText(),
            "criticidad": self.cb_criticidad.currentText()
        }

        token = getattr(self.main_window, 'token', '')
        try:
            exito = self.main_window.proxy.modificar_equipo(token, id_eq, datos_actualizados)
            if exito:
                QMessageBox.information(self, "Éxito", f"Cambios aplicados al equipo {id_eq}.")
                self._limpiar_formulario()
                self.cargar_equipos()
        except Exception as e:
            QMessageBox.critical(self, "Error de Actualización", f"No se guardaron los cambios:\n{e}")

    def _on_eliminar_clicked(self):
        id_eq = self.txt_id.text().strip()
        
        confirmacion = QMessageBox.question(
            self, "Confirmar Eliminación", f"¿Estás seguro de eliminar permanentemente el equipo {id_eq}?\nEsta acción fallará si cuenta con órdenes asociadas.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirmacion == QMessageBox.StandardButton.Yes:
            token = getattr(self.main_window, 'token', '')
            try:
                exito = self.main_window.proxy.baja_equipo(token, id_eq)
                if exito:
                    QMessageBox.information(self, "Catálogo Actualizado", "Equipo eliminado con éxito.")
                    self._limpiar_formulario()
                    self.cargar_equipos()
            except PermissionError as e:
                QMessageBox.warning(self, "Restricción de Integridad", str(e).replace("IntegridadReferencialError: ", ""))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo completar la operación:\n{e}")

    def _limpiar_formulario(self):
        """Limpia todos los campos y regresa el contenedor a su estado inicial de registro."""
        id_rol_usuario = getattr(self.main_window, 'id_rol', None)
        if id_rol_usuario != 4:
            self.txt_id.setDisabled(False)
            self.btn_registrar.setEnabled(True)
            self.btn_modificar.setEnabled(False)
            self.btn_eliminar.setEnabled(False)
            self.grupo_formulario.setTitle("💾 Registrar Nuevo Equipo")

        self.txt_id.clear()
        self.txt_nombre.clear()
        self.cb_tipo.setCurrentIndex(0) # Ajustado para resetear el combo
        self.txt_marca.clear()
        self.txt_modelo.clear()
        self.txt_serie.clear()
        self.txt_ubicacion.clear()
        self.cb_estado.setCurrentIndex(0)
        self.cb_criticidad.setCurrentIndex(1)
        self.date_instalacion.setDate(QDate.currentDate())
        self.table.clearSelection()