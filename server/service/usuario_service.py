from server.dao.usuario_dao import UsuarioDAO
from server.exceptions.exceptions import (
    EntidadDuplicadaError,
    EntidadNoEncontradaError,
    ReglaNegocioError,
)

ESTADOS_VALIDOS = {"Activo", "Inactivo", "Suspendido"}

ROLES_VALIDOS = {
    1,  # Administrador
    2,  # Coordinador
    3,  # Supervisor
    4,  # Técnico
}


class UsuarioService:

    def __init__(self):
        self._dao = UsuarioDAO()

    def alta_usuario(
        self,
        nombre_completo: str,
        rfc: str,
        telefono: str,
        correo: str,
        hash_contrasena: str,
        id_rol: int,
        estado: str = "Activo",
    ) -> bool:

        if estado not in ESTADOS_VALIDOS:
            raise ReglaNegocioError(
                f"Estado inválido: '{estado}'"
            )

        if self._dao.existe_rfc(rfc):
            raise EntidadDuplicadaError(
                f"Ya existe un usuario con RFC '{rfc}'"
            )
        
        if id_rol not in ROLES_VALIDOS:
            raise ReglaNegocioError(
                f"Rol inválido: '{id_rol}'"
            )


        if self._dao.existe_correo(correo):
            raise EntidadDuplicadaError(
                f"Ya existe un usuario con correo '{correo}'"
            )

        datos = {
            "nombre_completo": nombre_completo,
            "rfc": rfc,
            "telefono": telefono,
            "correo": correo,
            "hash_contrasena": hash_contrasena,
            "id_rol": id_rol,
            "estado": estado,
        }

        return self._dao.insertar(datos)

    def consultar_usuario(
        self,
        id_usuario: str
    ) -> dict:

        usuario = self._dao.buscar_por_id(
            id_usuario
        )

        if not usuario:
            raise EntidadNoEncontradaError(
                f"Usuario '{id_usuario}' no encontrado"
            )

        return usuario

    def modificar_usuario(
        self,
        id_usuario: str,
        datos_actualizados: dict
    ) -> bool:

        if not self._dao.buscar_por_id(
            id_usuario
        ):
            raise EntidadNoEncontradaError(
                f"Usuario '{id_usuario}' no encontrado"
            )

        if (
            "estado" in datos_actualizados
            and datos_actualizados["estado"]
            not in ESTADOS_VALIDOS
        ):
            raise ReglaNegocioError(
                f"Estado inválido: "
                f"'{datos_actualizados['estado']}'"
            )

        if (
            "id_rol" in datos_actualizados
            and datos_actualizados["id_rol"]
            not in ROLES_VALIDOS
        ):
            raise ReglaNegocioError(
                f"Rol inválido: "
                f"'{datos_actualizados['id_rol']}'"
            )

        return self._dao.actualizar(
            id_usuario,
            datos_actualizados
        )

    def baja_usuario(
        self,
        id_usuario: str
    ) -> bool:

        if not self._dao.buscar_por_id(
            id_usuario
        ):
            raise EntidadNoEncontradaError(
                f"Usuario '{id_usuario}' no encontrado"
            )

        return self._dao.actualizar(
            id_usuario,
            {"estado": "Inactivo"}
        )

    def listar_usuarios(self) -> list:
        return self._dao.listar_todos()