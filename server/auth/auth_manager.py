class AuthManager:

    def autenticar(self, username: str, password: str) -> str:
        raise NotImplementedError

    def cerrar_sesion(self, token: str) -> bool:
        raise NotImplementedError

    def validar_sesion(self, token: str) -> bool:
        raise NotImplementedError


class SessionHandler:

    def crear_token(self, user_id: str) -> str:
        raise NotImplementedError

    def invalidar_token(self, token: str) -> None:
        raise NotImplementedError

    def obtener_usuario(self, token: str) -> str | None:
        raise NotImplementedError