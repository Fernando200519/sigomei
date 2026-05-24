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
    "Programada":   ["En ejecución", "Cancelada"],
    "En ejecución": ["Finalizada",   "Cancelada"],
    "Finalizada":   [],
    "Cancelada":    [],
}

ESTADOS_ACTIVOS = {"Programada", "En ejecución"}


def _nfc(texto: str) -> str:
    return unicodedata.normalize("NFC", texto)


class OrdenService:

    def __init__(self):
        self._dao         = OrdenDAO()
        self._equipo_dao  = EquipoDAO()
        self._tecnico_dao = TecnicoDAO()

    def crear_orden(self, id_orden, id_equipo, tipo_mantenimiento,
                    fecha_programada, descripcion_trabajo, costo_estimado):
        equipo = self._equipo_dao.buscar_por_id(id_equipo)
        if not equipo:
            raise EntidadNoEncontradaError(f"Equipo '{id_equipo}' no encontrado")
        
        if costo_estimado < 0:
            raise ReglaNegocioError()

        # RN-02: El equipo no debe tener ya una orden activa EN LA MISMA FECHA
        if isinstance(fecha_programada, str):
            fecha_programada = date.fromisoformat(fecha_programada)

        ordenes = self._dao.listar_por_filtros(
            {"id_equipo": id_equipo}
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
                    f"RN-02: El equipo '{id_equipo}' "
                    f"ya tiene una orden activa "
                    f"para la fecha {fecha_programada} "
                    f"(id={orden['id_orden']}, "
                    f"estado={orden['estado_orden']})."
                )

        datos = {
            "id_orden":            id_orden,
            "id_equipo":           id_equipo,
            "tipo_mantenimiento":  tipo_mantenimiento,
            "fecha_programada":    fecha_programada,
            "descripcion_trabajo": descripcion_trabajo,
            "costo_estimado":      costo_estimado,
            "estado_orden":        "Programada",
            "id_tecnico":          None,
        }
        return self._dao.insertar(datos)

    def consultar_orden(self, id_orden):
        orden = self._dao.buscar_por_id(id_orden)
        if not orden:
            raise EntidadNoEncontradaError(f"Orden '{id_orden}' no encontrada")
        return orden

    def asignar_tecnico(self, id_orden, id_tecnico):
        orden = self._dao.buscar_por_id(id_orden)
        if not orden:
            raise EntidadNoEncontradaError(f"Orden '{id_orden}' no encontrada")

        tecnico = self._tecnico_dao.buscar_por_id(id_tecnico)
        if not tecnico:
            raise EntidadNoEncontradaError(f"Técnico '{id_tecnico}' no encontrado")

        equipo = self._equipo_dao.buscar_por_id(orden["id_equipo"])
        if not equipo:
            raise EntidadNoEncontradaError(
                f"Equipo '{orden['id_equipo']}' vinculado a la orden no encontrado"
            )

        if tecnico["estatus"] != "Activo":
            raise ReglaNegocioError(
                f"RN-03: El técnico '{id_tecnico}' está Inactivo y no puede "
                "ser asignado a una orden."
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
                    f"Se requiere nivel ≥ II; el técnico tiene nivel "
                    f"'{tecnico['nivel_certificacion']}'."
                )
        
        # RN-16:
        ordenes_activas = self._dao.listar_por_filtros(
            {"id_tecnico": id_tecnico,
             "estado_orden": "En Ejecucion"}
        )

        if ordenes_activas:
            raise ReglaNegocioError("No es posible asignar un técnico con una orden En Ejecucion"
            )

        return self._dao.asignar_tecnico(id_orden, id_tecnico)

    def iniciar_ejecucion(self, id_orden, fecha_inicio):
        orden = self._dao.buscar_por_id(id_orden)
        if not orden:
            raise EntidadNoEncontradaError(f"Orden '{id_orden}' no encontrada")

        self._validar_transicion(orden["estado_orden"], "En ejecución")

        fp = _parse_fecha(orden["fecha_programada"])
        fi = _parse_fecha(fecha_inicio)
        if fi < fp:
            raise ReglaNegocioError(
                f"RN-05: La fecha de inicio ({fecha_inicio}) no puede ser "
                f"anterior a la fecha programada ({orden['fecha_programada']})."
            )

        self._dao.actualizar_estado(id_orden, "En ejecución")
        return self._dao.actualizar_inicio(id_orden, fecha_inicio)

    def finalizar_orden(self, id_orden, fecha_cierre, costo_real):
        orden = self._dao.buscar_por_id(id_orden)
        if not orden:
            raise EntidadNoEncontradaError(f"Orden '{id_orden}' no encontrada")

        self._validar_transicion(orden["estado_orden"], "Finalizada")

        if not fecha_cierre:
            raise ReglaNegocioError(
                "RN-06: La fecha de cierre es obligatoria al finalizar."
            )
        if costo_real is None:
            raise ReglaNegocioError(
                "RN-06: El costo real es obligatorio al finalizar."
            )

        fecha_inicio_raw = orden.get("fecha_inicio")
        if fecha_inicio_raw:
            fi = _parse_fecha(fecha_inicio_raw)
            fc = _parse_fecha(fecha_cierre)
            if fc < fi:
                raise ReglaNegocioError(
                    f"RN-05: La fecha de cierre ({fecha_cierre}) no puede ser "
                    f"anterior a la fecha de inicio ({fecha_inicio_raw})."
                )

        self._dao.actualizar_estado(id_orden, "Finalizada")
        return self._dao.actualizar_cierre(id_orden, fecha_cierre, costo_real)

    def cancelar_orden(self, id_orden):
        orden = self._dao.buscar_por_id(id_orden)
        if not orden:
            raise EntidadNoEncontradaError(f"Orden '{id_orden}' no encontrada")

        self._validar_transicion(orden["estado_orden"], "Cancelada")
        return self._dao.actualizar_estado(id_orden, "Cancelada")

    def listar_ordenes_por_filtro(self, filtros):
        return self._dao.listar_por_filtros(filtros)

    def _validar_transicion(self, estado_actual: str, estado_nuevo: str) -> None:
        """RN-08: verifica que la transición sea permitida.
        Normaliza NFC para manejar diferencias de encoding entre Python y PostgreSQL.
        """
        estado_actual_nfc = _nfc(estado_actual)
        permitidos = TRANSICIONES_VALIDAS.get(estado_actual_nfc, [])
        if _nfc(estado_nuevo) not in [_nfc(p) for p in permitidos]:
            raise EstadoInvalidoError(
                f"RN-08: Transición inválida de '{estado_actual}' → '{estado_nuevo}'. "
                f"Transiciones permitidas: {permitidos}."
            )


def _parse_fecha(valor) -> date:
    if isinstance(valor, date):
        return valor
    return date.fromisoformat(str(valor))