from server.dao.tecnico_dao import TecnicoDAO
from server.dao.usuario_dao import UsuarioDAO
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

    ID_ROL_TECNICO = 4
    
    def __init__(self):
        self._dao = TecnicoDAO()
        self._usuario_dao = UsuarioDAO()

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
            raise ReglaNegocioError(f"Estado inválido: '{estatus}'")

        if self._usuario_dao.obtener_id_usuario_int(id_tecnico):
            raise EntidadDuplicadaError(f"Ya existe un técnico con id '{id_tecnico}'")
        

        if self._dao.existe_rfc(rfc):
            raise EntidadDuplicadaError(f"Ya existe un usuario con RFC '{rfc}'")
        
        datos_usuario = {
            "id_usuario": id_tecnico,
            "nombre_completo": nombre_completo,
            "rfc": rfc,
            "telefono": telefono,
            "correo": correo,
            "estado": estatus,
            "hash_contrasena": "temporal123",
            "id_rol": self.ID_ROL_TECNICO,
        }

        id_usuario = self._usuario_dao.insertar(datos_usuario)

        datos_tecnico = {
            "id_tecnico_int": id_usuario,
            "id_tecnico": id_tecnico,
            "especialidad": especialidad,
            "nivel_certificacion": nivel_certificacion,
            "fecha_ingreso": fecha_ingreso,
        }

        return self._dao.insertar(datos_tecnico)
            
    def consultar_tecnico(self, id_tecnico: str) -> dict:
        id_tecnico_int = self._usuario_dao.obtener_id_usuario_int(id_tecnico)
        if not id_tecnico_int:
            raise EntidadNoEncontradaError(f"Técnico '{id_tecnico}' no encontrado")
            
        tecnico = self._dao.buscar_por_id(id_tecnico_int)
        if not tecnico:
            raise EntidadNoEncontradaError(f"Técnico '{id_tecnico}' no encontrado")
        return tecnico

    def modificar_tecnico(self, id_tecnico: str, datos_actualizados: dict) -> bool:
        id_tecnico_int = self._usuario_dao.obtener_id_usuario_int(id_tecnico)
        if not id_tecnico_int or not self._dao.buscar_por_id(id_tecnico_int):
            raise EntidadNoEncontradaError(f"Técnico '{id_tecnico}' no encontrado")
            
        return self._dao.actualizar(id_tecnico_int, datos_actualizados)

    def baja_tecnico(self, id_tecnico: str) -> bool:
        id_tecnico_int = self._usuario_dao.obtener_id_usuario_int(id_tecnico)
        if not id_tecnico_int or not self._dao.buscar_por_id(id_tecnico_int):
            raise EntidadNoEncontradaError(f"Técnico '{id_tecnico}' no encontrado")

        if self._dao.tiene_ordenes_activas(id_tecnico_int):
            raise IntegridadReferencialError(
                f"RN-04: El técnico '{id_tecnico}' tiene órdenes activas y no puede darse de baja."
            )

        return self._dao.actualizar(id_tecnico_int, {"estatus": "Inactivo"})

    def listar_tecnicos(self) -> list:
        """Obtiene la lista completa de técnicos registrados sin filtros complejos."""
        return self._dao.listar_todos()
    
    def listar_tecnicos_por_filtro(self, filtros: dict) -> list:
        return self._dao.listar_tecnicos_por_filtro(filtros)