from server.dao.equipo_dao import EquipoDAO
from server.exceptions.exceptions import (
    EntidadDuplicadaError,
    EntidadNoEncontradaError,
    ReglaNegocioError,
    IntegridadReferencialError,
)
from psycopg2.errors import UniqueViolation, CheckViolation


TIPOS_VALIDOS       = {"Electrico", "Mecanico", "Hidraulico", "Neumatico"}
CRITICIDADES_VALIDAS = {"Alta", "Media", "Baja"}
ESTADOS_VALIDOS     = {"Operativo", "En Mantenimiento", "Fuera de Servicio"}


class EquipoService:

    def __init__(self):
        self._dao = EquipoDAO()

    def alta_equipo(
        self,
        id_equipo: str,
        nombre: str,
        tipo: str,
        marca: str,
        modelo: str,
        numero_serie: str,
        ubicacion_planta: str,
        fecha_instalacion: str,
        estado_operativo: str,
        criticidad: str,
    ) -> bool:
        if tipo not in TIPOS_VALIDOS:
            raise ReglaNegocioError(f"Tipo de equipo inválido: '{tipo}'")
        if criticidad not in CRITICIDADES_VALIDAS:
            raise ReglaNegocioError(f"Criticidad inválida: '{criticidad}'")
        if estado_operativo not in ESTADOS_VALIDOS:
            raise ReglaNegocioError(f"Estado operativo inválido: '{estado_operativo}'")

        if self._dao.buscar_por_id(id_equipo):
            raise EntidadDuplicadaError(f"Ya existe un equipo con id '{id_equipo}'")

        if self._dao.buscar_por_numero_serie(numero_serie):
            raise EntidadDuplicadaError(f"Ya existe un equipo con número de serie '{numero_serie}'")

        datos = {
            "id_equipo":         id_equipo,
            "nombre":            nombre,
            "tipo":              tipo,
            "marca":             marca,
            "modelo":            modelo,
            "numero_serie":      numero_serie,
            "ubicacion_planta":  ubicacion_planta,
            "fecha_instalacion": fecha_instalacion,
            "estado_operativo":  estado_operativo,
            "criticidad":        criticidad,
        }

        return self._dao.insertar(datos)
        
    def consultar_equipo(self, id_equipo: str) -> dict:
        equipo = self._dao.buscar_por_id(id_equipo)
        if not equipo:
            raise EntidadNoEncontradaError(f"Equipo '{id_equipo}' no encontrado")
        return equipo

    def modificar_equipo(self, id_equipo: str, datos_actualizados: dict) -> bool:
        if not self._dao.buscar_por_id(id_equipo):
            raise EntidadNoEncontradaError(f"Equipo '{id_equipo}' no encontrado")

        if "tipo" in datos_actualizados and datos_actualizados["tipo"] not in TIPOS_VALIDOS:
            raise ReglaNegocioError(f"Tipo de equipo inválido: '{datos_actualizados['tipo']}'")
        if "criticidad" in datos_actualizados and datos_actualizados["criticidad"] not in CRITICIDADES_VALIDAS:
            raise ReglaNegocioError(f"Criticidad inválida: '{datos_actualizados['criticidad']}'")

        return self._dao.actualizar(id_equipo, datos_actualizados)

    def baja_equipo(self, id_equipo: str) -> bool:
        if not self._dao.buscar_por_id(id_equipo):
            raise EntidadNoEncontradaError(f"Equipo '{id_equipo}' no encontrado")

        # RN-04: No se puede eliminar un equipo que tiene órdenes de mantenimiento
        if self._dao.tiene_ordenes_vinculadas(id_equipo):
            raise IntegridadReferencialError(
                f"RN-04: El equipo '{id_equipo}' tiene órdenes de mantenimiento "
                "vinculadas y no puede eliminarse."
            )

        return self._dao.eliminar(id_equipo)