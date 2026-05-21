from server.dao.equipo_dao import EquipoDAO
from server.exceptions.exceptions import (
    EntidadDuplicadaError, EntidadNoEncontradaError,
    ReglaNegocioError, IntegridadReferencialError,
)

class EquipoService:
    def __init__(self):
        self._dao = EquipoDAO()

    def alta_equipo(self, id_equipo, nombre, tipo, marca, modelo,
                    numero_serie, ubicacion_planta, fecha_instalacion,
                    estado_operativo, criticidad):
        raise NotImplementedError

    def consultar_equipo(self, id_equipo):
        raise NotImplementedError

    def modificar_equipo(self, id_equipo, datos_actualizados):
        raise NotImplementedError

    def baja_equipo(self, id_equipo):
        raise NotImplementedError