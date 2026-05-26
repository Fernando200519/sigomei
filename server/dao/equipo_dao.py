from server.dao.db_connection import get_connection
import psycopg2

class EquipoDAO:

    def insertar(self, datos: dict) -> bool:
        sql = """
            INSERT INTO equipos
                (id_equipo, nombre, tipo, marca, modelo, numero_serie,
                 ubicacion_planta, fecha_instalacion, estado_operativo, criticidad)
            VALUES
                (%(id_equipo)s, %(nombre)s, %(tipo)s, %(marca)s, %(modelo)s,
                 %(numero_serie)s, %(ubicacion_planta)s, %(fecha_instalacion)s,
                 %(estado_operativo)s, %(criticidad)s)
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                try: 
                    cur.execute(sql, datos)
                except psycopg2.Error as e:
                    print("PG ERROR:", e.args)
                    raise
            conn.commit()
        return True

    def buscar_por_id(self, id_equipo: str) -> dict | None:
        sql = "SELECT * FROM equipos WHERE id_equipo = %s"
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (id_equipo,))
                row = cur.fetchone()
        return dict(row) if row else None
    
    def buscar_por_numero_serie(self, num_serie: str) -> dict | None:
        sql = "SELECT * FROM equipos WHERE numero_serie = %s"
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (num_serie,))
                row = cur.fetchone()
        return dict(row) if row else None

    def actualizar(self, id_equipo: str, datos: dict) -> bool:
        if not datos:
            return False
        campos = ", ".join(f"{k} = %({k})s" for k in datos)
        sql = f"UPDATE equipos SET {campos} WHERE id_equipo = %(id_equipo)s"
        datos["id_equipo"] = id_equipo
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, datos)
            conn.commit()
        return True

    def eliminar(self, id_equipo: str) -> bool:
        sql = "DELETE FROM equipos WHERE id_equipo = %s"
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (id_equipo,))
            conn.commit()
        return True

    def tiene_ordenes_vinculadas(self, id_equipo: str) -> bool:
        sql = "SELECT 1 FROM ordenes_mantenimiento WHERE id_equipo = %s LIMIT 1"
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (id_equipo,))
                return cur.fetchone() is not None
    
    def listar_todos(self) -> list:
        """Consulta la base de datos y devuelve todos los equipos registrados."""
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id_equipo, nombre, tipo, ubicacion_planta, estado_operativo, criticidad 
                    FROM equipos;
                """)
                
                registros = cur.fetchall()
                
                return [dict(fila) for fila in registros]