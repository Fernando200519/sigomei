import os
import Pyro5.api
from pathlib import Path

from dotenv import load_dotenv

_ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=_ENV_PATH)

_HOST      = os.getenv("SERVER_HOST")
_PORT      = int(os.getenv("SERVER_PORT"))
_OBJECT_ID = os.getenv("SERVER_OBJECT_ID")

class SigomeiProxy:

    def __init__(self, host: str = _HOST, port: int = _PORT):
        uri = f"PYRO:{_OBJECT_ID}@{host}:{port}"
        self._remote = Pyro5.api.Proxy(uri)

    # Autenticación
    
    def login(self, username: str, password: str) -> str:
        return self._remote.login(username, password)

    def logout(self, token: str) -> bool:
        return self._remote.logout(token)

    # Equipos
    
    def alta_equipo(
        self,
        id_equipo, nombre, tipo, marca, modelo,
        numero_serie, ubicacion_planta, fecha_instalacion,
        estado_operativo, criticidad,
    ) -> bool:
        return self._remote.alta_equipo(
            id_equipo, nombre, tipo, marca, modelo,
            numero_serie, ubicacion_planta, fecha_instalacion,
            estado_operativo, criticidad,
        )

    def consultar_equipo(self, id_equipo: str) -> dict:
        return self._remote.consultar_equipo(id_equipo)

    def modificar_equipo(self, id_equipo: str, datos_actualizados: dict) -> bool:
        return self._remote.modificar_equipo(id_equipo, datos_actualizados)

    def baja_equipo(self, id_equipo: str) -> bool:
        return self._remote.baja_equipo(id_equipo)

    # Técnicos
    
    def alta_tecnico(
        self,
        id_tecnico, nombre_completo, rfc, telefono, correo,
        especialidad, nivel_certificacion, fecha_ingreso, estatus,
    ) -> bool:
        return self._remote.alta_tecnico(
            id_tecnico, nombre_completo, rfc, telefono, correo,
            especialidad, nivel_certificacion, fecha_ingreso, estatus,
        )

    def consultar_tecnico(self, id_tecnico: str) -> dict:
        return self._remote.consultar_tecnico(id_tecnico)

    def modificar_tecnico(self, id_tecnico: str, datos_actualizados: dict) -> bool:
        return self._remote.modificar_tecnico(id_tecnico, datos_actualizados)

    def baja_tecnico(self, id_tecnico: str) -> bool:
        return self._remote.baja_tecnico(id_tecnico)

    # Órdenes de Mantenimiento
    
    def crear_orden(
        self,
        id_orden, id_equipo, tipo_mantenimiento,
        fecha_programada, descripcion_trabajo, costo_estimado,
    ) -> bool:
        return self._remote.crear_orden(
            id_orden, id_equipo, tipo_mantenimiento,
            fecha_programada, descripcion_trabajo, costo_estimado,
        )

    def consultar_orden(self, id_orden: str) -> dict:
        return self._remote.consultar_orden(id_orden)

    def asignar_tecnico(self, id_orden: str, id_tecnico: str) -> bool:
        return self._remote.asignar_tecnico(id_orden, id_tecnico)

    def iniciar_ejecucion(self, id_orden: str, fecha_inicio: str) -> bool:
        return self._remote.iniciar_ejecucion(id_orden, fecha_inicio)

    def finalizar_orden(
        self, id_orden: str, fecha_cierre: str, costo_real: float
    ) -> bool:
        return self._remote.finalizar_orden(id_orden, fecha_cierre, costo_real)

    def cancelar_orden(self, id_orden: str) -> bool:
        return self._remote.cancelar_orden(id_orden)

    def listar_ordenes_por_filtro(self, filtros: dict) -> list:
        return self._remote.listar_ordenes_por_filtro(filtros)