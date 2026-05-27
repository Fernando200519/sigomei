from server.dao.db_connection import get_connection


class UsuarioDAO:

    def insertar(self, datos: dict) -> int:
        sql = """
            INSERT INTO usuarios (
                id_usuario,
                nombre_completo,
                rfc,
                telefono,
                correo,
                estado,
                hash_contrasena,
                id_rol
            )
            VALUES (
                %(id_usuario)s, 
                %(nombre_completo)s,
                %(rfc)s,
                %(telefono)s,
                %(correo)s,
                %(estado)s,
                %(hash_contrasena)s,
                %(id_rol)s
            )
            RETURNING id_usuario_int
        """

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, datos)
                return cur.fetchone()["id_usuario_int"]

    def buscar_por_id(
        self,
        id_usuario: str
    ) -> dict:

        sql = """
            SELECT
                u.id_usuario,
                u.nombre_completo,
                u.rfc,
                u.telefono,
                u.correo,
                u.estado,
                u.id_rol,
                r.nombre AS rol
            FROM usuarios u
            JOIN roles r
                ON r.id_rol = u.id_rol
            WHERE u.id_usuario = %s
        """

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (id_usuario,))
                return cur.fetchone()

    def obtener_id_usuario_int(
        self,
        id_usuario: str
    ) -> int | None:

        sql = """
            SELECT id_usuario_int
            FROM usuarios
            WHERE id_usuario = %s
        """

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (id_usuario,))
                row = cur.fetchone()
                return row["id_usuario_int"] if row else None

    def existe_rfc(
        self,
        rfc: str
    ) -> bool:

        sql = """
            SELECT 1
            FROM usuarios
            WHERE rfc = %s
        """

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (rfc,))
                return cur.fetchone() is not None

    def existe_correo(
        self,
        correo: str
    ) -> bool:

        sql = """
            SELECT 1
            FROM usuarios
            WHERE correo = %s
        """

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (correo,))
                return cur.fetchone() is not None

    def actualizar(
        self,
        id_usuario: str,
        datos_actualizados: dict
    ) -> bool:

        campos = []
        valores = []

        for campo, valor in datos_actualizados.items():
            campos.append(
                f"{campo} = %s"
            )
            valores.append(valor)

        valores.append(id_usuario)

        sql = f"""
            UPDATE usuarios
            SET {', '.join(campos)}
            WHERE id_usuario = %s
        """

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, valores)

        return True

    def listar_todos(
        self
    ) -> list:

        sql = """
            SELECT
                u.id_usuario,
                u.nombre_completo,
                u.rfc,
                u.telefono,
                u.correo,
                u.estado,
                r.nombre AS rol
            FROM usuarios u
            JOIN roles r
                ON r.id_rol = u.id_rol
            ORDER BY u.nombre_completo
        """

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                return cur.fetchall()