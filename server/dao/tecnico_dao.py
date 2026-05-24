from server.dao.db_connection import get_connection
import psycopg2 

class TecnicoDAO:

    def insertar(self, datos: dict) -> bool:
        sql = """
            INSERT INTO tecnicos
                (id_tecnico, nombre_completo, rfc, telefono, correo,
                especialidad, nivel_certificacion, fecha_ingreso, estatus)
            VALUES
                (%(id_tecnico)s, %(nombre_completo)s, %(rfc)s,
                %(telefono)s, %(correo)s, %(especialidad)s,
                %(nivel_certificacion)s, %(fecha_ingreso)s,
                %(estatus)s)
        """

        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql, datos)

                conn.commit()

            return True

        except psycopg2.Error as e:
            raise Exception(e)
        
    def buscar_por_id(self, id_tecnico: str) -> dict | None:
        sql = "SELECT * FROM tecnicos WHERE id_tecnico = %s"
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (id_tecnico,))
                row = cur.fetchone()
        return dict(row) if row else None

    def actualizar(self, id_tecnico: str, datos: dict) -> bool:
        if not datos:
            return False
        campos = ", ".join(f"{k} = %({k})s" for k in datos)
        sql = f"UPDATE tecnicos SET {campos} WHERE id_tecnico = %(id_tecnico)s"
        datos["id_tecnico"] = id_tecnico
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, datos)
            conn.commit()
        return True

    def eliminar(self, id_tecnico: str) -> bool:
        sql = "DELETE FROM tecnicos WHERE id_tecnico = %s"
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (id_tecnico,))
            conn.commit()
        return True

    def tiene_ordenes_activas(self, id_tecnico: str) -> bool:
        sql = """
            SELECT 1 FROM ordenes_mantenimiento
            WHERE id_tecnico = %s
              AND estado_orden NOT IN ('Finalizada', 'Cancelada')
            LIMIT 1
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (id_tecnico,))
                return cur.fetchone() is not None

    def existe_rfc(self, rfc: str) -> bool:
        sql = "SELECT 1 FROM tecnicos WHERE rfc = %s LIMIT 1"
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (rfc,))
                return cur.fetchone() is not None