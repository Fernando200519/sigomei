import unicodedata
from datetime import date

from server.dao.orden_dao import OrdenDAO
from server.dao.equipo_dao import EquipoDAO
from server.dao.tecnico_dao import TecnicoDAO
from server.exceptions.exceptions import (
    EntidadDuplicadaError,
    EntidadNoEncontradaError,
    ReglaNegocioError,
    EstadoInvalidoError,
)

NIVEL_NUM: dict[str, int] = {"I": 1, "II": 2, "III": 3}

TRANSICIONES_VALIDAS: dict[str, list[str]] = {
    "Programada":          ["En ejecucion", "Cancelada"],
    "En ejecucion":        ["Finalizada",   "Cancelada"],
    "Pendiente de cierre": ["Finalizada",   "Cancelada"],
    "Finalizada":          [],
    "Cancelada":           [],
}

ESTADOS_ACTIVOS = {"Programada", "En ejecucion"}


def _nfc(texto: str) -> str:
    return unicodedata.normalize("NFC", texto)


class OrdenService:

    def __init__(self):
        self._dao         = OrdenDAO()
        self._equipo_dao  = EquipoDAO()
        self._tecnico_dao = TecnicoDAO()

    def crear_orden(self, id_orden, id_equipo, tipo_mantenimiento,
                    fecha_programada, descripcion_trabajo, costo_estimado):
        id_equipo_int = self._equipo_dao.obtener_id_equipo_int(id_equipo)
        if not id_equipo_int:
            raise EntidadNoEncontradaError(f"Equipo '{id_equipo}' no encontrado")
        
        if costo_estimado < 0:
            raise ReglaNegocioError("El costo estimado no puede ser negativo")

        if isinstance(fecha_programada, str):
            fecha_programada = date.fromisoformat(fecha_programada)

        # RN-02: Se pasa el ID entero para realizar el filtrado correcto en el DAO
        ordenes = self._dao.listar_por_filtros(
            {"id_equipo_int": id_equipo_int}
        )

        for orden in ordenes:
            fecha_orden = orden.get("fecha_programada")
            if isinstance(fecha_orden, str):
                fecha_orden = date.fromisoformat(fecha_orden)

            if (
                orden.get("estado_orden") in ESTADOS_ACTIVOS
                and fecha_orden == fecha_programada
            ):
                raise EntidadDuplicadaError(
                    f"RN-02: El equipo '{id_equipo}' ya tiene una orden activa "
                    f"para la fecha {fecha_programada} (id={orden['id_orden']}, "
                    f"estado={orden['estado_orden']})."
                )

        datos = {
            "id_orden":            id_orden,
            "id_equipo_int":       id_equipo_int,
            "tipo_mantenimiento":  tipo_mantenimiento,
            "fecha_programada":    fecha_programada,
            "descripcion_trabajo": descripcion_trabajo,
            "costo_estimado":      costo_estimado,
            "estado_orden":        "Programada",
            "id_tecnico_int":      None,
        }
        return self._dao.insertar(datos)

    def consultar_orden(self, id_orden):
        id_orden_int = self._dao.obtener_id_orden_int(id_orden)
        if not id_orden_int:
            raise EntidadNoEncontradaError(f"Orden '{id_orden}' no encontrada")
            
        orden = self._dao.buscar_por_id(id_orden_int)
        if not orden:
            raise EntidadNoEncontradaError(f"Orden '{id_orden}' no encontrada")
        return orden

    def asignar_tecnico(self, id_orden, id_tecnico):
        id_orden_int = self._dao.obtener_id_orden_int(id_orden)
        if not id_orden_int:
            raise EntidadNoEncontradaError(f"Orden '{id_orden}' no encontrada")
            
        orden = self._dao.buscar_por_id(id_orden_int)
        if not orden:
            raise EntidadNoEncontradaError(f"Orden '{id_orden}' no encontrada")

        id_tecnico_int = self._tecnico_dao.obtener_id_tecnico_int(id_tecnico)
        if not id_tecnico_int:
            raise EntidadNoEncontradaError(f"Técnico '{id_tecnico}' no encontrado")
            
        tecnico = self._tecnico_dao.buscar_por_id(id_tecnico_int)
        if not tecnico:
            raise EntidadNoEncontradaError(f"Técnico '{id_tecnico}' no encontrado")

        equipo = self._equipo_dao.buscar_por_id(orden["id_equipo_int"])
        if not equipo:
            raise EntidadNoEncontradaError("Equipo vinculado a la orden no encontrado")

        estado_tecnico = tecnico.get("estatus") or tecnico.get("estado")
        if estado_tecnico != "Activo":
            raise ReglaNegocioError(
                f"RN-03: El técnico '{id_tecnico}' está Inactivo y no puede ser asignado."
            )

        if _nfc(tecnico["especialidad"]) != _nfc(equipo["tipo"]):
            raise ReglaNegocioError(
                f"RN-01: La especialidad del técnico ('{tecnico['especialidad']}') "
                f"no coincide con el tipo del equipo ('{equipo['tipo']}')."
            )
        
        if _nfc(equipo["criticidad"]) == "Alta":
            nivel = NIVEL_NUM.get(_nfc(tecnico["nivel_certificacion"]), 0)
            if nivel < 2:
                raise ReglaNegocioError(
                    f"RN-07: El equipo '{equipo['id_equipo']}' es de criticidad Alta. "
                    f"Se requiere nivel ≥ II; el técnico tiene nivel '{tecnico['nivel_certificacion']}'."
                )
        
        ordenes_activas = self._dao.listar_por_filtros(
            {"id_tecnico_int": id_tecnico_int, "estado_orden": "En ejecucion"}
        )

        if ordenes_activas:
            raise ReglaNegocioError("No es posible asignar un técnico con una orden En ejecucion")

        return self._dao.asignar_tecnico(id_orden_int, id_tecnico_int)
    
    def solicitar_cierre(self, id_orden: str, id_usuario_int: int) -> bool:
        """Permite a un técnico solicitar el cierre de una orden en ejecución."""
        orden = self._dao.buscar_por_id(self._dao.obtener_id_orden_int(id_orden))
        
        if not orden:
            raise EntidadNoEncontradaError(f"La orden '{id_orden}' no existe.")

        if orden["estado_orden"].lower() != "en ejecucion":
            raise ReglaNegocioError(
                f"No se puede solicitar el cierre. La orden está en estado '{orden['estado_orden']}'."
            )

        if orden["id_tecnico_int"] != id_usuario_int:
            raise ReglaNegocioError("No está autorizado a solicitar el cierre de una orden asignada a otro técnico.")

        return self._dao.actualizar_estado(orden["id_orden_int"], "Pendiente de cierre")

    def iniciar_ejecucion(self, id_orden, fecha_inicio):
        id_orden_int = self._dao.obtener_id_orden_int(id_orden)
        if not id_orden_int:
            raise EntidadNoEncontradaError(f"Orden '{id_orden}' no encontrada")
            
        orden = self._dao.buscar_por_id(id_orden_int)
        if not orden:
            raise EntidadNoEncontradaError(f"Orden '{id_orden}' no encontrada")

        self._validar_transicion(orden["estado_orden"], "En ejecucion")

        fp = _parse_fecha(orden["fecha_programada"])
        fi = _parse_fecha(fecha_inicio)
        if fi < fp:
            raise ReglaNegocioError(
                f"RN-05: La fecha de inicio ({fecha_inicio}) no puede ser "
                f"anterior a la fecha programada ({orden['fecha_programada']})."
            )

        self._dao.actualizar_estado(id_orden_int, "En ejecucion")
        return self._dao.actualizar_inicio(id_orden_int, fecha_inicio)

    def finalizar_orden(self, id_orden, fecha_cierre, costo_real):
        id_orden_int = self._dao.obtener_id_orden_int(id_orden)
        if not id_orden_int:
            raise EntidadNoEncontradaError(f"Orden '{id_orden}' no encontrada")
            
        orden = self._dao.buscar_por_id(id_orden_int)
        if not orden:
            raise EntidadNoEncontradaError(f"Orden '{id_orden}' no encontrada")

        self._validar_transicion(orden["estado_orden"], "Finalizada")

        if not fecha_cierre:
            raise ReglaNegocioError("RN-06: La fecha de cierre es obligatoria al finalizar.")
        if costo_real is None:
            raise ReglaNegocioError("RN-06: El costo real es obligatorio al finalizar.")

        fecha_inicio_raw = orden.get("fecha_inicio").date()
        
        if fecha_inicio_raw:
            fi = _parse_fecha(fecha_inicio_raw)
            fc = _parse_fecha(fecha_cierre)
            if fc < fi:
                raise ReglaNegocioError(
                    f"RN-05: La fecha de cierre ({fecha_cierre}) no puede ser "
                    f"anterior a la fecha de inicio ({fecha_inicio_raw})."
                )

        self._dao.actualizar_estado(id_orden_int, "Finalizada")
        return self._dao.actualizar_cierre(id_orden_int, fecha_cierre, costo_real)

    def cancelar_orden(self, id_orden):
        id_orden_int = self._dao.obtener_id_orden_int(id_orden)
        if not id_orden_int:
            raise EntidadNoEncontradaError(f"Orden '{id_orden}' no encontrada")
            
        orden = self._dao.buscar_por_id(id_orden_int)
        if not orden:
            raise EntidadNoEncontradaError(f"Orden '{id_orden}' no encontrada")

        self._validar_transicion(orden["estado_orden"], "Cancelada")
        return self._dao.actualizar_estado(id_orden_int, "Cancelada")

    def listar_ordenes_por_filtro(self, filtros: dict) -> list:
        filtros_copy = filtros.copy()

        if "id_equipo" in filtros_copy:
            id_equipo_str = filtros_copy.pop("id_equipo") 
            filtros_copy["id_equipo_int"] = self._equipo_dao.obtener_id_equipo_int(id_equipo_str)

        if "id_tecnico" in filtros_copy:
            id_tecnico_str = filtros_copy.pop("id_tecnico") 
            filtros_copy["id_tecnico_int"] = self._tecnico_dao.obtener_id_tecnico_int(id_tecnico_str)

        return self._dao.listar_por_filtros(filtros_copy)
    
    def _validar_transicion(self, estado_actual: str, estado_nuevo: str) -> None:
        estado_actual_nfc = _nfc(estado_actual)
        permitidos = TRANSICIONES_VALIDAS.get(estado_actual_nfc, [])
        if _nfc(estado_nuevo) not in [_nfc(p) for p in permitidos]:
            raise EstadoInvalidoError(
                f"RN-08: Transicion inválida de '{estado_actual}' → '{estado_nuevo}'. "
                f"Transiciones permitidas: {permitidos}."
            )


def _parse_fecha(valor) -> date:
    if isinstance(valor, date):
        return valor
    return date.fromisoformat(str(valor))