from server.dao.tecnico_dao import TecnicoDAO
from server.exceptions.exceptions import (
    EntidadDuplicadaError, EntidadNoEncontradaError,
    ReglaNegocioError, IntegridadReferencialError,
)

class TecnicoService:
    def __init__(self):
        self._dao = TecnicoDAO()

    def alta_tecnico(self, id_tecnico, nombre_completo, rfc, telefono,
                     correo, especialidad, nivel_certificacion,
                     fecha_ingreso, estatus):
        raise NotImplementedError

    def consultar_tecnico(self, id_tecnico):
        raise NotImplementedError

    def modificar_tecnico(self, id_tecnico, datos_actualizados):
        raise NotImplementedError

    def baja_tecnico(self, id_tecnico):
        raise NotImplementedError