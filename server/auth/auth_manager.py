import uuid

from werkzeug.security import check_password_hash

from server.dao.sesion_dao import SesionDAO
from server.dao.usuario_dao import UsuarioDAO
from server.exceptions.exceptions import AutenticacionError, ReglaNegocioError


class AuthManager:

    ROL_ADMINISTRADOR = 1
    ROL_COORDINADOR = 2
    ROL_SUPERVISOR = 3
    ROL_TECNICO = 4

    ROLES_SUPERVISION = {
        ROL_ADMINISTRADOR,
        ROL_COORDINADOR,
        ROL_SUPERVISOR
    }

    def __init__(self):
        self._sesiones = {}
        self._usuario_dao = UsuarioDAO()
        self._sesion_dao = SesionDAO()
        

    def validar_roles(
        self,
        token: str,
        roles_permitidos: set[int]
    ) -> dict:

        sesion = self.verificar(token)

        if sesion["id_rol"] not in roles_permitidos:
            raise ReglaNegocioError(
                "No tiene permisos para realizar esta acción."
            )

        return sesion

    def validar_supervision(
        self,
        token: str
    ) -> dict:

        return self.validar_roles(
            token,
            self.ROLES_SUPERVISION
        )

    def login(self, correo: str, password: str) -> str:
        """
        Valida credenciales, crea sesión persistente
        y devuelve token temporal de autenticación.
        """

        usuario = self._usuario_dao.buscar_por_correo(correo)

        if not usuario:
            raise AutenticacionError(
                "Credenciales incorrectas."
            )

        if usuario["estado"] != "Activo":
            raise AutenticacionError(
                "El usuario no tiene acceso al sistema."
            )

        if not check_password_hash(
            usuario["hash_contrasena"],
            password
        ):
            raise AutenticacionError(
                "Credenciales incorrectas."
            )

        token = str(uuid.uuid4())

        id_sesion = self._sesion_dao.crear_sesion(
            usuario["id_usuario_int"]
        )

        self._sesiones[token] = {
            "token": token,
            "id_usuario_int": usuario["id_usuario_int"],
            "id_usuario": usuario["id_usuario"],
            "nombre_completo": usuario["nombre_completo"],
            "correo": usuario["correo"],
            "id_rol": usuario["id_rol"],
            "estado": usuario["estado"],
            "id_sesion": id_sesion,
        }

        return token

    def verificar(self, token: str) -> dict:
        """
        Verifica que el token sea válido
        y devuelve el contexto del usuario autenticado.
        """

        sesion = self._sesiones.get(token)

        if not sesion:
            raise AutenticacionError(
                "Sesión inválida o expirada."
            )

        return sesion

    def logout(self, token: str) -> bool:
        """
        Cierra la sesión persistente
        y elimina el token en memoria.
        """

        sesion = self._sesiones.get(token)

        if not sesion:
            return False

        self._sesion_dao.cerrar_sesion(
            sesion["id_sesion"]
        )

        del self._sesiones[token]

        return True

    def tiene_rol(
        self,
        token: str,
        roles_permitidos: list[int]
    ) -> bool:
        """
        Verifica si el usuario autenticado
        tiene alguno de los roles permitidos.
        """

        sesion = self.verificar(token)

        return sesion["id_rol"] in roles_permitidos