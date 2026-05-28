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
    
    def login(self, correo: str, password: str) -> str:
        return self._remote.login(correo, password)

    def logout(self, token: str) -> bool:
        return self._remote.logout(token)
    
    # Equipos
    
    def alta_equipo(
        self, token,
        id_equipo, nombre, tipo, marca, modelo,
        numero_serie, ubicacion_planta, fecha_instalacion,
        estado_operativo, criticidad,
    ) -> bool:
        return self._remote.alta_equipo(
            token, id_equipo, nombre, tipo, marca, modelo,
            numero_serie, ubicacion_planta, fecha_instalacion,
            estado_operativo, criticidad,
        )

    def consultar_equipo(self, token, id_equipo: str) -> dict:
        return self._remote.consultar_equipo(token, id_equipo)

    def modificar_equipo(self, token, id_equipo: str, datos_actualizados: dict) -> bool:
        return self._remote.modificar_equipo(token, id_equipo, datos_actualizados)

    def baja_equipo(self, token, id_equipo: str) -> bool:
        return self._remote.baja_equipo(token, id_equipo)

    def listar_equipos(self, token) -> list:
        return self._remote.listar_equipos(token)
    
    # Técnicos
    
    def alta_tecnico(
        self, token,
        id_tecnico, nombre_completo, rfc, telefono, correo,
        especialidad, nivel_certificacion, fecha_ingreso, estatus,
    ) -> bool:
        return self._remote.alta_tecnico(
            token, id_tecnico, nombre_completo, rfc, telefono, correo,
            especialidad, nivel_certificacion, fecha_ingreso, estatus,
        )

    def consultar_tecnico(self, token, id_tecnico: str) -> dict:
        return self._remote.consultar_tecnico(token, id_tecnico)

    def modificar_tecnico(self, token, id_tecnico: str, datos_actualizados: dict) -> bool:
        return self._remote.modificar_tecnico(token, id_tecnico, datos_actualizados)

    def baja_tecnico(self, token, id_tecnico: str) -> bool:
        return self._remote.baja_tecnico(token, id_tecnico)

    def listar_tecnicos(self, token) -> list:
        return self._remote.listar_tecnicos(token)

    def listar_tecnicos_por_filtro(self, token, filtros: dict) -> list:
        return self._remote.listar_tecnicos_por_filtro(token, filtros)

    # Órdenes de Mantenimiento
    
    def crear_orden(
        self, token,
        id_orden, id_equipo, tipo_mantenimiento,
        fecha_programada, descripcion_trabajo, costo_estimado,
    ) -> bool:
        return self._remote.crear_orden(
            token, id_orden, id_equipo, tipo_mantenimiento,
            fecha_programada, descripcion_trabajo, costo_estimado,
        )

    def consultar_orden(self, token, id_orden: str) -> dict:
        return self._remote.consultar_orden(token, id_orden)

    def asignar_tecnico(self, token, id_orden: str, id_tecnico: str) -> bool:
        return self._remote.asignar_tecnico(token, id_orden, id_tecnico)

    def solicitar_cierre(self, token: str, id_orden: str) -> bool:
        return self._remote.solicitar_cierre(token, id_orden)

    def iniciar_ejecucion(self, token, id_orden: str, fecha_inicio: str) -> bool:
        return self._remote.iniciar_ejecucion(token, id_orden, fecha_inicio)

    def finalizar_orden(
        self, token, id_orden: str, fecha_cierre: str, costo_real: float
    ) -> bool:
        return self._remote.finalizar_orden(token, id_orden, fecha_cierre, costo_real)

    def cancelar_orden(self, token, id_orden: str) -> bool:
        return self._remote.cancelar_orden(token, id_orden)

    def listar_ordenes_por_filtro(self, token, filtros: dict) -> list:
        return self._remote.listar_ordenes_por_filtro(token, filtros)

    # Usuarios
    
    def alta_usuario(
        self, token, nombre_completo, rfc, telefono, correo,
        contrasena, id_rol, id_usuario, estado="Activo"
    ) -> bool:
        return self._remote.alta_usuario(
            token, nombre_completo, rfc, telefono, correo,
            contrasena, id_rol, id_usuario, estado
        )

    def consultar_usuario(self, token, id_usuario: str) -> dict:
        return self._remote.consultar_usuario(token, id_usuario)

    def modificar_usuario(self, token, id_usuario: str, datos_actualizados: dict) -> bool:
        return self._remote.modificar_usuario(token, id_usuario, datos_actualizados)

    def baja_usuario(self, token, id_usuario: str) -> bool:
        return self._remote.baja_usuario(token, id_usuario)

    def listar_usuarios(self, token) -> list:
        return self._remote.listar_usuarios(token)