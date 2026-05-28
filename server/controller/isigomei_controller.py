import functools
import logging
import Pyro5.api

from server.auth.auth_manager import AuthManager
from server.service.equipo_service import EquipoService
from server.service.tecnico_service import TecnicoService
from server.service.orden_service import OrdenService
from server.service.usuario_service import UsuarioService
from server.exceptions.exceptions import (
    EntidadDuplicadaError,
    EntidadNoEncontradaError,
    ReglaNegocioError,
    EstadoInvalidoError,
    IntegridadReferencialError,
    AutenticacionError,
)

log = logging.getLogger("sigomei.server")


def _pyro_safe(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):

        params = args[1:] if len(args) > 1 else ""

        log.info(
            f"Solicitud remota recibida: "
            f"{fn.__name__} | Parámetros: {params}"
        )

        try:
            resultado = fn(*args, **kwargs)

            log.info(
                f"Operación exitosa: "
                f"{fn.__name__} | Respuesta: {resultado}"
            )

            return resultado

        except EntidadDuplicadaError as e:
            log.warning(
                f"Rechazado en {fn.__name__}: "
                f"EntidadDuplicadaError — {e}"
            )
            raise ValueError(
                f"EntidadDuplicadaError: {e}"
            ) from None

        except EntidadNoEncontradaError as e:
            log.warning(
                f"Rechazado en {fn.__name__}: "
                f"EntidadNoEncontradaError — {e}"
            )
            raise LookupError(
                f"EntidadNoEncontradaError: {e}"
            ) from None

        except (
            ReglaNegocioError,
            EstadoInvalidoError,
            IntegridadReferencialError,
        ) as e:

            log.warning(
                f"Validación de regla denegada "
                f"en {fn.__name__}: "
                f"{type(e).__name__} — {e}"
            )

            raise PermissionError(
                f"{type(e).__name__}: {e}"
            ) from None

        except AutenticacionError as e:
            log.warning(
                f"Falla de autenticación: {e}"
            )

            raise ConnectionRefusedError(
                f"AutenticacionError: {e}"
            ) from None

        except Exception as e:
            log.error(
                f"Error crítico interno "
                f"en {fn.__name__}: "
                f"{type(e).__name__} — {e}",
                exc_info=True
            )

            raise RuntimeError(
                f"{type(e).__name__}: {e}"
            ) from None

    return wrapper


@Pyro5.api.expose
class ISigomeiController:

    def __init__(self):
        self._auth = AuthManager()

        self._equipo_svc = EquipoService()
        self._tecnico_svc = TecnicoService()
        self._orden_svc = OrdenService()
        self._usuario_svc = UsuarioService()


    @_pyro_safe
    def login(
        self,
        correo: str,
        password: str
    ) -> str:

        return self._auth.login(
            correo,
            password
        )

    @_pyro_safe
    def logout(
        self,
        token: str
    ) -> bool:

        return self._auth.logout(token)


    @_pyro_safe
    def alta_equipo(
        self,
        token,
        id_equipo,
        nombre,
        tipo,
        marca,
        modelo,
        numero_serie,
        ubicacion_planta,
        fecha_instalacion,
        estado_operativo,
        criticidad
    ) -> bool:

        self._auth.validar_supervision(token)

        return self._equipo_svc.alta_equipo(
            id_equipo,
            nombre,
            tipo,
            marca,
            modelo,
            numero_serie,
            ubicacion_planta,
            fecha_instalacion,
            estado_operativo,
            criticidad,
        )

    @_pyro_safe
    def consultar_equipo(
        self,
        token,
        id_equipo: str
    ) -> dict:

        self._auth.verificar(token)

        return self._equipo_svc.consultar_equipo(
            id_equipo
        )

    @_pyro_safe
    def modificar_equipo(
        self,
        token,
        id_equipo: str,
        datos_actualizados: dict
    ) -> bool:

        self._auth.validar_supervision(token)

        return self._equipo_svc.modificar_equipo(
            id_equipo,
            datos_actualizados
        )

    @_pyro_safe
    def baja_equipo(
        self,
        token,
        id_equipo: str
    ) -> bool:

        self._auth.validar_supervision(token)

        return self._equipo_svc.baja_equipo(
            id_equipo
        )

    @_pyro_safe
    def listar_equipos(
        self,
        token
    ) -> list:

        self._auth.verificar(token)

        return self._equipo_svc.listar_equipos()


    @_pyro_safe
    def alta_tecnico(
        self,
        token,
        id_tecnico,
        nombre_completo,
        rfc,
        telefono,
        correo,
        especialidad,
        nivel_certificacion,
        fecha_ingreso,
        estatus
    ) -> bool:

        self._auth.validar_supervision(token)

        return self._tecnico_svc.alta_tecnico(
            id_tecnico,
            nombre_completo,
            rfc,
            telefono,
            correo,
            especialidad,
            nivel_certificacion,
            fecha_ingreso,
            estatus,
        )

    @_pyro_safe
    def consultar_tecnico(
        self,
        token,
        id_tecnico: str
    ) -> dict:

        self._auth.verificar(token)

        return self._tecnico_svc.consultar_tecnico(
            id_tecnico
        )

    @_pyro_safe
    def modificar_tecnico(
        self,
        token,
        id_tecnico: str,
        datos_actualizados: dict
    ) -> bool:

        self._auth.validar_supervision(token)

        return self._tecnico_svc.modificar_tecnico(
            id_tecnico,
            datos_actualizados
        )

    @_pyro_safe
    def baja_tecnico(
        self,
        token,
        id_tecnico: str
    ) -> bool:

        self._auth.validar_supervision(token)

        return self._tecnico_svc.baja_tecnico(
            id_tecnico
        )

    @_pyro_safe
    def listar_tecnicos(
        self,
        token
    ) -> list:

        self._auth.verificar(token)

        return self._tecnico_svc.listar_tecnicos()

    @_pyro_safe
    def listar_tecnicos_por_filtro(
        self,
        token,
        filtros: dict
    ) -> list:

        self._auth.verificar(token)

        return self._tecnico_svc.listar_tecnicos_por_filtro(
            filtros
        )

    @_pyro_safe
    def crear_orden(
        self,
        token,
        id_orden,
        id_equipo,
        tipo_mantenimiento,
        fecha_programada,
        descripcion_trabajo,
        costo_estimado
    ) -> bool:

        sesion = self._auth.validar_supervision(
            token
        )

        return self._orden_svc.crear_orden(
            id_orden,
            id_equipo,
            tipo_mantenimiento,
            fecha_programada,
            descripcion_trabajo,
            costo_estimado,
            # creado_por_int=sesion["id_usuario_int"]
        )

    @_pyro_safe
    def consultar_orden(
        self,
        token,
        id_orden: str
    ) -> dict:

        self._auth.verificar(token)

        return self._orden_svc.consultar_orden(
            id_orden
        )

    @_pyro_safe
    def asignar_tecnico(
        self,
        token,
        id_orden: str,
        id_tecnico: str
    ) -> bool:

        self._auth.verificar(token)

        return self._orden_svc.asignar_tecnico(
            id_orden,
            id_tecnico
        )
    

    @_pyro_safe
    def solicitar_cierre(self, token: str, id_orden: str) -> bool:
        """
        RF-09 | Permite a un técnico autenticado enviar una solicitud de cierre
        para una orden asignada bajo su cargo.
        """
        sesion = self._auth.verificar(token)
        return self._orden_svc.solicitar_cierre(id_orden, sesion["id_usuario_int"])

    # RN-14
    @_pyro_safe
    def iniciar_ejecucion(
        self,
        token,
        id_orden: str,
        fecha_inicio: str
    ) -> bool:

        self._auth.verificar(token)

        return self._orden_svc.iniciar_ejecucion(
            id_orden,
            fecha_inicio
        )

    # RN-20
    @_pyro_safe
    def finalizar_orden(
        self,
        token,
        id_orden: str,
        fecha_cierre: str,
        costo_real: float
    ) -> bool:

        self._auth.validar_supervision(token)

        return self._orden_svc.finalizar_orden(
            id_orden,
            fecha_cierre,
            costo_real
        )

    @_pyro_safe
    def cancelar_orden(
        self,
        token,
        id_orden: str
    ) -> bool:

        self._auth.verificar(token)

        return self._orden_svc.cancelar_orden(
            id_orden
        )

    @_pyro_safe
    def listar_ordenes_por_filtro(
        self,
        token,
        filtros: dict
    ) -> list:

        self._auth.verificar(token)

        return self._orden_svc.listar_ordenes_por_filtro(
            filtros
        )


    @_pyro_safe
    def alta_usuario(
        self,
        token,
        nombre_completo,
        rfc,
        telefono,
        correo,
        contrasena,
        id_rol,
        id_usuario,
        estado="Activo"
    ) -> bool:

        self._auth.validar_supervision(
            token
        )

        return self._usuario_svc.alta_usuario(
            nombre_completo,
            rfc,
            telefono,
            correo,
            contrasena,
            id_rol,
            id_usuario,
            estado
        )

    @_pyro_safe
    def consultar_usuario(
        self,
        token,
        id_usuario: str
    ) -> dict:

        self._auth.verificar(token)

        return self._usuario_svc.consultar_usuario(
            id_usuario
        )

    @_pyro_safe
    def modificar_usuario(
        self,
        token,
        id_usuario: str,
        datos_actualizados: dict
    ) -> bool:

        self._auth.validar_supervision(
            token
        )

        return self._usuario_svc.modificar_usuario(
            id_usuario,
            datos_actualizados
        )

    @_pyro_safe
    def baja_usuario(
        self,
        token,
        id_usuario: str
    ) -> bool:

        self._auth.validar_supervision(
            token
        )

        return self._usuario_svc.baja_usuario(
            id_usuario
        )

    @_pyro_safe
    def listar_usuarios(
        self,
        token
    ) -> list:

        self._auth.validar_supervision(
            token
        )

        return self._usuario_svc.listar_usuarios()