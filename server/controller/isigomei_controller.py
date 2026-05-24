import functools
import logging
import Pyro5.api

from server.auth.auth_manager import AuthManager
from server.service.equipo_service import EquipoService
from server.service.tecnico_service import TecnicoService
from server.service.orden_service import OrdenService
from server.exceptions.exceptions import (
    EntidadDuplicadaError, EntidadNoEncontradaError,
    ReglaNegocioError, EstadoInvalidoError,
    IntegridadReferencialError, AutenticacionError,
)

log = logging.getLogger("sigomei.server")

def _pyro_safe(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        params = args[1:] if len(args) > 1 else ""
        
        log.info(f"Solicitud remota recibida: {fn.__name__} | Parámetros: {params}")
        
        try:
            resultado = fn(*args, **kwargs)
            
            log.info(f"Operación exitosa: {fn.__name__} | Respuesta: {resultado}")
            return resultado
            
        except EntidadDuplicadaError as e:
            log.warning(f"Rechazado en {fn.__name__}: EntidadDuplicadaError — {e}")
            raise ValueError(f"EntidadDuplicadaError: {e}") from None
            
        except EntidadNoEncontradaError as e:
            log.warning(f"Rechazado en {fn.__name__}: EntidadNoEncontradaError — {e}")
            raise LookupError(f"EntidadNoEncontradaError: {e}") from None
            
        except (ReglaNegocioError, EstadoInvalidoError, IntegridadReferencialError) as e:
            log.warning(f"Validación de Regla denegada en {fn.__name__}: {type(e).__name__} — {e}")
            raise PermissionError(f"{type(e).__name__}: {e}") from None
            
        except AutenticacionError as e:
            log.warning(f"Falla de autenticación: {e}")
            raise ConnectionRefusedError(f"AutenticacionError: {e}") from None
            
        except Exception as e:
            log.error(f"Error crítico interno en {fn.__name__}: {type(e).__name__} — {e}", exc_info=True)
            raise RuntimeError(f"{type(e).__name__}: {e}") from None
            
    return wrapper


@Pyro5.api.expose
class ISigomeiController:

    def __init__(self):
        self._auth        = AuthManager()
        self._equipo_svc  = EquipoService()
        self._tecnico_svc = TecnicoService()
        self._orden_svc   = OrdenService()

    #  Autenticación
    @_pyro_safe
    def login(self, username: str, password: str) -> str:
        return self._auth.login(username, password)

    @_pyro_safe
    def logout(self, token: str) -> bool:
        return self._auth.logout(token)

    #  Equipos
    @_pyro_safe
    def alta_equipo(self, id_equipo, nombre, tipo, marca, modelo,
                    numero_serie, ubicacion_planta, fecha_instalacion,
                    estado_operativo, criticidad) -> bool:
        return self._equipo_svc.alta_equipo(
            id_equipo, nombre, tipo, marca, modelo,
            numero_serie, ubicacion_planta, fecha_instalacion,
            estado_operativo, criticidad,
        )

    @_pyro_safe
    def consultar_equipo(self, id_equipo: str) -> dict:
        return self._equipo_svc.consultar_equipo(id_equipo)

    @_pyro_safe
    def modificar_equipo(self, id_equipo: str, datos_actualizados: dict) -> bool:
        return self._equipo_svc.modificar_equipo(id_equipo, datos_actualizados)

    @_pyro_safe
    def baja_equipo(self, id_equipo: str) -> bool:
        return self._equipo_svc.baja_equipo(id_equipo)

    #  Técnicos
    @_pyro_safe
    def alta_tecnico(self, id_tecnico, nombre_completo, rfc, telefono,
                     correo, especialidad, nivel_certificacion,
                     fecha_ingreso, estatus) -> bool:
        return self._tecnico_svc.alta_tecnico(
            id_tecnico, nombre_completo, rfc, telefono, correo,
            especialidad, nivel_certificacion, fecha_ingreso, estatus,
        )

    @_pyro_safe
    def consultar_tecnico(self, id_tecnico: str) -> dict:
        return self._tecnico_svc.consultar_tecnico(id_tecnico)

    @_pyro_safe
    def modificar_tecnico(self, id_tecnico: str, datos_actualizados: dict) -> bool:
        return self._tecnico_svc.modificar_tecnico(id_tecnico, datos_actualizados)

    @_pyro_safe
    def baja_tecnico(self, id_tecnico: str) -> bool:
        return self._tecnico_svc.baja_tecnico(id_tecnico)

    #  Órdenes de Mantenimiento
    @_pyro_safe
    def crear_orden(self, id_orden, id_equipo, tipo_mantenimiento,
                    fecha_programada, descripcion_trabajo,
                    costo_estimado) -> bool:
        return self._orden_svc.crear_orden(
            id_orden, id_equipo, tipo_mantenimiento,
            fecha_programada, descripcion_trabajo, costo_estimado,
        )

    @_pyro_safe
    def consultar_orden(self, id_orden: str) -> dict:
        return self._orden_svc.consultar_orden(id_orden)

    @_pyro_safe
    def asignar_tecnico(self, id_orden: str, id_tecnico: str) -> bool:
        return self._orden_svc.asignar_tecnico(id_orden, id_tecnico)

    @_pyro_safe
    def iniciar_ejecucion(self, id_orden: str, fecha_inicio: str) -> bool:
        return self._orden_svc.iniciar_ejecucion(id_orden, fecha_inicio)

    @_pyro_safe
    def finalizar_orden(self, id_orden: str, fecha_cierre: str,
                        costo_real: float) -> bool:
        return self._orden_svc.finalizar_orden(id_orden, fecha_cierre, costo_real)

    @_pyro_safe
    def cancelar_orden(self, id_orden: str) -> bool:
        return self._orden_svc.cancelar_orden(id_orden)

    @_pyro_safe
    def listar_ordenes_por_filtro(self, filtros: dict) -> list:
        return self._orden_svc.listar_ordenes_por_filtro(filtros)