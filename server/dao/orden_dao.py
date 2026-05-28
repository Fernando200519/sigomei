import datetime
from server.dao.db_connection import get_connection


class OrdenDAO:

    def insertar(self, datos: dict) -> bool:
        """Inserta la orden y registra su estado inicial 'Programada' en el historial."""
        sql_orden = """
            INSERT INTO ordenes_mantenimiento
                (id_orden, id_equipo_int, tipo_mantenimiento, fecha_programada,
                 descripcion_trabajo, costo_estimado, id_tecnico_int)
            VALUES
                (%(id_orden)s, %(id_equipo_int)s, %(tipo_mantenimiento)s,
                 %(fecha_programada)s, %(descripcion_trabajo)s,
                 %(costo_estimado)s, %(id_tecnico_int)s)
            RETURNING id_orden_int;
        """
        
        sql_historial = """
            INSERT INTO historial_estados_orden (id_orden_int, id_estado_orden, fecha_hora_inicio)
            VALUES (%s, (SELECT id_estado_orden FROM estados_orden WHERE nombre = 'Programada'), NOW());
        """
        
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql_orden, datos)
                row = cur.fetchone()
                id_orden_int = dict(row)["id_orden_int"] if row else None
                
                if id_orden_int:
                    cur.execute(sql_historial, (id_orden_int,))
                    
        return True

    def obtener_id_orden_int(self, id_orden: str) -> int | None:
        """Obtiene el ID interno (entero) a partir del ID de negocio (varchar)."""
        sql = "SELECT id_orden_int FROM ordenes_mantenimiento WHERE id_orden = %s"
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (id_orden,))
                row = cur.fetchone()
        return dict(row)["id_orden_int"] if row else None

    def buscar_por_id(self, id_orden_int: int) -> dict | None:
        """Busca una orden por ID y obtiene su estado actual desde el historial activo."""
        sql = """
            SELECT o.*, 
                eo.nombre AS estado_orden,
                e.id_equipo,
                t.id_tecnico
            FROM ordenes_mantenimiento o
            LEFT JOIN historial_estados_orden heo 
                ON o.id_orden_int = heo.id_orden_int AND heo.fecha_hora_fin IS NULL
            LEFT JOIN estados_orden eo 
                ON heo.id_estado_orden = eo.id_estado_orden
            LEFT JOIN equipos e
                ON e.id_equipo_int = o.id_equipo_int
            LEFT JOIN tecnicos t
                ON t.id_tecnico_int = o.id_tecnico_int
            WHERE o.id_orden_int = %s
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (id_orden_int,))
                row = cur.fetchone()
        return dict(row) if row else None

    def listar_por_filtros(self, filtros: dict) -> list:
        """Busca órdenes aplicando filtros dinámicos evaluando el estado actual activo."""
        campos_validos = {
            "estado_orden":        ("eo.nombre = %(estado_orden)s",),
            "id_equipo_int":       ("o.id_equipo_int = %(id_equipo_int)s",),
            "id_tecnico_int":      ("o.id_tecnico_int = %(id_tecnico_int)s",),
            "tipo_mantenimiento":  ("o.tipo_mantenimiento = %(tipo_mantenimiento)s",),
            "fecha_desde":         ("o.fecha_programada >= %(fecha_desde)s",),
            "fecha_hasta":         ("o.fecha_programada <= %(fecha_hasta)s",),
            "costo_estimado_min":  ("o.costo_estimado >= %(costo_estimado_min)s",),
            "costo_estimado_max":  ("o.costo_estimado <= %(costo_estimado_max)s",),
        }

        condiciones = []
        parametros = {}

        for campo, valor in filtros.items():
            if campo in campos_validos and valor is not None:
                condiciones.append(campos_validos[campo][0])
                parametros[campo] = valor

        where = ("WHERE " + " AND ".join(condiciones)) if condiciones else ""
        
        sql = f"""
            SELECT o.*, 
                eo.nombre AS estado_orden,
                e.id_equipo,
                t.id_tecnico
            FROM ordenes_mantenimiento o
            LEFT JOIN historial_estados_orden heo 
                ON o.id_orden_int = heo.id_orden_int AND heo.fecha_hora_fin IS NULL
            LEFT JOIN estados_orden eo 
                ON heo.id_estado_orden = eo.id_estado_orden
            LEFT JOIN equipos e
                ON e.id_equipo_int = o.id_equipo_int
            LEFT JOIN tecnicos t
                ON t.id_tecnico_int = o.id_tecnico_int
            {where} 
            ORDER BY o.fecha_programada DESC;
        """

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, parametros)
                return [dict(r) for r in cur.fetchall()]

    def actualizar_estado(self, id_orden_int: int, nuevo_estado: str) -> bool:
        """Cierra el estado activo anterior y abre el nuevo en la tabla de historial."""
        sql_cerrar_actual = """
            UPDATE historial_estados_orden 
            SET fecha_hora_fin = NOW() 
            WHERE id_orden_int = %s AND fecha_hora_fin IS NULL;
        """
        
        sql_insertar_nuevo = """
            INSERT INTO historial_estados_orden (id_orden_int, id_estado_orden, fecha_hora_inicio)
            VALUES (%s, (SELECT id_estado_orden FROM estados_orden WHERE nombre = %s), NOW());
        """
        
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql_cerrar_actual, (id_orden_int,))
                cur.execute(sql_insertar_nuevo, (id_orden_int, nuevo_estado))
                
        return True

    def asignar_tecnico(self, id_orden_int: int, id_tecnico_int: int) -> bool:
        sql = "UPDATE ordenes_mantenimiento SET id_tecnico_int = %s WHERE id_orden_int = %s"
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (id_tecnico_int, id_orden_int))
        return True

    def actualizar_inicio(self, id_orden_int: int, fecha_inicio: str) -> bool:
        sql = "UPDATE ordenes_mantenimiento SET fecha_inicio = %s WHERE id_orden_int = %s"
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (fecha_inicio, id_orden_int))
        return True

    def actualizar_cierre(self, id_orden_int: int, fecha_cierre: str,
                          costo_real: float) -> bool:
        sql = """
            UPDATE ordenes_mantenimiento
            SET fecha_cierre = %s, costo_real = %s
            WHERE id_orden_int = %s
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (fecha_cierre, costo_real, id_orden_int))
        return True