from server.dao.db_connection import get_connection


class OrdenDAO:

    def insertar(self, datos: dict) -> bool:
        sql = """
            INSERT INTO ordenes_mantenimiento
                (id_orden, id_equipo, tipo_mantenimiento, fecha_programada,
                 descripcion_trabajo, costo_estimado, estado_orden, id_tecnico)
            VALUES
                (%(id_orden)s, %(id_equipo)s, %(tipo_mantenimiento)s,
                 %(fecha_programada)s, %(descripcion_trabajo)s,
                 %(costo_estimado)s, %(estado_orden)s, %(id_tecnico)s)
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, datos)
        return True

    def buscar_por_id(self, id_orden: str) -> dict | None:
        sql = "SELECT * FROM ordenes_mantenimiento WHERE id_orden = %s"
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (id_orden,))
                row = cur.fetchone()
        return dict(row) if row else None

    def listar_por_filtros(self, filtros: dict) -> list:
        condiciones = [f"{k} = %({k})s" for k in filtros]
        where = ("WHERE " + " AND ".join(condiciones)) if condiciones else ""
        sql = f"SELECT * FROM ordenes_mantenimiento {where}"
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, filtros)
                return [dict(r) for r in cur.fetchall()]

    def actualizar_estado(self, id_orden: str, nuevo_estado: str) -> bool:
        sql = "UPDATE ordenes_mantenimiento SET estado_orden = %s WHERE id_orden = %s"
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (nuevo_estado, id_orden))
        return True

    def asignar_tecnico(self, id_orden: str, id_tecnico: str) -> bool:
        sql = "UPDATE ordenes_mantenimiento SET id_tecnico = %s WHERE id_orden = %s"
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (id_tecnico, id_orden))
        return True

    def actualizar_inicio(self, id_orden: str, fecha_inicio: str) -> bool:
        sql = "UPDATE ordenes_mantenimiento SET fecha_inicio = %s WHERE id_orden = %s"
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (fecha_inicio, id_orden))
        return True

    def actualizar_cierre(self, id_orden: str, fecha_cierre: str,
                          costo_real: float) -> bool:
        sql = """
            UPDATE ordenes_mantenimiento
            SET fecha_cierre = %s, costo_real = %s
            WHERE id_orden = %s
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (fecha_cierre, costo_real, id_orden))
        return True