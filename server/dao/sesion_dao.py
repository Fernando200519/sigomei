from server.dao.db_connection import get_connection


class SesionDAO:

    def crear_sesion(
        self,
        id_usuario_int: int
    ) -> int:

        sql = """
            INSERT INTO sesiones (
                id_usuario_int
            )
            VALUES (%s)
            RETURNING id_sesion
        """

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    sql,
                    (id_usuario_int,)
                )

                row = cur.fetchone()

        return row["id_sesion"]

    def cerrar_sesion(
        self,
        id_sesion: int
    ) -> bool:

        sql = """
            UPDATE sesiones
            SET fecha_hora_fin = NOW()
            WHERE id_sesion = %s
        """

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    sql,
                    (id_sesion,)
                )

        return True