from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTableWidget, QTableWidgetItem, 
    QHeaderView, QMessageBox, QComboBox, QDialog, QGroupBox, QTextEdit
)
from PyQt6.QtCore import Qt

from client.gui.components.asignar_tecnico_dialog import AsignarTecnicoDialog
from client.gui.components.iniciar_ejecucion_dialog import IniciarEjecucionDialog
from client.gui.components.finalizar_orden_dialog import FinalizarOrdenDialog
from client.gui.components.crear_orden_dialog import CrearOrdenDialog

class OrdenesView(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # ================= PANEL IZQUIERDO: TABLA Y FILTRADO =================
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)

        grupo_tabla = QGroupBox("Órdenes de Mantenimiento Registradas")
        grupo_tabla.setStyleSheet("QGroupBox { font-size: 14px; font-weight: bold; color: #1565C0; }")
        tabla_layout = QVBoxLayout(grupo_tabla)

        # Barra de Filtros
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filtrar por Estado:"))
        
        self.cb_filtro_estado = QComboBox()
        self.cb_filtro_estado.addItems(["Todos", "Programada", "En ejecucion", "Pendiente de cierre", "Finalizada", "Cancelada"])
        filter_layout.addWidget(self.cb_filtro_estado)

        self.btn_refrescar = QPushButton("🔍 Buscar / Refrescar")
        self.btn_refrescar.clicked.connect(self.cargar_ordenes)
        filter_layout.addWidget(self.btn_refrescar)
        
        # NUEVO BOTÓN AGREGADO A LA BARRA DE HERRAMIENTAS
        self.btn_nueva_orden = QPushButton("➕ Crear Nueva Orden")
        self.btn_nueva_orden.setStyleSheet("background-color: #1565C0; color: white; font-weight: bold;")
        self.btn_nueva_orden.clicked.connect(self._on_nueva_orden_clicked)
        filter_layout.addWidget(self.btn_nueva_orden)
        
        filter_layout.addStretch()
        tabla_layout.addLayout(filter_layout)

        # Tabla Principal
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID Orden", "ID Equipo", "Técnico Asignado", "Tipo", "Fecha Prog.", "Estado"
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
        
        left_layout.addWidget(grupo_tabla)

        # ================= PANEL DERECHO: DETALLES Y ACCIONES DE ESTADO =================
        self.grupo_operaciones = QGroupBox("📋 Detalles de Orden Seleccionada")
        self.grupo_operaciones.setFixedWidth(360)
        self.grupo_operaciones.setStyleSheet("""
            QGroupBox { font-size: 14px; font-weight: bold; color: #1565C0; border: 1px solid #B0BEC5; border-radius: 6px; margin-top: 12px; }
            QGroupBox::title { subcontrol-origin: margin; left: 8px; padding: 0 3px; }
        """)
        right_layout = QVBoxLayout(self.grupo_operaciones)
        right_layout.setContentsMargins(12, 18, 12, 12)

        right_layout.addWidget(QLabel("<b>Descripción del Trabajo:</b>"))
        self.txt_detalle_desc = QTextEdit()
        self.txt_detalle_desc.setReadOnly(True)
        self.txt_detalle_desc.setStyleSheet("background-color: #FAFAFA; border: 1px solid #CFD8DC; border-radius: 4px;")
        self.txt_detalle_desc.setMaximumHeight(100)
        right_layout.addWidget(self.txt_detalle_desc)

        self.lbl_costo_est = QLabel("Costo Estimado: $0.00")
        self.lbl_costo_est.setStyleSheet("font-size: 12px; color: #37474F;")
        right_layout.addWidget(self.lbl_costo_est)

        self.lbl_costo_real = QLabel("Costo Real: --")
        self.lbl_costo_real.setStyleSheet("font-size: 12px; font-weight: bold; color: #2E7D32;")
        right_layout.addWidget(self.lbl_costo_real)

        right_layout.addSpacing(10)
        right_layout.addWidget(QLabel("<b>Flujo de Trabajo y Estados:</b>"))

        # BOTONES DE OPERACIÓN
        self.btn_asignar = QPushButton("👤 Asignar Técnico")
        self.btn_asignar.clicked.connect(self._on_asignar_clicked)
        self.btn_asignar.setStyleSheet("background-color: #1565C0; color: white; font-weight: bold; padding: 6px; border-radius: 4px;")
        right_layout.addWidget(self.btn_asignar)

        self.btn_iniciar = QPushButton("🚀 Iniciar Ejecución")
        self.btn_iniciar.clicked.connect(self._on_iniciar_clicked)
        self.btn_iniciar.setStyleSheet("background-color: #00838F; color: white; font-weight: bold; padding: 6px; border-radius: 4px;")
        right_layout.addWidget(self.btn_iniciar)

        self.btn_finalizar = QPushButton("🔒 Finalizar Orden")
        self.btn_finalizar.clicked.connect(self._on_finalizar_or_solicitar_clicked)
        self.btn_finalizar.setStyleSheet("background-color: #2E7D32; color: white; font-weight: bold; padding: 6px; border-radius: 4px;")
        right_layout.addWidget(self.btn_finalizar)

        self.btn_cancelar = QPushButton("🚫 Cancelar Orden")
        self.btn_cancelar.clicked.connect(self._on_cancelar_clicked)
        self.btn_cancelar.setStyleSheet("background-color: #C62828; color: white; font-weight: bold; padding: 6px; border-radius: 4px;")
        right_layout.addWidget(self.btn_cancelar)

        right_layout.addStretch()

        main_layout.addWidget(left_container, stretch=3)
        main_layout.addWidget(self.grupo_operaciones, stretch=1)
        self.setLayout(main_layout)

    def verificar_permisos_ui(self):
        """Modifica los botones visibles y el flujo según las restricciones de rol del usuario."""
        id_rol_usuario = getattr(self.main_window, 'id_rol', None)
        
        if id_rol_usuario == 4:
            self.btn_asignar.hide()
            self.btn_cancelar.hide()
            self.btn_nueva_orden.hide() # Ocultar botón de alta a los técnicos
            
            self.btn_finalizar.setText("📩 Solicitar Cierre (RF-09)")
            self.btn_finalizar.setStyleSheet("background-color: #E65100; color: white; font-weight: bold; padding: 6px; border-radius: 4px;")
        else:
            self.btn_asignar.show()
            self.btn_cancelar.show()
            self.btn_nueva_orden.show() # Mostrar a Admin, Coordinador y Supervisor
            self.btn_finalizar.setText("🔒 Finalizar Orden (Cierre)")
            self.btn_finalizar.setStyleSheet("background-color: #2E7D32; color: white; font-weight: bold; padding: 6px; border-radius: 4px;")

    def cargar_ordenes(self):
        try:
            token = getattr(self.main_window, 'token', '')
            estado_sel = self.cb_filtro_estado.currentText()
            filtros = {} if estado_sel == "Todos" else {"estado_orden": estado_sel}

            ordenes = self.main_window.proxy.listar_ordenes_por_filtro(token, filtros)

            self.table.setRowCount(0)
            for row_idx, orden in enumerate(ordenes):
                self.table.insertRow(row_idx)
                tecnico = orden.get("id_tecnico") or "Sin asignar"
                
                self.table.setItem(row_idx, 0, QTableWidgetItem(str(orden.get("id_orden", ""))))
                self.table.setItem(row_idx, 1, QTableWidgetItem(str(orden.get("id_equipo", ""))))
                self.table.setItem(row_idx, 2, QTableWidgetItem(str(tecnico)))
                self.table.setItem(row_idx, 3, QTableWidgetItem(str(orden.get("tipo_mantenimiento", ""))))
                self.table.setItem(row_idx, 4, QTableWidgetItem(str(orden.get("fecha_programada", ""))))
                self.table.setItem(row_idx, 5, QTableWidgetItem(str(orden.get("estado_orden", ""))))
                
            self._limpiar_detalles()
        except Exception as e:
            QMessageBox.critical(self, "Error de Datos", f"No se pudieron cargar las órdenes de forma remota:\n{e}")

    def _get_selected_orden_id(self) -> str | None:
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Advertencia", "Por favor, selecciona una orden de la tabla.")
            return None
        row = selected_rows[0].row()
        return self.table.item(row, 0).text()

    def _on_fila_seleccionada(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows: return
        
        row = selected_rows[0].row()
        id_orden = self.table.item(row, 0).text()

        try:
            token = getattr(self.main_window, 'token', '')
            orden_detalles = self.main_window.proxy.consultar_orden(token, id_orden)
            
            if orden_detalles:
                self.grupo_operaciones.setTitle(f"📋 Orden: {id_orden}")
                self.txt_detalle_desc.setText(str(orden_detalles.get("descripcion_trabajo", "Sin descripción.")))
                
                try:
                    costo_est = float(orden_detalles.get("costo_estimado") or 0.00)
                    self.lbl_costo_est.setText(f"Costo Estimado: ${costo_est:,.2f}")
                except (ValueError, TypeError):
                    self.lbl_costo_est.setText("Costo Estimado: $0.00")
                
                costo_real = orden_detalles.get("costo_real")
                if costo_real is not None and costo_real != "":
                    try:
                        costo_real_val = float(costo_real)
                        self.lbl_costo_real.setText(f"Costo Real: ${costo_real_val:,.2f}")
                    except (ValueError, TypeError):
                        self.lbl_costo_real.setText("Costo Real: Pendiente de cierre")
                else:
                    self.lbl_costo_real.setText("Costo Real: Pendiente de cierre")
        except Exception as e:
            QMessageBox.critical(self, "Error de Detalle", f"No se pudo consultar el desglose de la orden:\n{e}")

    # ACCIÓN DEL NUEVO BOTÓN
    def _on_nueva_orden_clicked(self):
        dialogo = CrearOrdenDialog(self.main_window)
        if dialogo.exec() == QDialog.DialogCode.Accepted:
            self.cargar_ordenes()

    def _on_asignar_clicked(self):
        id_orden = self._get_selected_orden_id()
        if not id_orden: return
            
        dialogo = AsignarTecnicoDialog(id_orden, self.main_window)
        if dialogo.exec() == QDialog.DialogCode.Accepted:
            self.cargar_ordenes()
    
    def _on_iniciar_clicked(self):
        id_orden = self._get_selected_orden_id()
        if not id_orden: return

        dialogo = IniciarEjecucionDialog(id_orden, self.main_window)
        if dialogo.exec() == QDialog.DialogCode.Accepted:
            self.cargar_ordenes()

    def _on_finalizar_or_solicitar_clicked(self):
        id_orden = self._get_selected_orden_id()
        if not id_orden: return

        id_rol_usuario = getattr(self.main_window, 'id_rol', None)
        token = getattr(self.main_window, 'token', '')

        if id_rol_usuario == 4:
            confirmacion = QMessageBox.question(
                self, "Solicitar Cierre", 
                f"¿Deseas enviar la solicitud de cierre para la orden {id_orden} a revisión?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if confirmacion == QMessageBox.StandardButton.Yes:
                try:
                    exito = self.main_window.proxy.solicitar_cierre(token, id_orden)
                    if exito:
                        QMessageBox.information(self, "Enviado", "Solicitud de cierre registrada con éxito.")
                        self.cargar_ordenes()
                except PermissionError as e:
                    QMessageBox.warning(self, "Validación Denegada", str(e))
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"No se pudo procesar la solicitud:\n{e}")
        else:
            dialogo = FinalizarOrdenDialog(id_orden, self.main_window)
            if dialogo.exec() == QDialog.DialogCode.Accepted:
                self.cargar_ordenes()

    def _on_cancelar_clicked(self):
        id_orden = self._get_selected_orden_id()
        if not id_orden: return

        confirmacion = QMessageBox.question(
            self, "Confirmar Cancelación", f"¿Estás seguro de cancelar definitivamente la orden {id_orden}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirmacion == QMessageBox.StandardButton.Yes:
            token = getattr(self.main_window, 'token', '')
            try:
                exito = self.main_window.proxy.cancelar_orden(token, id_orden)
                if exito:
                    QMessageBox.information(self, "Cancelada", f"La orden {id_orden} ha sido cancelada.")
                    self.cargar_ordenes()
            except PermissionError as e:
                QMessageBox.warning(self, "Estado Inválido", str(e).replace("EstadoInvalidoError: ", ""))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo cancelar la orden:\n{e}")

    def _limpiar_detalles(self):
        self.grupo_operaciones.setTitle("📋 Detalles de Orden Seleccionada")
        self.txt_detalle_desc.clear()
        self.lbl_costo_est.setText("Costo Estimado: $0.00")
        self.lbl_costo_real.setText("Costo Real: --")
        self.table.clearSelection()