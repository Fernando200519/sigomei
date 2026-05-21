from server.dao.orden_dao import OrdenDAO
from server.dao.equipo_dao import EquipoDAO
from server.dao.tecnico_dao import TecnicoDAO
from server.exceptions.exceptions import (
    EntidadDuplicadaError, EntidadNoEncontradaError,
    ReglaNegocioError, EstadoInvalidoError,
)

class OrdenService:
    def __init__(self):
        self._dao = OrdenDAO()
        self._equipo_dao = EquipoDAO()
        self._tecnico_dao = TecnicoDAO()

    def crear_orden(self, id_orden, id_equipo, tipo_mantenimiento,
                    fecha_programada, descripcion_trabajo, costo_estimado):
        raise NotImplementedError

    def consultar_orden(self, id_orden):
        raise NotImplementedError

    def asignar_tecnico(self, id_orden, id_tecnico):
        raise NotImplementedError

    def iniciar_ejecucion(self, id_orden, fecha_inicio):
        raise NotImplementedError

    def finalizar_orden(self, id_orden, fecha_cierre, costo_real):
        raise NotImplementedError

    def cancelar_orden(self, id_orden):
        raise NotImplementedError

    def listar_ordenes_por_filtro(self, filtros):
        raise NotImplementedError