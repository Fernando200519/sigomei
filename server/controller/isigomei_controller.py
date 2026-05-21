import Pyro5.api

from server.auth.auth_manager import AuthManager
from server.service.equipo_service import EquipoService
from server.service.tecnico_service import TecnicoService
from server.service.orden_service import OrdenService


@Pyro5.api.expose
class ISigomeiController:
    
    def __init__(self):
        self._auth = AuthManager()
        self._equipo_svc = EquipoService()
        self._tecnico_svc = TecnicoService()
        self._orden_svc = OrdenService()

    # ------------------------------------------------------------------
    # Autenticación
    # ------------------------------------------------------------------

    def login(self, username: str, password: str) -> str:
        raise NotImplementedError

    def logout(self, token: str) -> bool:
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Módulo 1: Gestión de Equipos
    # ------------------------------------------------------------------

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
        raise NotImplementedError

    def consultar_equipo(self, id_equipo: str) -> dict | None:
        raise NotImplementedError

    def modificar_equipo(self, id_equipo: str, datos_actualizados: dict) -> bool:
        raise NotImplementedError

    def baja_equipo(self, id_equipo: str) -> bool:
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Módulo 2: Gestión de Técnicos
    # ------------------------------------------------------------------

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
        raise NotImplementedError

    def consultar_tecnico(self, id_tecnico: str) -> dict | None:
        raise NotImplementedError

    def modificar_tecnico(self, id_tecnico: str, datos_actualizados: dict) -> bool:
        raise NotImplementedError

    def baja_tecnico(self, id_tecnico: str) -> bool:
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Módulo 3: Órdenes de Mantenimiento
    # ------------------------------------------------------------------

    def crear_orden(
        self,
        id_orden: str,
        id_equipo: str,
        tipo_mantenimiento: str,
        fecha_programada: str,
        descripcion_trabajo: str,
        costo_estimado: float,
    ) -> bool:
        raise NotImplementedError

    def consultar_orden(self, id_orden: str) -> dict:
        raise NotImplementedError

    def asignar_tecnico(self, id_orden: str, id_tecnico: str) -> bool:
        raise NotImplementedError

    def iniciar_ejecucion(self, id_orden: str, fecha_inicio: str) -> bool:
        raise NotImplementedError

    def finalizar_orden(self, id_orden: str, fecha_cierre: str, costo_real: float) -> bool:
        raise NotImplementedError

    def cancelar_orden(self, id_orden: str) -> bool:
        raise NotImplementedError

    def listar_ordenes_por_filtro(self, filtros: dict) -> list:
        raise NotImplementedError