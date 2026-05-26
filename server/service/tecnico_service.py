from server.dao.tecnico_dao import TecnicoDAO
from server.exceptions.exceptions import (
    EntidadDuplicadaError,
    EntidadNoEncontradaError,
    ReglaNegocioError,
    IntegridadReferencialError,
)

ESPECIALIDADES_VALIDAS   = {"Electrico", "Mecanico", "Hidraulico", "Neumatico"}
NIVELES_VALIDOS          = {"I", "II", "III"}
ESTATUS_VALIDOS          = {"Activo", "Inactivo"}


class TecnicoService:

    def __init__(self):
        self._dao = TecnicoDAO()

    def alta_tecnico(
        self,
        id_tecnico: str,
        nombre_completo: str,
        rfc: str,
        telefono: str,
        correo: str,
        especialidad: str,
        nivel_certificacion: str,
        fecha_ingreso: str,
        estatus: str,
    ) -> bool:
        if especialidad not in ESPECIALIDADES_VALIDAS:
            raise ReglaNegocioError(f"Especialidad inválida: '{especialidad}'")
        if nivel_certificacion not in NIVELES_VALIDOS:
            raise ReglaNegocioError(f"Nivel de certificación inválido: '{nivel_certificacion}'")
        if estatus not in ESTATUS_VALIDOS:
            raise ReglaNegocioError(f"Estatus inválido: '{estatus}'")

        if self._dao.buscar_por_id(id_tecnico):
            raise EntidadDuplicadaError(f"Ya existe un técnico con id '{id_tecnico}'")
        if self._dao.existe_rfc(rfc):
            raise EntidadDuplicadaError(f"Ya existe un técnico con RFC '{rfc}'")

        datos = {
            "id_tecnico":          id_tecnico,
            "nombre_completo":     nombre_completo,
            "rfc":                 rfc,
            "telefono":            telefono,
            "correo":              correo,
            "especialidad":        especialidad,
            "nivel_certificacion": nivel_certificacion,
            "fecha_ingreso":       fecha_ingreso,
            "estatus":             estatus,
        }
        return self._dao.insertar(datos)

    def consultar_tecnico(self, id_tecnico: str) -> dict:
        tecnico = self._dao.buscar_por_id(id_tecnico)
        if not tecnico:
            raise EntidadNoEncontradaError(f"Técnico '{id_tecnico}' no encontrado")
        return tecnico

    def modificar_tecnico(self, id_tecnico: str, datos_actualizados: dict) -> bool:
        if not self._dao.buscar_por_id(id_tecnico):
            raise EntidadNoEncontradaError(f"Técnico '{id_tecnico}' no encontrado")
        return self._dao.actualizar(id_tecnico, datos_actualizados)

    def baja_tecnico(self, id_tecnico: str) -> bool:
        if not self._dao.buscar_por_id(id_tecnico):
            raise EntidadNoEncontradaError(f"Técnico '{id_tecnico}' no encontrado")

        # RN-04: No se puede dar de baja a un técnico con órdenes activas
        if self._dao.tiene_ordenes_activas(id_tecnico):
            raise IntegridadReferencialError(
                f"RN-04: El técnico '{id_tecnico}' tiene órdenes activas "
                "y no puede darse de baja."
            )

        return self._dao.actualizar(id_tecnico, {"estatus": "Inactivo"})

    def listar_tecnicos(self) -> list:
        """Obtiene la lista completa de técnicos registrados sin filtros complejos."""
        return self._dao.listar_todos()