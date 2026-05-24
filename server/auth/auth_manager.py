import uuid
from server.exceptions.exceptions import AutenticacionError

_USUARIOS = {
    "admin": "admin123",
    "tecnico": "tec456",
    "supervisor@sigomei.mx": "Test1234"
}


class AuthManager:

    def __init__(self):
        self._sesiones: dict[str, str] = {}

    def login(self, username: str, password: str) -> str:
        """Valida credenciales y devuelve un token de sesión."""
        if _USUARIOS.get(username) != password:
            raise AutenticacionError("Credenciales incorrectas.")
        token = str(uuid.uuid4())
        self._sesiones[token] = username
        return token

    def logout(self, token: str) -> bool:
        """Invalida un token de sesión."""
        return self._sesiones.pop(token, None) is not None

    def verificar(self, token: str) -> str:
        """Devuelve el username asociado al token o lanza AutenticacionError."""
        if token not in self._sesiones:
            raise AutenticacionError("Sesión inválida o expirada.")
        return self._sesiones[token]