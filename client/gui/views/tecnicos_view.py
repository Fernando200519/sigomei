from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, 
    QLineEdit, QComboBox, QDateEdit, QPushButton, QTableWidget, 
    QTableWidgetItem, QHeaderView, QMessageBox, QGroupBox
)
from PyQt6.QtCore import QDate, Qt

class TecnicosView(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # ================= PANEL IZQUIERDO: TABLA Y FILTROS =================
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)

        grupo_lista = QGroupBox("Catálogo de Personal Técnico")
        grupo_lista.setStyleSheet("QGroupBox { font-size: 14px; font-weight: bold; color: #1565C0; }")
        lista_layout = QVBoxLayout(grupo_lista)

        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Especialidad:"))
        self.cb_filtro_esp = QComboBox()
        self.cb_filtro_esp.addItems(["Todas", "Electrico", "Mecanico", "Hidraulico", "Neumatico"])
        filter_layout.addWidget(self.cb_filtro_esp)

        filter_layout.addWidget(QLabel("Estatus:"))
        self.cb_filtro_est = QComboBox()
        self.cb_filtro_est.addItems(["Todos", "Activo", "Inactivo", "Suspendido"])
        filter_layout.addWidget(self.cb_filtro_est)

        self.btn_filtrar = QPushButton("🔍 Filtrar Personal")
        self.btn_filtrar.clicked.connect(self.cargar_tecnicos)
        filter_layout.addWidget(self.btn_filtrar)
        lista_layout.addLayout(filter_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "ID Técnico", "Nombre Completo", "Especialidad", "Certificación", "Estatus"
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
        lista_layout.addWidget(self.table)
        
        left_layout.addWidget(grupo_lista)

        # ================= PANEL DERECHO: FORMULARIO CRUD =================
        self.grupo_formulario = QGroupBox("💾 Registrar Nuevo Técnico")
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

        estilo_inputs = "QLineEdit, QComboBox, QDateEdit { padding: 4px; border: 1px solid #CFD8DC; border-radius: 4px; }"

        self.txt_id = QLineEdit()
        self.txt_id.setPlaceholderText("Ej. TEC-003")
        self.txt_id.setStyleSheet(estilo_inputs)

        self.txt_nombre = QLineEdit()
        self.txt_nombre.setPlaceholderText("Ej. Juan Pérez Gómez")
        self.txt_nombre.setStyleSheet(estilo_inputs)

        self.txt_rfc = QLineEdit()
        self.txt_rfc.setPlaceholderText("13 caracteres")
        self.txt_rfc.setStyleSheet(estilo_inputs)

        self.txt_telefono = QLineEdit()
        self.txt_telefono.setPlaceholderText("Ej. 9211234567")
        self.txt_telefono.setStyleSheet(estilo_inputs)

        self.txt_correo = QLineEdit()
        self.txt_correo.setPlaceholderText("Ej. juan.perez@empresa.mx")
        self.txt_correo.setStyleSheet(estilo_inputs)

        self.cb_especialidad = QComboBox()
        self.cb_especialidad.addItems(["Electrico", "Mecanico", "Hidraulico", "Neumatico"])
        self.cb_especialidad.setStyleSheet(estilo_inputs)

        # CORRECCIÓN UX: Cambiado de QLineEdit a QComboBox con los tokens estrictos del contrato (I, II, III)
        self.cb_certificacion = QComboBox()
        self.cb_certificacion.addItems(["I", "II", "III"])
        self.cb_certificacion.setStyleSheet(estilo_inputs)

        self.date_ingreso = QDateEdit()
        self.date_ingreso.setCalendarPopup(True)
        self.date_ingreso.setDate(QDate.currentDate())
        self.date_ingreso.setStyleSheet(estilo_inputs)

        self.cb_estatus = QComboBox()
        self.cb_estatus.addItems(["Activo", "Inactivo", "Suspendido"])
        self.cb_estatus.setStyleSheet(estilo_inputs)

        form_layout.addRow("ID Técnico *:", self.txt_id)
        form_layout.addRow("Nombre Completo *:", self.txt_nombre)
        form_layout.addRow("RFC *:", self.txt_rfc)
        form_layout.addRow("Teléfono:", self.txt_telefono)
        form_layout.addRow("Correo *:", self.txt_correo)
        form_layout.addRow("Especialidad *:", self.cb_especialidad)
        form_layout.addRow("Certificación *:", self.cb_certificacion) # Cambiado a cb_certificacion
        form_layout.addRow("Fecha Ingreso *:", self.date_ingreso)
        form_layout.addRow("Estatus *:", self.cb_estatus)

        right_layout.addLayout(form_layout)
        right_layout.addSpacing(10)

        self.btn_registrar = QPushButton("💾 Guardar Nuevo Técnico")
        self.btn_registrar.clicked.connect(self._on_registrar_clicked)
        self.btn_registrar.setStyleSheet("background-color: #1565C0; color: white; font-weight: bold; padding: 7px; border-radius: 4px;")
        right_layout.addWidget(self.btn_registrar)

        self.btn_modificar = QPushButton("✏️ Actualizar Cambios")
        self.btn_modificar.clicked.connect(self._on_modificar_clicked)
        self.btn_modificar.setStyleSheet("background-color: #2E7D32; color: white; font-weight: bold; padding: 7px; border-radius: 4px;")
        self.btn_modificar.setEnabled(False)
        right_layout.addWidget(self.btn_modificar)

        self.btn_eliminar = QPushButton("❌ Eliminar del Registro")
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
            self.txt_rfc.setDisabled(True)
            self.txt_telefono.setDisabled(True)
            self.txt_correo.setDisabled(True)
            self.cb_especialidad.setDisabled(True)
            self.cb_certificacion.setDisabled(True) # Ajustado
            self.date_ingreso.setDisabled(True)
            self.cb_estatus.setDisabled(True)
            
            self.btn_registrar.hide()
            self.btn_modificar.hide()
            self.btn_eliminar.hide()
            self.btn_limpiar.hide()
            
            self.lbl_permiso_aviso.setText("⚠️ Modo Lectura: No cuentas con privilegios de supervisión sobre este catálogo.")
            self.grupo_formulario.setTitle("🔍 Ficha del Técnico Seleccionado")
        else:
            self.txt_id.setDisabled(False)
            self.btn_registrar.show()
            self.btn_modificar.show()
            self.btn_eliminar.show()
            self.btn_limpiar.show()
            self.lbl_permiso_aviso.setText("")
            self.grupo_formulario.setTitle("💾 Registrar Nuevo Técnico")

    def cargar_tecnicos(self):
        try:
            token = getattr(self.main_window, 'token', '')
            filtros = {}
            if self.cb_filtro_esp.currentText() != "Todas":
                filtros["especialidad"] = self.cb_filtro_esp.currentText()
            if self.cb_filtro_est.currentText() != "Todos":
                filtros["estatus"] = self.cb_filtro_est.currentText()

            tecnicos = self.main_window.proxy.listar_tecnicos_por_filtro(token, filtros)

            self.table.setRowCount(0)
            for row_idx, tec in enumerate(tecnicos):
                self.table.insertRow(row_idx)
                self.table.setItem(row_idx, 0, QTableWidgetItem(str(tec.get("id_tecnico", ""))))
                self.table.setItem(row_idx, 1, QTableWidgetItem(str(tec.get("nombre_completo", ""))))
                self.table.setItem(row_idx, 2, QTableWidgetItem(str(tec.get("especialidad", ""))))
                self.table.setItem(row_idx, 3, QTableWidgetItem(str(tec.get("nivel_certificacion", ""))))
                self.table.setItem(row_idx, 4, QTableWidgetItem(str(tec.get("estatus", ""))))
        except Exception as e:
            QMessageBox.critical(self, "Error de Red", f"No se pudo sincronizar el listado de personal:\n{e}")

    def _on_fila_seleccionada(self):
        filas_seleccionadas = self.table.selectionModel().selectedRows()
        if not filas_seleccionadas:
            return

        fila = filas_seleccionadas[0].row()
        item_id = self.table.item(fila, 0)
        if not item_id: return
        
        id_tecnico = item_id.text()

        try:
            token = getattr(self.main_window, 'token', '')
            tec_detalles = self.main_window.proxy.consultar_tecnico(token, id_tecnico)
            
            if tec_detalles:
                self.txt_id.setText(str(tec_detalles.get("id_tecnico", "")))
                self.txt_id.setDisabled(True)
                self.txt_nombre.setText(str(tec_detalles.get("nombre_completo", "")))
                self.txt_rfc.setText(str(tec_detalles.get("rfc", "")))
                self.txt_telefono.setText(str(tec_detalles.get("telefono", "")))
                self.txt_correo.setText(str(tec_detalles.get("correo", "")))
                self.cb_certificacion.setCurrentText(str(tec_detalles.get("nivel_certificacion", "I"))) # Ajustado para QComboBox
                
                self.cb_especialidad.setCurrentText(str(tec_detalles.get("especialidad", "Mecanico")))
                self.cb_estatus.setCurrentText(str(tec_detalles.get("estatus", "Activo")))
                
                fecha_str = tec_detalles.get("fecha_ingreso")
                if fecha_str:
                    self.date_ingreso.setDate(QDate.fromString(str(fecha_str), "yyyy-MM-dd"))

                id_rol_usuario = getattr(self.main_window, 'id_rol', None)
                if id_rol_usuario != 4:
                    self.grupo_formulario.setTitle(f"✏️ Editando Técnico: {id_tecnico}")
                    self.btn_registrar.setEnabled(False)
                    self.btn_modificar.setEnabled(True)
                    self.btn_eliminar.setEnabled(True)
        except Exception as e:
            QMessageBox.critical(self, "Error de Datos", f"Fallo al mapear información del técnico:\n{e}")

    def _on_registrar_clicked(self):
        id_tec = self.txt_id.text().strip()
        nombre = self.txt_nombre.text().strip()
        rfc = self.txt_rfc.text().strip()
        correo = self.txt_correo.text().strip()

        if not id_tec or not nombre or not rfc or not correo:
            QMessageBox.warning(self, "Campos Vacíos", "Los campos marcados con (*) son estrictamente obligatorios.")
            return

        token = getattr(self.main_window, 'token', '')
        try:
            exito = self.main_window.proxy.alta_tecnico(
                token, id_tec, nombre, rfc, self.txt_telefono.text().strip(), correo,
                self.cb_especialidad.currentText(), self.cb_certificacion.currentText(), # Ajustado para QComboBox
                self.date_ingreso.date().toString("yyyy-MM-dd"), self.cb_estatus.currentText()
            )
            if exito:
                QMessageBox.information(self, "Éxito", f"Técnico '{id_tec}' dado de alta de forma correcta.")
                self._limpiar_formulario()
                self.cargar_tecnicos()
        except ValueError as e:
            QMessageBox.warning(self, "Registro Duplicado", str(e).replace("EntidadDuplicadaError: ", ""))
        except Exception as e:
            QMessageBox.critical(self, "Error de Servidor", f"No se pudo completar el registro:\n{e}")

    def _on_modificar_clicked(self):
        id_tec = self.txt_id.text().strip()
        
        datos_actualizados = {
            "nombre_completo": self.txt_nombre.text().strip(),
            "rfc": self.txt_rfc.text().strip(),
            "telefono": self.txt_telefono.text().strip(),
            "correo": self.txt_correo.text().strip(),
            "especialidad": self.cb_especialidad.currentText(),
            "nivel_certificacion": self.cb_certificacion.currentText(), # Ajustado para QComboBox
            "fecha_ingreso": self.date_ingreso.date().toString("yyyy-MM-dd"),
            "estatus": self.cb_estatus.currentText()
        }

        token = getattr(self.main_window, 'token', '')
        try:
            exito = self.main_window.proxy.modificar_tecnico(token, id_tec, datos_actualizados)
            if exito:
                QMessageBox.information(self, "Éxito", f"Ficha del técnico {id_tec} actualizada satisfactoriamente.")
                self._limpiar_formulario()
                self.cargar_tecnicos()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se guardaron los cambios:\n{e}")

    def _on_eliminar_clicked(self):
        """Envía la solicitud de baja física o lógica al backend y limpia la UI."""
        id_tec = self.txt_id.text().strip()
        
        confirmacion = QMessageBox.question(
            self, "Confirmar Operación", 
            f"¿Deseas remover al técnico {id_tec} del sistema?\nEsta operación fallará si cuenta con historial de órdenes.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirmacion == QMessageBox.StandardButton.Yes:
            token = getattr(self.main_window, 'token', '')
            try:
                # 1. Ejecutar el borrado en el servidor remoto
                exito = self.main_window.proxy.baja_tecnico(token, id_tec)
                if exito:
                    QMessageBox.information(self, "Catálogo Actualizado", f"Registro del técnico {id_tec} removido con éxito.")
                    
                    # 2. CORRECCIÓN CRÍTICA: Forzar el reseteo completo de los campos e índices de la tabla PyQt6
                    self.table.clearSelection()
                    self._limpiar_formulario()
                    
                    # 3. Volver a consultar al servidor para repoblar la grilla sin el elemento eliminado
                    self.cargar_tecnicos()
            except PermissionError as e:
                QMessageBox.warning(self, "Restricción de Regla", str(e).replace("IntegridadReferencialError: ", ""))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo completar la baja:\n{e}")

    def _limpiar_formulario(self):
        id_rol_usuario = getattr(self.main_window, 'id_rol', None)
        if id_rol_usuario != 4:
            self.txt_id.setDisabled(False)
            self.btn_registrar.setEnabled(True)
            self.btn_modificar.setEnabled(False)
            self.btn_eliminar.setEnabled(False)
            self.grupo_formulario.setTitle("💾 Registrar Nuevo Técnico")

        self.txt_id.clear()
        self.txt_nombre.clear()
        self.txt_rfc.clear()
        self.txt_telefono.clear()
        self.txt_correo.clear()
        self.cb_certificacion.setCurrentIndex(0) # Ajustado para resetear el combo
        self.cb_especialidad.setCurrentIndex(0)
        self.cb_estatus.setCurrentIndex(0)
        self.date_ingreso.setDate(QDate.currentDate())
        self.table.clearSelection()