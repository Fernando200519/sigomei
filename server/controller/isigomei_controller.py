import Pyro5.api

from server.auth.auth_manager import AuthManager
from server.service.equipo_service import EquipoService
from server.service.tecnico_service import TecnicoService
from server.service.orden_service import OrdenService

@Pyro5.api.expose
class ISigomeiController:

    def __init__(self):
        self._auth        = AuthManager()
        self._equipo_svc  = EquipoService()
        self._tecnico_svc = TecnicoService()
        self._orden_svc   = OrdenService()

    #  Autenticación

    def login(self, username: str, password: str) -> str:
        """Devuelve un token de sesión o lanza AutenticacionError."""
        return self._auth.login(username, password)

    def logout(self, token: str) -> bool:
        return self._auth.logout(token)

    # Equipos

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
        return self._equipo_svc.alta_equipo(
            id_equipo, nombre, tipo, marca, modelo,
            numero_serie, ubicacion_planta, fecha_instalacion,
            estado_operativo, criticidad,
        )

    def consultar_equipo(self, id_equipo: str) -> dict:
        return self._equipo_svc.consultar_equipo(id_equipo)

    def modificar_equipo(self, id_equipo: str, datos_actualizados: dict) -> bool:
        return self._equipo_svc.modificar_equipo(id_equipo, datos_actualizados)

    def baja_equipo(self, id_equipo: str) -> bool:
        return self._equipo_svc.baja_equipo(id_equipo)

    # Técnicos

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
        return self._tecnico_svc.alta_tecnico(
            id_tecnico, nombre_completo, rfc, telefono, correo,
            especialidad, nivel_certificacion, fecha_ingreso, estatus,
        )

    def consultar_tecnico(self, id_tecnico: str) -> dict:
        return self._tecnico_svc.consultar_tecnico(id_tecnico)

    def modificar_tecnico(self, id_tecnico: str, datos_actualizados: dict) -> bool:
        return self._tecnico_svc.modificar_tecnico(id_tecnico, datos_actualizados)

    def baja_tecnico(self, id_tecnico: str) -> bool:
        return self._tecnico_svc.baja_tecnico(id_tecnico)

    # Órdenes de Mantenimiento

    def crear_orden(
        self,
        id_orden: str,
        id_equipo: str,
        tipo_mantenimiento: str,
        fecha_programada: str,
        descripcion_trabajo: str,
        costo_estimado: float,
    ) -> bool:
        return self._orden_svc.crear_orden(
            id_orden, id_equipo, tipo_mantenimiento,
            fecha_programada, descripcion_trabajo, costo_estimado,
        )

    def consultar_orden(self, id_orden: str) -> dict:
        return self._orden_svc.consultar_orden(id_orden)

    def asignar_tecnico(self, id_orden: str, id_tecnico: str) -> bool:
        return self._orden_svc.asignar_tecnico(id_orden, id_tecnico)

    def iniciar_ejecucion(self, id_orden: str, fecha_inicio: str) -> bool:
        return self._orden_svc.iniciar_ejecucion(id_orden, fecha_inicio)

    def finalizar_orden(
        self, id_orden: str, fecha_cierre: str, costo_real: float
    ) -> bool:
        return self._orden_svc.finalizar_orden(id_orden, fecha_cierre, costo_real)

    def cancelar_orden(self, id_orden: str) -> bool:
        return self._orden_svc.cancelar_orden(id_orden)

    def listar_ordenes_por_filtro(self, filtros: dict) -> list:
        return self._orden_svc.listar_ordenes_por_filtro(filtros)