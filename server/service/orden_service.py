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
    "Programada":    ["En Ejecución", "Cancelada"],
    "En ejecución":  ["Finalizada",   "Cancelada"],
    "Finalizada":    [],
    "Cancelada":     [],
}

ESTADOS_ACTIVOS = {"Programada", "En Ejecución"}


class OrdenService:

    def __init__(self):
        self._dao         = OrdenDAO()
        self._equipo_dao  = EquipoDAO()
        self._tecnico_dao = TecnicoDAO()

    def crear_orden(
        self,
        id_orden: str,
        id_equipo: str,
        tipo_mantenimiento: str,
        fecha_programada: str,
        descripcion_trabajo: str,
        costo_estimado: float,
    ) -> bool:
        # Verificar que el equipo exista
        equipo = self._equipo_dao.buscar_por_id(id_equipo)
        if not equipo:
            raise EntidadNoEncontradaError(f"Equipo '{id_equipo}' no encontrado")

        # RN-02: El equipo no debe tener ya una orden activa EN LA MISMA FECHA
        ordenes = self._dao.listar_por_filtros({"id_equipo": id_equipo})
        for o in ordenes:
            # Agregamos la validación de la fecha programada aquí:
            if o.get("estado_orden") in ESTADOS_ACTIVOS and o.get("fecha_programada") == fecha_programada:
                raise EntidadDuplicadaError(
                    f"RN-02: El equipo '{id_equipo}' ya tiene una orden activa "
                    f"para la fecha {fecha_programada} "
                    f"(id={o['id_orden']}, estado={o['estado_orden']})."
                )

        datos = {
            "id_orden":           id_orden,
            "id_equipo":          id_equipo,
            "tipo_mantenimiento": tipo_mantenimiento,
            "fecha_programada":   fecha_programada,
            "descripcion_trabajo":descripcion_trabajo,
            "costo_estimado":     costo_estimado,
            "estado_orden":       "Programada",
            "id_tecnico":         None,
        }
        return self._dao.insertar(datos)

    def consultar_orden(self, id_orden: str) -> dict:
        orden = self._dao.buscar_por_id(id_orden)
        if not orden:
            raise EntidadNoEncontradaError(f"Orden '{id_orden}' no encontrada")
        return orden

    def asignar_tecnico(self, id_orden: str, id_tecnico: str) -> bool:
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

        # RN-03: Técnico debe estar Activo
        if tecnico["estatus"] != "Activo":
            raise ReglaNegocioError(
                f"RN-03: El técnico '{id_tecnico}' está Inactivo y no puede "
                "ser asignado a una orden."
            )

        # RN-01: La especialidad del técnico debe coincidir con el tipo del equipo
        if tecnico["especialidad"] != equipo["tipo"]:
            raise ReglaNegocioError(
                f"RN-01: La especialidad del técnico ('{tecnico['especialidad']}') "
                f"no coincide con el tipo del equipo ('{equipo['tipo']}')."
            )

        # RN-07: Equipos de criticidad Alta requieren técnico con nivel ≥ II
        if equipo["criticidad"] == "Alta":
            nivel = NIVEL_NUM.get(tecnico["nivel_certificacion"], 0)
            if nivel < 2:
                raise ReglaNegocioError(
                    f"RN-07: El equipo '{equipo['id_equipo']}' es de criticidad Alta. "
                    f"Se requiere técnico con nivel ≥ II; "
                    f"el técnico tiene nivel '{tecnico['nivel_certificacion']}'."
                )

        return self._dao.asignar_tecnico(id_orden, id_tecnico)

    def iniciar_ejecucion(self, id_orden: str, fecha_inicio: str) -> bool:
        orden = self._dao.buscar_por_id(id_orden)
        if not orden:
            raise EntidadNoEncontradaError(f"Orden '{id_orden}' no encontrada")

        # RN-08: Transición válida
        self._validar_transicion(orden["estado_orden"], "En Ejecución")

        # RN-05: fecha_inicio ≥ fecha_programada
        fp = _parse_fecha(orden["fecha_programada"])
        fi = _parse_fecha(fecha_inicio)
        if fi < fp:
            raise ReglaNegocioError(
                f"RN-05: La fecha de inicio ({fecha_inicio}) no puede ser "
                f"anterior a la fecha programada ({orden['fecha_programada']})."
            )

        self._dao.actualizar_estado(id_orden, "En Ejecución")
        return self._dao.actualizar_inicio(id_orden, fecha_inicio)

    def finalizar_orden(
        self, id_orden: str, fecha_cierre: str, costo_real: float
    ) -> bool:
        orden = self._dao.buscar_por_id(id_orden)
        if not orden:
            raise EntidadNoEncontradaError(f"Orden '{id_orden}' no encontrada")

        # RN-08: Transición válida
        self._validar_transicion(orden["estado_orden"], "Finalizada")

        # RN-06: Campos obligatorios al finalizar
        if not fecha_cierre:
            raise ReglaNegocioError(
                "RN-06: La fecha de cierre es obligatoria al finalizar la orden."
            )
        if costo_real is None:
            raise ReglaNegocioError(
                "RN-06: El costo real es obligatorio al finalizar la orden."
            )

        # RN-05: fecha_cierre ≥ fecha_inicio (si existe)
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

    def cancelar_orden(self, id_orden: str) -> bool:
        orden = self._dao.buscar_por_id(id_orden)
        if not orden:
            raise EntidadNoEncontradaError(f"Orden '{id_orden}' no encontrada")

        # RN-08: Transición válida
        self._validar_transicion(orden["estado_orden"], "Cancelada")

        return self._dao.actualizar_estado(id_orden, "Cancelada")

    def listar_ordenes_por_filtro(self, filtros: dict) -> list:
        return self._dao.listar_por_filtros(filtros)

    def _validar_transicion(self, estado_actual: str, estado_nuevo: str) -> None:
        """RN-08: Verifica que la transición de estado sea permitida."""
        permitidos = TRANSICIONES_VALIDAS.get(estado_actual, [])
        if estado_nuevo not in permitidos:
            raise EstadoInvalidoError(
                f"RN-08: Transición inválida de '{estado_actual}' → '{estado_nuevo}'. "
                f"Transiciones permitidas: {permitidos}."
            )


def _parse_fecha(valor) -> date:
    """Convierte str ISO-8601 o date a objeto date."""
    if isinstance(valor, date):
        return valor
    return date.fromisoformat(str(valor))