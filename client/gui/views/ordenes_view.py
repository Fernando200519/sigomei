from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTableWidget, QTableWidgetItem, 
    QHeaderView, QMessageBox, QComboBox, QDialog
)

from client.gui.components.asignar_tecnico_dialog import AsignarTecnicoDialog
from client.gui.components.iniciar_ejecucion_dialog import IniciarEjecucionDialog
from client.gui.components.finalizar_orden_dialog import FinalizarOrdenDialog

class OrdenesView(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("Gestión de Órdenes de Mantenimiento")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)

        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filtrar por Estado:"))
        
        self.cb_filtro_estado = QComboBox()
        self.cb_filtro_estado.addItems(["Todos", "Programada", "En ejecucion", "Finalizada", "Cancelada"])
        filter_layout.addWidget(self.cb_filtro_estado)

        self.btn_refrescar = QPushButton("Buscar / Refrescar")
        self.btn_refrescar.clicked.connect(self.cargar_ordenes)
        filter_layout.addWidget(self.btn_refrescar)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID Orden", "ID Equipo", "Técnico Asignado", "Tipo", "Fecha Prog.", "Estado"
        ])
        
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

        actions_layout = QHBoxLayout()
        
        self.btn_asignar = QPushButton("Asignar Técnico")
        self.btn_asignar.clicked.connect(self._on_asignar_clicked)
        
        self.btn_iniciar = QPushButton("Iniciar Ejecución")
        self.btn_iniciar.clicked.connect(self._on_iniciar_clicked)
        
        self.btn_finalizar = QPushButton("Finalizar Orden")
        self.btn_finalizar.clicked.connect(self._on_finalizar_clicked)
        
        actions_layout.addWidget(self.btn_asignar)
        actions_layout.addWidget(self.btn_iniciar)
        actions_layout.addWidget(self.btn_finalizar)
        actions_layout.addStretch()
        
        layout.addLayout(actions_layout)
        self.setLayout(layout)

    def cargar_ordenes(self):
        """Consulta las órdenes al servidor mediante el proxy y llena la tabla."""
        try:
            estado_sel = self.cb_filtro_estado.currentText()
            filtros = {} if estado_sel == "Todos" else {"estado_orden": estado_sel}

            ordenes = self.main_window.proxy.listar_ordenes_por_filtro(filtros)

            self.table.setRowCount(0)
            for row_idx, orden in enumerate(ordenes):
                self.table.insertRow(row_idx)
                
                tecnico = orden.get("id_tecnico") or "Sin asignar"
                
                self.table.setItem(row_idx, 0, QTableWidgetItem(str(orden["id_orden"])))
                self.table.setItem(row_idx, 1, QTableWidgetItem(str(orden["id_equipo"])))
                self.table.setItem(row_idx, 2, QTableWidgetItem(str(tecnico)))
                self.table.setItem(row_idx, 3, QTableWidgetItem(str(orden["tipo_mantenimiento"])))
                self.table.setItem(row_idx, 4, QTableWidgetItem(str(orden["fecha_programada"])))
                self.table.setItem(row_idx, 5, QTableWidgetItem(str(orden["estado_orden"])))
                
        except Exception as e:
            QMessageBox.critical(self, "Error de Datos", f"No se pudieron cargar las órdenes:\n{e}")

    def _get_selected_orden_id(self) -> str | None:
        """Método auxiliar helper para recuperar el ID seleccionado de la tabla."""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Advertencia", "Por favor, selecciona una orden de la tabla.")
            return None
        row = selected_rows[0].row()
        return self.table.item(row, 0).text()

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

    def _on_finalizar_clicked(self):
        id_orden = self._get_selected_orden_id()
        if not id_orden: return

        dialogo = FinalizarOrdenDialog(id_orden, self.main_window)
        if dialogo.exec() == QDialog.DialogCode.Accepted:
            self.cargar_ordenes()